import os
import re
import time
import logging
from collections import defaultdict
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Rate limiting ─────────────────────────────────────────────────────────────
RATE_LIMIT  = 25      # max questions per IP
RATE_WINDOW = 86400    # sliding window: 24 hours in seconds

_rate_store: dict[str, list[float]] = defaultdict(list)


def _get_client_ip(request: Request) -> str:
    """Extract real client IP from X-Forwarded-For.

    Uses the rightmost (last) value to prevent spoofing — Azure Container Apps
    appends the verified client IP last in the chain.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"


_sweep_counter = 0
_SWEEP_INTERVAL = 200  # evict stale IPs every N requests


def _check_rate_limit(ip: str) -> tuple[bool, int]:
    """
    Sliding window check. Returns (allowed, remaining).
    Mutates _rate_store: appends timestamp if allowed, prunes stale entries.
    Every _SWEEP_INTERVAL calls, evicts IPs with no recent activity to prevent
    unbounded memory growth from unique visitor IPs accumulating over time.
    """
    global _sweep_counter
    now = time.time()
    cutoff = now - RATE_WINDOW

    # Periodic full sweep to evict IPs whose entire window has expired
    _sweep_counter += 1
    if _sweep_counter % _SWEEP_INTERVAL == 0:
        stale = [k for k, v in list(_rate_store.items()) if not any(t > cutoff for t in v)]
        for k in stale:
            del _rate_store[k]

    # Prune requests outside the window for this IP
    _rate_store[ip] = [t for t in _rate_store[ip] if t > cutoff]
    if len(_rate_store[ip]) >= RATE_LIMIT:
        return False, 0
    _rate_store[ip].append(now)
    return True, RATE_LIMIT - len(_rate_store[ip])

# ── Module-level clients (initialised once on startup, reused across requests) ─
_base_endpoint = os.environ.get("AZURE_INFERENCE_ENDPOINT", "")

_search_client = SearchClient(
    endpoint=os.environ.get("AZURE_SEARCH_ENDPOINT", ""),
    index_name=os.environ.get("AZURE_SEARCH_INDEX_NAME", ""),
    credential=AzureKeyCredential(os.environ.get("AZURE_SEARCH_KEY", "")),
)

_inference_client = AzureOpenAI(
    azure_endpoint=_base_endpoint,
    api_key=os.environ.get("AZURE_INFERENCE_KEY", ""),
    api_version="2025-01-01-preview",
)

SYSTEM_PROMPT = """You are a talent advisor briefing a hiring manager on Todd DeBlieck, a candidate for senior healthcare IT and AI transformation leadership roles.

