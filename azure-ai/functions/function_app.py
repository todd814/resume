import os
import time
import json
import logging
from collections import defaultdict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Rate limiting ─────────────────────────────────────────────────────────────
RATE_LIMIT  = 10       # max questions per IP
RATE_WINDOW = 86400    # sliding window: 24 hours in seconds

_rate_store: dict[str, list[float]] = defaultdict(list)


def _get_client_ip(request: Request) -> str:
    """Extract real client IP, preferring X-Forwarded-For from Azure/CDN."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _check_rate_limit(ip: str) -> tuple[bool, int]:
    """
    Sliding window check. Returns (allowed, remaining).
    Mutates _rate_store: appends timestamp if allowed, prunes stale entries.
    """
    now = time.time()
    cutoff = now - RATE_WINDOW
    # Prune requests outside the window
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
    "What AWS services has Todd worked with?",
    "Tell me about Todd's Epic certifications.",
    "What AI tools does Todd use?",
    "Describe Todd's Cosmos Administrator experience.",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

    # --- Step 2: Stream answer from Phi-4-mini ---
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION: {question}\n\nAnswer using only the CONTEXT above:"},
    ]

    def _stream_generator():
        try:
            stream = _inference_client.chat.completions.create(
                model="Phi-4-mini-instruct",
                messages=messages,
                max_tokens=350,
                temperature=0.0,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield f"data: {json.dumps({'chunk': chunk.choices[0].delta.content})}\n\n"
            yield f"data: {json.dumps({'done': True, 'remaining': remaining})}\n\n"
        except Exception:
            logger.exception("Inference streaming error")
            yield f"data: {json.dumps({'error': 'Inference failed. Please try again.'})}\n\n"

    return StreamingResponse(
        _stream_generator(),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "ask-resume"}
