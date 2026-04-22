import os
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a helpful AI assistant for Todd DeBlieck's interactive resume. \
Recruiters, hiring managers, and colleagues can ask you questions about Todd's background, \
skills, and experience. Answer only from the provided resume context — do not fabricate details. \
Be concise, professional, and enthusiastic about Todd's accomplishments. \
If a question falls outside the resume context, say so politely and suggest relevant sections."""

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

    try:
        # --- Step 1: Retrieve relevant resume chunks from Azure AI Search ---
        search_client = SearchClient(
            endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
            index_name=os.environ["AZURE_SEARCH_INDEX_NAME"],
            credential=AzureKeyCredential(os.environ["AZURE_SEARCH_KEY"]),
        )

        results = search_client.search(search_text=question, top=5)

        context_chunks = []
        for doc in results:
            section = doc.get("section", "")
            content = doc.get("content", "")
            if content:
                context_chunks.append(f"[{section}]\n{content}")

        if not context_chunks:
            return JSONResponse(
                {"answer": "I couldn't find relevant information in Todd's resume for that question. Try asking about his work experience, skills, certifications, or projects."},
                status_code=200,
            )

        context = "\n\n---\n\n".join(context_chunks)

        # --- Step 2: Generate answer with Phi-4-mini via Azure AI Foundry serverless ---
        # Derive base endpoint — strip /api/projects/... if present
        raw_endpoint = os.environ["AZURE_INFERENCE_ENDPOINT"]
        base_endpoint = raw_endpoint.split("/api/projects/")[0] if "/api/projects/" in raw_endpoint else raw_endpoint

        inference_client = AzureOpenAI(
            azure_endpoint=base_endpoint,
            api_key=os.environ["AZURE_INFERENCE_KEY"],
            api_version="2024-10-21",
        )

        response = inference_client.chat.completions.create(
            model="Phi-4-mini-instruct",  # deployment name
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Resume context:\n\n{context}\n\nQuestion: {question}"},
            ],
            max_tokens=600,
            temperature=0.3,
        )

        answer = response.choices[0].message.content
        return JSONResponse({"answer": answer}, status_code=200)

    except Exception:
        logger.exception("Error processing ask_resume request")
        return JSONResponse(
            {"error": "An error occurred processing your request. Please try again."},
            status_code=500,
        )


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "ask-resume"}
