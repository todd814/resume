# Todd DeBlieck

**AI Practitioner | Empirical AI Research Candidate | Healthcare EMR Domain Expert**

- **Location:** Richmond, VA
- **Email:** todd@deblieck.me
- **Chat:** [AI Chat](https://ask.todd.deblieck.me/)
- **LinkedIn:** [todd-deblieck](https://www.linkedin.com/in/todd-deblieck-53b13b13/)
- **Website:** [todd.deblieck.me](https://todd.deblieck.me/)
- **GitHub:** [github.com/todd814/resume](https://github.com/todd814/resume/)

---

## Summary

AI Practitioner making a deliberate transition into empirical AI research, motivated by ensuring AI systems are safe and beneficial for humanity. Over the past year, moved well beyond theoretical AI literacy into hands-on experimentation: built and deployed a production retrieval-augmented generation (RAG) system, conducted local LoRA fine-tuning experiments, explored Azure AI Foundry and Document Intelligence services, and developed systematic prompt and system-prompt engineering practices — treating each design decision as an empirical question with testable outcomes.

Brings 15+ years of domain expertise observing and driving technology transformation inside healthcare — one of the largest industries in the US and one of the highest-stakes environments for AI deployment, where accuracy, equity, safety, and accountability are non-negotiable. That vantage point, bridging clinical operations and technical systems at scale, is directly relevant to studying AI's economic effects and societal implications.

Thrives in fast-paced, collaborative environments. That instinct was forged first as a Marine Corps NCO executing missions under time-critical conditions and has been applied across every stage of a 15-year career coordinating complex, cross-functional work. Can implement ideas quickly and communicate findings clearly to both technical and non-technical stakeholders.

Holds the **Microsoft Certified: AI Business Professional** credential and an assessed **Applied Skill in building generative AI applications**. Completed the **Microsoft & LinkedIn Professional Certificate: AI for Organizational Leaders** — covering responsible AI leadership, integrating AI into business strategy, building organization-wide AI aptitude, and evaluating the societal implications of generative AI. Technical interest in ML and Python dates to 2019, when IBM credentials in *Python for Data Science*, *Applied Data Science with Python*, and *Machine Learning with Python* established a foundational understanding that has grown continuously since.

---

## AI Research & Experimentation Skills

**Fine-Tuning & Model Experimentation**
Local LoRA fine-tuning experiments exploring how supervised fine-tuning shapes model behavior — including the relationship between training data composition, hyperparameters, and output quality. Azure AI Foundry services for inference and model management *(Microsoft Applied Skill: Build a Generative AI Chat App; Develop an AI app with the Microsoft Foundry SDK)*; Azure Document Intelligence for structured information extraction from unstructured documents. Iterative prompt and system-prompt engineering with systematic behavioral testing across model variants. Foundational ML theory grounded in IBM credentials: *Machine Learning with Python – Level 1* and *Applied Data Science with Python – Level 2* (2019).

**Retrieval-Augmented Generation (RAG)**
Designed and deployed a RAG system: evaluated BM25 keyword retrieval vs. semantic vector search for factual grounding; implemented query normalization (third-person → first-person conversion to improve recall); tuned chunking strategies and context window usage; validated answer quality across diverse question types. Each architectural choice made through empirical testing, not convention.

**Large Language Models**
Daily hands-on use of Claude (Anthropic), ChatGPT, and GitHub Copilot as research and development tools. Experience building on LLM APIs (Azure OpenAI, Azure AI Foundry) to construct inference pipelines. System-prompt design for behavioral control, tone, and output constraints. Formal training in responsible AI principles, AI governance, and safety considerations in AI deployment, including assessed completion of: *Embrace Responsible AI Principles and Practices* · *Introduction to Generative AI and Agents* · *Generative AI Essentials: Using LLMs to Work with Data* (IBM SkillsBuild) · *AI Fundamentals with Capstone Project* (IBM SkillsBuild).

**Python & AI-Assisted Development**
Python scripting and AI-assisted development applied to RAG indexing pipelines, FastAPI backends, LoRA fine-tuning workflows, and infrastructure automation. Strong structural understanding of code; leverages AI pair programming to extend implementation speed and reach. Python foundation established through IBM credentials: *Python for Data Science* · *Applied Data Science with Python – Level 2* · *Machine Learning with Python – Level 1* (2019), with continued applied use across every hands-on AI project since.

**Azure Cloud & AI Services**
Azure AI Foundry · Azure AI Search · Azure Container Apps · Azure Static Web Apps · Azure OpenAI Service · Azure Document Intelligence · Log Analytics · Terraform

**Infrastructure as Code & DevOps**
Terraform for cloud resource provisioning; GitHub Actions for CI/CD pipelines; automated deployments and infrastructure lifecycle management; Docker.

**Additional Programming & Data**
PowerShell · Bash · SQL · YAML · HTML · CSS

**AWS Cloud Infrastructure**
AWS Certified Solutions Architect – Associate; Route 53, EC2, S3, CloudFront, Auto Scaling, RDS, DynamoDB, VPC.

---

## Projects

### Ask My Resume — Production RAG System (Empirical AI Design)
**2026 – Current** | [github.com/todd814/resume/azure-ai](https://github.com/todd814/resume/tree/main/azure-ai)

Designed, built, and deployed a production retrieval-augmented generation system from scratch — treating every architectural decision as an empirical question. Evaluated BM25 keyword retrieval vs. semantic vector search for factual grounding accuracy; implemented query normalization to convert third-person queries to first-person before embedding, improving recall against first-person indexed content; tuned chunking strategy and context window usage to balance coverage against hallucination risk; systematically validated answer quality across diverse question types.

Backend: FastAPI on Azure Container Apps (scale-to-zero); Azure AI Search for retrieval; Phi-4-mini-instruct via Azure AI Foundry for generation. Full infrastructure managed with Terraform (Cloud backend) and deployed via GitHub Actions CI/CD.

**Stack:** Azure AI Foundry · Phi-4-mini-instruct · Azure AI Search · Azure Container Apps · Static Web Apps · Terraform · Python · FastAPI · GitHub Actions

*This project directly fulfills the Microsoft Applied Skill: Build a Generative AI Chat App credential (April 2026) — an assessed, hands-on evaluation of generative AI application development.*

---

### LoRA Fine-Tuning & Document Intelligence Exploration
**2025 – Current**

Active fine-tuning and model experimentation across two tracks: (1) domain-specific Gemma 3 fine-tuning for the Aurelius app (see below) — building JSONL corpora, running curriculum and mixed training strategies, and exporting quantized LiteRT models for on-device deployment; (2) broader exploration of LoRA fine-tuning to understand how training data composition, learning rate, and strategy affect output behavior across prompting styles. Exploring Azure Document Intelligence for structured information extraction from clinical and operational documents. Developing systematic prompt and system-prompt engineering practices — designing behavioral tests, comparing outputs across model variants, and documenting what changes. Grounded in IBM credentials: *AI Fundamentals with Capstone Project* and *Generative AI Essentials: Using LLMs to Work with Data* (Nov 2025); ML theory foundation from *Machine Learning with Python – Level 1* (2019).

---

### Aurelius — Stoic Tinnitus Wellness Android App (On-Device LLM + Fine-Tuning Pipeline)
**2025 – Current**

Built a production Android app that deploys a fine-tuned Gemma 3 1B model entirely on-device for a sensitive mental health use case — chronic severe tinnitus management. The project spans three AI engineering layers: fine-tuning, inference optimization, and responsible deployment design.

**Fine-tuning pipeline:** Constructed two domain-specific JSONL training corpora — one for Stoic philosophy and mentorship style, one for tinnitus clinical guidance, TFI scoring, and differential diagnosis context. Implemented end-to-end training orchestration (curriculum and mixed strategies), model merging, and LiteRT export via Python scripts. Augmented corpora programmatically using `augment_training_data.py` targeting 5,000+ samples per domain before training runs.

**On-device inference:** Deployed quantized int4 Gemma 3 1B via LiteRT-LM bundled directly in the APK. Integrated MediaPipe text classification for journal sentiment analysis and a TFLite recommendation engine for adaptive practice routing — all fully offline with no external API calls.

**Responsible AI design:** The use case demanded serious safety constraints. Applied multi-dimensional clinical grounding — injecting TFI scores, PSQI sleep data, PCL-5 PTSD checklist results, and etiology cluster scores into LLM context before every response to reduce hallucination risk and keep guidance clinically appropriate. Built a red flag triage module with emergency escalation for dangerous presentations (unilateral pulsatile tinnitus, sudden hearing loss, neurological signs) and integrated VA crisis line routing into PCL-5 scoring. Response shaping actively suppresses repetitive phrasing and bounds conversational history to prevent context drift.

**Empirical testing harness:** Built a Python parity harness (`chat_cli.py`) that runs the identical LLM pipeline via Android instrumentation when a device is connected, or falls back to local terminal mode — enabling reproducible behavioral testing across environments. Supports golden file regression tests, seed data profiles (minimal through full-14d), and dry-run validation.

**Stack:** Kotlin · Jetpack Compose · LiteRT-LM (Gemma 3 1B int4) · MediaPipe · TFLite · Room · Python · MVVM · Jetpack WindowManager · Android AudioTrack

---

### Self-Hosted Resume — AWS + Terraform + GitHub Actions
**2020 – 2026** | [github.com/todd814/resume](https://github.com/todd814/resume/)

Provisioned all AWS infrastructure using Terraform; implemented a fully automated GitHub Actions CI/CD pipeline with linting, validation, and deployment stages. Version-controlled, reproducible infrastructure at production grade.

**Stack:** AWS S3 · CloudFront · Route 53 · IAM · Terraform · GitHub Actions

---

<div style="break-before: page; page-break-before: always;"></div>

## Work Experience

### Senior Application Coordinator | Clinical Content | Cosmos — Nordic Global *(supporting Bon Secours Mercy Health I&T)*
**January 2024 – Current**

- Administer and govern data mappings within Epic Cosmos — one of the largest real-world clinical data platforms in existence — ensuring data integrity, interoperability, and compliance with governance standards across a large health system.
- Direct analysis and implementation planning for new Cosmos platform features, managing end-to-end rollouts that affect downstream data quality and clinical research utility.
- Serve as subject matter expert bridging clinical operations and data platform needs — translating between technical systems and real-world healthcare workflows at scale for cross-functional stakeholders and leadership.

---

### Sr. Application Coordinator | Clinical Content — Nordic Global *(formerly Bon Secours Mercy Health)*
**August 2016 – Current**

- Built metadata tracking and reporting solutions, including executive Tableau dashboards for clinical Order Set utilization and governance visibility — applying empirical data analysis to drive operational decisions.
- Applied data analysis to identify and retire ~2,200 unused clinical Order Sets, reducing the active inventory from ~4,000 to ~1,800 in the first year; designed the policy-aligned workflow that made the change durable.
- Developed custom SQL and Reporting Workbench analyses to identify cross-environment discrepancies and resolve documentation gaps for VTE/Sepsis quality workflows — turning raw data into actionable clinical improvements.
- Pioneered workflow redesigns that reduced large-scale implementation timelines and analyst overhead; moved fast without sacrificing quality.
- Lead complex, cross-functional project work: coordinated diverse stakeholders, tracked deliverables, and communicated findings and status clearly to leadership.
- Execute ITIL-aligned support processes across Incident, Request, and Change Management; mentored new analysts through onboarding and Epic certification.

---

### Co-Founder & CEO | Peace Out Richmond LLC
**2021 – Current** | Service-Disabled Veteran-Owned Small Business (SDVOSB)

- Co-founded and operate a Service-Disabled Veteran-Owned Small Business; maintain SDVOSB certification compliance and SAM.gov registration to preserve federal contracting eligibility.
- Direct all business operations: financial management, P&L oversight, budgeting, and quarterly tax obligations — full administrative accountability for an independent business entity.
- Drive strategic planning, business development, and client relationship management; responsible for identifying opportunities, building partnerships, and sustaining revenue.
- Manage vendor relationships, contractor coordination, and procurement to support day-to-day and project-based operational needs.
- Oversee marketing, brand positioning, and all external-facing business communications.
- Maintain legal and regulatory compliance including business licensing, liability coverage, and applicable state and federal reporting requirements.

---

### Identity and Access Management (IAM) Application Coordinator — Bon Secours Health System
**August 2015 – August 2016**

- Led IAM implementation for the health system's first Epic partner, delivering on schedule.
- Developed a PowerShell automation suite to process large-scale user data — generating Employee Access Records and Role-Based Access Control (RBAC) spreadsheets — replacing a slow, manual, error-prone process with a reliable, repeatable one.
- Built a script to retrieve and bulk-validate data against the NPPES NPI Registry API; developed Excel macros for post-processing and EMR import.

---

### Orders Application Coordinator — Bon Secours Health System
**April 2010 – August 2015**

- Led a physician workspace and order mode redesign project: analyzed clinical requirements, defined inclusion/exclusion criteria, and deployed a new "Within Scope of Clinical Practice" order mode that improved nurse workflow efficiency across the enterprise.
- Developed a custom provider sidebar for required documentation — core measures, clinical rules — using required documentation logic.
- Led migration of team content from an Oracle-based intranet to SharePoint; served as site owner and established standardized distribution processes.
- Mentored new analysts through onboarding and Epic certification; ensuring they had the context and tools to become effective contributors quickly.

---

### Go-Live Support Consultant
**April 2009 – April 2010**

End-user go-live support for Stanford University's Dermatology Clinic, Sentara Hospital, and University of Chicago Hospital during Epic EMR implementations.

---

### Sergeant — United States Marine Corps
**May 2008 – April 2009**

- Recalled to active duty; led a convoy security and Quick Reaction Force element conducting logistics security missions in Iraq — responsible for team readiness, mission execution, and real-time decisions under hostile and time-critical conditions.
- Directed command center operations: coordinated multiple deployed units simultaneously, triaged incoming mission data, and relayed time-sensitive information to maintain continuity of operations — the definition of fast-paced, high-stakes, collaborative work.
- Maintained accountability for cryptographic communication systems and secure protocol compliance with zero tolerance for failure.

---

### Military Police — United States Marine Corps
**August 2002 – August 2006**

- Competitively selected for a Marine Expeditionary Unit (MEU); led security operations across the Pacific including humanitarian clinics, port security, and shore patrol.
- Appointed Night Shift Desk Sergeant as a Lance Corporal — two grades below the typical billet requirement — commanding shift operations, dispatching units, managing live incident response, and reporting directly to Base Commander's staff.
- Deployed to Iraq; led convoy security missions under threat conditions, responsible for team safety and mission success in a combat environment.
- Combat-disabled veteran; sustained service-connected injury in theater.

---

<div style="break-before: page; page-break-before: always;"></div>

## Certifications & AI Training

**Credentials**
- [Microsoft Certified: AI Business Professional](https://learn.microsoft.com/api/credentials/share/en-us/todd814/8A24F4E73ACC4C86?sharingId=7A5F48460A651ED7) (April 2026) — responsible AI governance, AI strategy, scaling AI adoption
- [Microsoft Applied Skill: Build a Generative AI Chat App](https://learn.microsoft.com/en-us/users/todd814/) (April 2026) — assessed, hands-on generative AI application development
- [AI for Organizational Leaders — Professional Certificate](https://www.linkedin.com/learning/certificates/31f95bad084096ff31c4538ea73ada9361c543fc22f5a009fc6bc3bd43e01fb5) — Microsoft & LinkedIn Learning (May 2026) — responsible AI leadership, AI business strategy, building org-wide AI aptitude, evaluating generative AI's societal implications
- AWS Certified Solutions Architect – Associate *(expired Mar 2023)*
- [All badges and credentials on Credly](https://www.credly.com/users/todd-deblieck)

**IBM SkillsBuild & IBM — AI, ML, and Python Credentials** *(via Credly)*

| Badge | Issued |
|---|---|
| Generative AI Essentials: Using LLMs to Work with Data | Nov 2025 |
| Artificial Intelligence Fundamentals with Capstone Project | Nov 2025 |
| Artificial Intelligence Fundamentals | Nov 2025 |
| Machine Learning with Python – Level 1 | Mar 2019 |
| Applied Data Science with Python – Level 2 | Mar 2019 |
| Python for Data Science | Feb 2019 |
| Docker Essentials: A Developer Introduction | Mar 2019 |

*The 2019 IBM credentials reflect a long-standing technical interest in ML and Python that predates the current generative AI wave — not a recent pivot.*

**Microsoft Learn — Completed Learning Paths** *([View full profile](https://learn.microsoft.com/en-us/users/todd814/))*

| Path | Completed |
|---|---|
| Build a generative AI chat app *(Applied Skill)* | Apr 2026 |
| Discover AI for leaders in healthcare | Apr 2026 |
| Discover AI for leaders in sustainability | Apr 2026 |
| Transform your business with AI | Apr 2026 |
| Drive business value with AI solutions | Apr 2026 |
| Explore the business value of generative AI solutions | Apr 2026 |
| Transform business workflows with generative AI | Apr 2026 |

**Selected Modules — Directly Relevant to AI Safety & Research**

- [Embrace responsible AI principles and practices](https://learn.microsoft.com/en-us/training/modules/embrace-responsible-ai-principles-practices/) *(Apr 2026)* — AI ethics, harm mitigation, fairness, transparency, and accountability frameworks
- [Develop an AI app with the Microsoft Foundry SDK](https://learn.microsoft.com/en-us/training/modules/ai-foundry-sdk/) *(Apr 2026)* — hands-on SDK-level AI application development
- [Introduction to generative AI and agents](https://learn.microsoft.com/en-us/training/modules/fundamentals-generative-ai/) *(Feb 2026)* — agentic AI systems and generative AI foundations
- [Scale AI in your organization](https://learn.microsoft.com/en-us/training/modules/scale-ai/) *(Apr 2026)* — organizational AI deployment, governance, and risk
- [Define a Microsoft AI strategy to create business value in healthcare](https://learn.microsoft.com/en-us/training/modules/define-microsoft-ai-strategy-healthcare/) *(Apr 2026)* — AI deployment considerations in high-stakes healthcare environments

---

## Education

| Institution | Program | Years |
|---|---|---|
| Western Governors University | Humanities and Science | 2022–2023 |
| Strayer University | General Studies | 2013 |
| Coastline Community College | General Studies | 2007–2008 |

---

## Domain Expertise Note

Fifteen years inside healthcare — one of the largest and highest-stakes industries in the US for AI deployment, where accuracy, equity, and accountability are non-negotiable. Firsthand experience with large-scale clinical data platforms (Epic Cosmos), how AI and technology deployment decisions affect real-world patient and clinician outcomes, and how organizations succeed or fail at translating technical capability into measurable value. Directly relevant to research on AI's economic effects, labor market impacts, and societal implications.

---

## Epic Certifications

- Cosmos Administration
- Cosmos Super User Badge
- Cosmos Researcher Badge
- Inpatient Procedural Orders Certification
