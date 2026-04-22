import azure.functions as func
import json
import os
import logging

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
from openai import AzureOpenAI

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

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


@app.route(route="ask", methods=["POST", "OPTIONS"])
def ask_resume(req: func.HttpRequest) -> func.HttpResponse:
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

    # Handle CORS preflight
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=200, headers=cors_headers)

    # Parse request body
    try:
        body = req.get_json()
        question = body.get("question", "").strip()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON body"}),
            status_code=400,
            mimetype="application/json",
            headers=cors_headers,
        )

    if not question:
        return func.HttpResponse(
            json.dumps({"error": "No question provided", "suggested": SUGGESTED_QUESTIONS}),
            status_code=400,
            mimetype="application/json",
            headers=cors_headers,
        )

    if len(question) > 500:
        return func.HttpResponse(
            json.dumps({"error": "Question too long (max 500 characters)"}),
            status_code=400,
            mimetype="application/json",
            headers=cors_headers,
        )

    try:
        # --- Step 1: Retrieve relevant resume chunks from Azure AI Search ---
        search_client = SearchClient(
            endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
            index_name=os.environ["AZURE_SEARCH_INDEX_NAME"],
            credential=AzureKeyCredential(os.environ["AZURE_SEARCH_KEY"]),
        )

        results = search_client.search(
            search_text=question,
            top=5,
            query_type=QueryType.SEMANTIC,
            semantic_configuration_name="resume-semantic-config",
            query_caption="extractive",
            query_answer="extractive",
        )

        context_chunks = []
        for doc in results:
            section = doc.get("section", "")
            content = doc.get("content", "")
            if content:
                context_chunks.append(f"[{section}]\n{content}")

        if not context_chunks:
            return func.HttpResponse(
                json.dumps({"answer": "I couldn't find relevant information in Todd's resume for that question. Try asking about his work experience, skills, certifications, or projects."}),
                status_code=200,
                mimetype="application/json",
                headers=cors_headers,
            )

        context = "\n\n---\n\n".join(context_chunks)

        # --- Step 2: Generate answer with Azure OpenAI ---
        openai_client = AzureOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_key=os.environ["AZURE_OPENAI_KEY"],
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        )

        response = openai_client.chat.completions.create(
            model=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Resume context:\n\n{context}\n\nQuestion: {question}",
                },
            ],
            max_tokens=600,
            temperature=0.3,
        )

        answer = response.choices[0].message.content
        return func.HttpResponse(
            json.dumps({"answer": answer}),
            status_code=200,
            mimetype="application/json",
            headers=cors_headers,
        )

    except Exception as e:
        logging.exception("Error processing ask_resume request")
        return func.HttpResponse(
            json.dumps({"error": "An error occurred processing your request. Please try again."}),
            status_code=500,
            mimetype="application/json",
            headers=cors_headers,
        )


@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Simple health check endpoint."""
    return func.HttpResponse(
        json.dumps({"status": "healthy", "service": "ask-resume"}),
        status_code=200,
        mimetype="application/json",
    )
