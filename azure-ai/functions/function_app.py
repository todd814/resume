import os
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
_raw_endpoint = os.environ.get("AZURE_INFERENCE_ENDPOINT", "")
_base_endpoint = _raw_endpoint.split("/api/projects/")[0] if "/api/projects/" in _raw_endpoint else _raw_endpoint

_search_client = SearchClient(
    endpoint=os.environ.get("AZURE_SEARCH_ENDPOINT", ""),
    index_name=os.environ.get("AZURE_SEARCH_INDEX_NAME", ""),
    credential=AzureKeyCredential(os.environ.get("AZURE_SEARCH_KEY", "")),
)

_inference_client = AzureOpenAI(
    azure_endpoint=_base_endpoint,
    api_key=os.environ.get("AZURE_INFERENCE_KEY", ""),
    api_version="2024-10-21",
)

SYSTEM_PROMPT = """You are an assistant that answers questions about Todd DeBlieck's resume.

RULES — follow them strictly:
1. Answer ONLY using facts that appear verbatim in the CONTEXT blocks provided by the user.
2. Do NOT add, infer, or invent any detail that is not explicitly stated in the context.
3. If the context does not contain the answer, say exactly: "I don't have that information in Todd's resume."
4. Do not mention companies, titles, dates, certifications, tools, or skills unless they appear in the context.
5. Be concise and professional."""

SUGGESTED_QUESTIONS = [
    "What is Todd's most recent role?",
    "What Azure services has Todd worked with?",
    "Tell me about Todd's Epic certifications.",
    "What AI tools does Todd use?",
    "Describe Todd's Cosmos Administrator experience.",
]

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

    # --- Step 1: Retrieve relevant resume chunks (single search call) ---
    try:
        results = list(_search_client.search(search_text=question, top=7))
    except Exception:
        logger.exception("Azure Search error")
        return JSONResponse({"error": "Search unavailable. Please try again."}, status_code=500)

    # Ensure the most-recent Work Experience chunk is always present
    context_chunks = []
    seen_ids = set()
    work_chunk = None
    for doc in results:
        doc_id = doc.get("id", "")
        content = doc.get("content", "")
        section = doc.get("section", "")
        if not content:
            continue
        seen_ids.add(doc_id)
        entry = f"[{section}: {doc.get('title', '')}]\n{content}"
        if section == "Work Experience" and work_chunk is None:
            work_chunk = entry          # first Work Experience hit becomes the anchor
        else:
            context_chunks.append(entry)

    if work_chunk:
        context_chunks.insert(0, work_chunk)  # always first in context

    if not context_chunks:
        return JSONResponse(
            {"answer": "I couldn't find relevant information in Todd's resume for that question. Try asking about his work experience, skills, certifications, or projects.", "remaining": remaining},
            status_code=200,
        )

    context = "\n\n---\n\n".join(context_chunks[:6])  # cap at 6 chunks

    # --- Step 2: Generate answer from Phi-4-mini ---
    try:
        response = _inference_client.chat.completions.create(
            model="Phi-4-mini-instruct",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION: {question}\n\nAnswer using only the CONTEXT above:"},
            ],
            max_tokens=350,
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
