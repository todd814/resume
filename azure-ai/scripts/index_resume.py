"""
index_resume.py — Chunks Todd_DeBlieck_Resume.md and indexes it into Azure AI Search.

Usage:
    python index_resume.py

Required environment variables (or set in a .env file):
    AZURE_SEARCH_ENDPOINT   — e.g. https://resumeai-search.search.windows.net
    AZURE_SEARCH_KEY        — Admin key from Terraform output: search_admin_key
    AZURE_SEARCH_INDEX_NAME — Default: resume-content

Run this once after Terraform apply, and again whenever the resume MD is updated.
"""

import os
import re
import json
import sys
from pathlib import Path

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from openai import AzureOpenAI
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)

# ── Config ──────────────────────────────────────────────────────────────────

SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
SEARCH_KEY      = os.environ["AZURE_SEARCH_KEY"]
INDEX_NAME      = os.environ.get("AZURE_SEARCH_INDEX_NAME", "resume-content")

EMBEDDING_ENDPOINT   = os.environ.get("AZURE_INFERENCE_ENDPOINT", "")
EMBEDDING_KEY        = os.environ.get("AZURE_INFERENCE_KEY", "")
EMBEDDING_DEPLOYMENT = os.environ.get("AZURE_EMBEDDING_DEPLOYMENT", "text-embedding-3-small-1")

RESUME_MD_PATH       = Path(__file__).parent.parent.parent / "src" / "Todd_DeBlieck_Resume.md"
SUPPLEMENTAL_QA_PATH = Path(__file__).parent.parent.parent / "src" / "content" / "supplemental_qa.md"

# ── Index Definition ─────────────────────────────────────────────────────────

def build_index() -> SearchIndex:
    fields = [
        SimpleField(
            name="id",
            type=SearchFieldDataType.String,
            key=True,
            filterable=True,
        ),
        SearchableField(
            name="content",
            type=SearchFieldDataType.String,
            analyzer_name="en.lucene",
        ),
        SearchableField(
            name="title",
            type=SearchFieldDataType.String,
            analyzer_name="en.lucene",
        ),
        SimpleField(
            name="section",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),
        SimpleField(
            name="chunk_index",
            type=SearchFieldDataType.Int32,
            filterable=True,
            sortable=True,
        ),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_profile_name="hnsw-profile",
        ),
    ]

    return SearchIndex(
        name=INDEX_NAME,
        fields=fields,
        vector_search=VectorSearch(
            algorithms=[HnswAlgorithmConfiguration(name="hnsw-config")],
            profiles=[VectorSearchProfile(name="hnsw-profile", algorithm_configuration_name="hnsw-config")],
        ),
    )


# ── Resume Parsing ────────────────────────────────────────────────────────────

def parse_supplemental_qa(md_path: Path) -> list[dict]:
    """
    Parse supplemental_qa.md Q&A pairs into individual indexed chunks.
    Each Q+A pair becomes one document with section metadata.
    """
    text = md_path.read_text(encoding="utf-8")
    documents = []
    chunk_index = 10000  # offset to avoid ID collisions with resume chunks

    current_section = "Supplemental Q&A"
    section_pattern = re.compile(r"^## (.+)$", re.MULTILINE)
    qa_pattern = re.compile(
        r"\*\*Q: (.+?)\*\*\s*\nA: (.+?)(?=\n\n\*\*Q:|\Z)",
        re.DOTALL,
    )

    # Track section headings for metadata
    section_positions = [(m.start(), m.group(1).strip()) for m in section_pattern.finditer(text)]

    for match in qa_pattern.finditer(text):
        question = match.group(1).strip()
        answer = match.group(2).strip()
        if not answer:
            continue

        # Find which section this Q&A falls under
        pos = match.start()
        section = "Supplemental Q&A"
        for sec_pos, sec_name in section_positions:
            if sec_pos <= pos:
                section = sec_name

        documents.append({
            "id": f"qa-{chunk_index}",
            "title": question,
            "section": f"Supplemental Q&A — {section}",
            "content": f"Q: {question}\nA: {answer}",
            "chunk_index": chunk_index,
        })
        chunk_index += 1

    return documents


