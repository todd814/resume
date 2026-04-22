# resume

[![CI](https://github.com/todd814/resume/actions/workflows/ci.yml/badge.svg)](https://github.com/todd814/resume/actions/workflows/ci.yml)
[![Terraform Plan & Test](https://github.com/todd814/resume/actions/workflows/terraform.yml/badge.svg)](https://github.com/todd814/resume/actions/workflows/terraform.yml)
[![Lint](https://github.com/todd814/resume/actions/workflows/lint.yml/badge.svg)](https://github.com/todd814/resume/actions/workflows/lint.yml)
[![Azure AI](https://github.com/todd814/resume/actions/workflows/azure-ai.yml/badge.svg)](https://github.com/todd814/resume/actions/workflows/azure-ai.yml)

Source code for my online resume and the **Ask My Resume** Azure AI RAG chatbot — both provisioned with Terraform and deployed via GitHub Actions CI/CD.

🌐 **Live site:** https://resume.devious.one

---

## Projects

### Resume Website — AWS
Static single-page resume hosted on AWS infrastructure:
- **S3** — static file hosting
- **CloudFront** — CDN and HTTPS termination
- **Route 53** — DNS
- **IAM** — least-privilege roles and policies
- **Terraform** — all infrastructure as code
- **GitHub Actions** — CI/CD pipeline (lint → validate → deploy)

### Ask My Resume — Azure AI RAG Chatbot
Floating chat widget on the resume that answers questions about my background using retrieval-augmented generation:
- **Azure OpenAI** (GPT-4o) — answer generation
- **Azure AI Search** — semantic search over resume content
- **Azure Functions** (Python 3.11) — serverless RAG API backend
- **Azure Static Web Apps** — standalone chat UI
- **Terraform** — all Azure infrastructure as code
- **GitHub Actions** — deploys function, chat UI, and re-indexes resume content on change

---

## Repository Structure

```
├── src/                        # Resume HTML + Markdown
├── terraform/                  # AWS infrastructure (Terraform)
├── azure-ai/
│   ├── terraform/              # Azure infrastructure (Terraform)
│   ├── functions/              # Azure Functions Python RAG backend
│   ├── chat-ui/                # Standalone chat UI (Azure Static Web Apps)
│   └── scripts/                # Resume indexer for Azure AI Search
└── .github/workflows/          # CI/CD pipelines
```
