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
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
)

# ── Config ──────────────────────────────────────────────────────────────────

SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
SEARCH_KEY      = os.environ["AZURE_SEARCH_KEY"]
INDEX_NAME      = os.environ.get("AZURE_SEARCH_INDEX_NAME", "resume-content")

RESUME_MD_PATH  = Path(__file__).parent.parent.parent / "src" / "Todd_DeBlieck_Resume.md"

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
    ]

    semantic_config = SemanticConfiguration(
        name="resume-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="title"),
            content_fields=[SemanticField(field_name="content")],
            keywords_fields=[SemanticField(field_name="section")],
        ),
    )

    return SearchIndex(
        name=INDEX_NAME,
        fields=fields,
        semantic_search=SemanticSearch(configurations=[semantic_config]),
    )


# ── Resume Parsing ────────────────────────────────────────────────────────────

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
    print(f"  {len(documents)} chunks created.")

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