def parse_resume(md_path: Path) -> list[dict]:
    """
    Split the resume Markdown into chunks by ## section heading.
    Large sections (Work Experience bullets) are further split into
    individual role blocks so each chunk stays focused.
    """
    text = md_path.read_text(encoding="utf-8")

    # Split on ## headings
    section_pattern = re.compile(r"^## (.+)$", re.MULTILINE)
    splits = list(section_pattern.finditer(text))

    sections = []
    for i, match in enumerate(splits):
        section_title = match.group(1).strip()
        start = match.end()
        end = splits[i + 1].start() if i + 1 < len(splits) else len(text)
        section_body = text[start:end].strip()
        sections.append((section_title, section_body))

    documents = []
    chunk_index = 0

    for section_title, section_body in sections:
        # For Work Experience, split by ### role headings for finer granularity
        if section_title == "Work Experience":
            role_pattern = re.compile(r"^### (.+)$", re.MULTILINE)
            role_splits = list(role_pattern.finditer(section_body))

            for j, role_match in enumerate(role_splits):
                role_title = role_match.group(1).strip()
                role_start = role_match.end()
                role_end = role_splits[j + 1].start() if j + 1 < len(role_splits) else len(section_body)
                role_body = section_body[role_start:role_end].strip()

                documents.append({
                    "id": f"work-{chunk_index}",
                    "title": role_title,
                    "section": "Work Experience",
                    "content": f"{role_title}\n\n{role_body}",
                    "chunk_index": chunk_index,
                })
                chunk_index += 1
        else:
            # Split other long sections into ~800-char chunks with overlap
            chunks = chunk_text(section_body, max_chars=800, overlap=100)
            for chunk in chunks:
                documents.append({
                    "id": f"chunk-{chunk_index}",
                    "title": section_title,
                    "section": section_title,
                    "content": chunk,
                    "chunk_index": chunk_index,
                })
                chunk_index += 1

    return documents


def chunk_text(text: str, max_chars: int = 800, overlap: int = 100) -> list[str]:
    """Split text into overlapping chunks on paragraph boundaries."""
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 > max_chars and current:
            chunks.append(current.strip())
            # Carry over the last paragraph as overlap
            current = current[-overlap:] + "\n\n" + para if len(current) > overlap else para
        else:
            current = f"{current}\n\n{para}" if current else para

    if current.strip():
        chunks.append(current.strip())

    return chunks if chunks else [text]


# ── Embedding ─────────────────────────────────────────────────────────────────

def embed_texts(client: AzureOpenAI, texts: list[str], deployment: str) -> list[list[float]]:
    """Embed texts with text-embedding-3-small in batches of 16. Returns 1536-dim vectors."""
    vectors: list[list[float]] = []
    batch_size = 16
    total_batches = (len(texts) + batch_size - 1) // batch_size
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = client.embeddings.create(model=deployment, input=batch)
        vectors.extend([item.embedding for item in response.data])
        print(f"  Embedded batch {i // batch_size + 1}/{total_batches} ({len(batch)} items)")
    return vectors


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not RESUME_MD_PATH.exists():
        print(f"ERROR: Resume file not found at {RESUME_MD_PATH}", file=sys.stderr)
        sys.exit(1)

    credential = AzureKeyCredential(SEARCH_KEY)

    # Create or update index
    print(f"Creating/updating index '{INDEX_NAME}' ...")
    index_client = SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=credential)
    index_client.create_or_update_index(build_index())
    print("  Index ready.")

    # Parse and chunk resume
    print(f"Parsing {RESUME_MD_PATH.name} ...")
    documents = parse_resume(RESUME_MD_PATH)
    print(f"  {len(documents)} resume chunks created.")

    # Parse supplemental Q&A
    if SUPPLEMENTAL_QA_PATH.exists():
        print(f"Parsing {SUPPLEMENTAL_QA_PATH.name} ...")
        qa_docs = parse_supplemental_qa(SUPPLEMENTAL_QA_PATH)
        print(f"  {len(qa_docs)} Q&A chunks created.")
        documents.extend(qa_docs)
    else:
        print(f"No supplemental Q&A found at {SUPPLEMENTAL_QA_PATH}, skipping.")

    # Generate embeddings
    missing_embed = [v for v in ["AZURE_INFERENCE_ENDPOINT", "AZURE_INFERENCE_KEY"] if not os.environ.get(v)]
    if missing_embed:
        print(f"ERROR: Missing env vars for embeddings: {', '.join(missing_embed)}", file=sys.stderr)
        sys.exit(1)

    print(f"Generating embeddings with '{EMBEDDING_DEPLOYMENT}' ...")
    embed_client = AzureOpenAI(
        azure_endpoint=EMBEDDING_ENDPOINT,
        api_key=EMBEDDING_KEY,
        api_version="2025-01-01-preview",
    )
    texts = [doc["content"] for doc in documents]
    vectors = embed_texts(embed_client, texts, EMBEDDING_DEPLOYMENT)
    for doc, vector in zip(documents, vectors):
        doc["content_vector"] = vector
    print(f"  {len(vectors)} embeddings generated.")

    # Upload documents
    print("Uploading documents to Azure AI Search ...")
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=credential,
    )
    result = search_client.upload_documents(documents=documents)
    succeeded = sum(1 for r in result if r.succeeded)
    failed    = sum(1 for r in result if not r.succeeded)
    print(f"  Uploaded: {succeeded} succeeded, {failed} failed.")

    if failed:
        print("WARNING: Some documents failed to upload.", file=sys.stderr)
        sys.exit(1)

    print("\nDone! Resume is now searchable in Azure AI Search.")
    print(f"Index: {INDEX_NAME}")
    print(f"Endpoint: {SEARCH_ENDPOINT}")


if __name__ == "__main__":
    main()