RULES — follow strictly:
1. Answer ONLY using facts that appear in the CONTEXT blocks provided. Do NOT invent, infer, or add any detail not stated there.
2. If the context does not contain the answer, say exactly: "I don't have that information in Todd's resume."
3. Lead with leadership impact and outcomes — not a list of duties.
4. Be concise, confident, and direct — like a recruiter champion who knows this candidate well.
5. For broad questions (who is, tell me about, overview, background), synthesize a tight 3-4 sentence executive summary: current role → core expertise → key differentiator.
6. For specific questions, answer precisely in 1-3 sentences."""

SUGGESTED_QUESTIONS = [
    "What is Todd's most recent role?",
    "What Azure services has Todd worked with?",
    "Tell me about Todd's Epic certifications.",
    "What AI tools does Todd use?",
    "Describe Todd's Cosmos Administrator experience.",
]

# ── Section priority for context ordering ────────────────────────────────────
# Lower number = higher priority in the context window sent to the model.
_SECTION_PRIORITY: dict[str, int] = {
    "Summary":            0,
    "Work Experience":    1,
    "Skills":             2,
    "Certifications":     3,
    "Projects":           4,
    "Education":          5,
    "Professional Development": 6,
    "Personal Accolades": 99,  # suppress from top — rarely recruiter-relevant
}

# Broad / overview question patterns — trigger a supplemental summary search
_BROAD_Q = re.compile(
    r"\b(tell me about|who is|describe|overview|background|introduce|summarize|summary|"
    r"about this person|about todd|what does .* do|what kind of)\b",
    re.IGNORECASE,
)


def _is_broad(question: str) -> bool:
    return bool(_BROAD_Q.search(question))


# ── CORS ─────────────────────────────────────────────────────────────────────
# Comma-separated origins injected via ALLOWED_ORIGINS env var (set in Terraform).
# Defaults to deny-all if the variable is absent or empty.
_raw_origins = os.environ.get("ALLOWED_ORIGINS", "")
_allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

# ── Startup validation ────────────────────────────────────────────────────────
_REQUIRED_VARS = [
    "AZURE_INFERENCE_ENDPOINT",
    "AZURE_INFERENCE_KEY",
    "AZURE_SEARCH_ENDPOINT",
    "AZURE_SEARCH_KEY",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    missing = [v for v in _REQUIRED_VARS if not os.environ.get(v)]
    if missing:
        logger.critical("Missing required environment variables: %s", ", ".join(missing))
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_methods=["POST", "OPTIONS", "GET"],
    allow_headers=["Content-Type"],
)


@app.post("/api/ask")
async def ask_resume(request: Request):
    # ── Rate limit check ──────────────────────────────────────────────────────
    ip = _get_client_ip(request)
    allowed, remaining = _check_rate_limit(ip)
    if not allowed:
        return JSONResponse(
            {"error": "Daily question limit reached. Come back tomorrow!", "limit": RATE_LIMIT, "remaining": 0},
            status_code=429,
        )

    try:
        body = await request.json()
        question = body.get("question", "").strip()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    if not question:
        return JSONResponse(
            {"error": "No question provided", "suggested": SUGGESTED_QUESTIONS},
            status_code=400,
        )

    if len(question) > 500:
        return JSONResponse(
            {"error": "Question too long (max 500 characters)"},
            status_code=400,
        )

    # --- Step 1: Retrieve relevant resume chunks ---
    try:
        raw_results = list(_search_client.search(search_text=question, top=7))
        # Broad questions get a supplemental pass anchored to summary/skills/experience
        if _is_broad(question):
            anchor_results = list(_search_client.search(
                search_text="Todd DeBlieck professional summary leadership background skills expertise",
                top=4,
            ))
            raw_results = raw_results + anchor_results
    except Exception:
        logger.exception("Azure Search error")
        return JSONResponse({"error": "Search unavailable. Please try again."}, status_code=500)

    # Deduplicate, build entries, sort by section priority
    seen_ids: set[str] = set()
    entries: list[tuple[int, str]] = []  # (priority, text)
    for doc in raw_results:
        doc_id = doc.get("id", "")
        if not doc_id or doc_id in seen_ids:
            continue
        content = doc.get("content", "")
        if not content:
            continue
        seen_ids.add(doc_id)
        section = doc.get("section", "")
        priority = _SECTION_PRIORITY.get(section, 50)
        entries.append((priority, f"[{section}: {doc.get('title', '')}]\n{content}"))

    entries.sort(key=lambda x: x[0])
    context_chunks = [text for _, text in entries]

    if not context_chunks:
        return JSONResponse(
            {"answer": "I couldn't find relevant information in Todd's resume for that question. Try asking about his work experience, skills, certifications, or projects.", "remaining": remaining},
            status_code=200,
        )

    context = "\n\n---\n\n".join(context_chunks[:7])  # cap at 7 chunks

    # --- Step 2: Generate answer from gpt-5-nano ---
    try:
        response = _inference_client.chat.completions.create(
            model="gpt-5-nano-1",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION: {question}\n\nAnswer using only the CONTEXT above:"},
            ],
            max_completion_tokens=420,
            temperature=0.0,
            timeout=30.0,
        )
        answer = response.choices[0].message.content
        return JSONResponse({"answer": answer, "remaining": remaining}, status_code=200)
    except Exception:
        logger.exception("Inference error")
        return JSONResponse({"error": "The AI took too long to respond. Please try again with a shorter or less open-ended question.", "remaining": remaining}, status_code=500)


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "ask-resume"}
