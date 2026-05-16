# BOLDR — Self-Improving Customer Intelligence Engine

> **ECHELON 2026 AI Workflow Competition** | Track: REVENUE ROCKET — Sales, Marketing, and Customer Acquisition

**Author:** Steve Ng, Founder and CEO — Digital Futures Consultancy LLP

---

## 🎯 What This Is

BOLDR is a Singapore-based watch micro-brand with a 3-person customer service team drowning in manual email support. This project transforms their reactive support into a **self-improving intelligence engine** — one that answers questions, identifies knowledge gaps, updates its own Knowledge Base, and generates marketing signals automatically.

**This is not a chatbot.** This is a closed-loop intelligence system that gets smarter with every ticket.

---

## 🏗️ Architecture

```
Customer Enquiry (Email/Chat/IG/WhatsApp)
    ↓
n8n Workflow → Intent Extraction → Persona Classification
    ↓
KB Search (ChromaDB + Keyword Hybrid)
    ↓
┌─────────────────┐     ┌──────────────────┐
│  Answer Found?   │─Yes→│  Draft Reply      │→ Human Approval Queue → Send
└────────┬──────────┘     └──────────────────┘
         │ No
         ↓
┌─────────────────┐     ┌──────────────────┐
│  Gap Detection   │────→│  CS Escalation    │→ Human Resolves → KB Auto-Draft
└─────────────────┘     └──────────────────┘
         ↓
┌─────────────────┐
│ Theme Clustering │→ Weekly Theme Report → Monthly Marketing Brief
└─────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Docker Image |
|---|---|---|
| Workflow Orchestration | n8n (self-hosted) | `n8nio/n8n:latest` |
| Vector Store | ChromaDB | `chromadb/chroma:latest` |
| LLM | GLM-5.1 (API) | Cloud API, no container needed |
| Embeddings | BGE-m3 / all-MiniLM-L6-v2 | Built into Python app |
| KB Processing | Python 3.12 (Pandas, LangChain) | `python:3.12-slim` |
| Dashboard | Streamlit | Built into Python app |
| Knowledge Base | Markdown + JSON | Version-controlled in repo |

### Alternative Stack Comparison

See [project_plan.md](../project_plan.md) §5 for full tech stack justification and comparative analysis against Make+GPT-4o+Pinecone, LangGraph+LlamaIndex+Qdrant, and n8n+Claude+ChromaDB.

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/stevenyy88/BOLDR.git
cd BOLDR

# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Start everything with Docker Compose
docker compose up -d

# Access the services:
# - n8n workflow editor: http://localhost:5678
# - Streamlit dashboard: http://localhost:8501
# - ChromaDB: http://localhost:8000
```

---

## 📁 Project Structure

```
BOLDR/
├── README.md                    # This file
├── .gitignore                   # Git ignore rules
├── docker-compose.yml           # One-command deployment
├── .env.example                 # Environment variable template
├── project_plan.md               # Full project plan (symlink)
│
├── app/                         # Python application
│   ├── Dockerfile               # Python app container
│   ├── requirements.txt         # Python dependencies
│   ├── main.py                  # Entry point
│   ├── kb/                      # Knowledge Base indexing
│   │   ├── __init__.py
│   │   ├── indexer.py           # Parse DOCX, CSV, PDF → ChromaDB
│   │   ├── retriever.py         # Hybrid search (vector + keyword)
│   │   └── schemas.py           # KB data schemas
│   ├── classifier/              # Intent + persona classification
│   │   ├── __init__.py
│   │   ├── intent.py            # Question type classification
│   │   ├── persona.py           # Buyer persona tagging (7 personas)
│   │   └── confidence.py        # Confidence scoring
│   ├── generator/               # Reply + KB entry generation
│   │   ├── __init__.py
│   │   ├── reply_drafter.py     # Draft replies in BOLDR brand voice
│   │   ├── kb_auto_draft.py     # Auto-draft KB entries for gaps
│   │   └── brand_voice.py       # Brand voice templates from SOP
│   ├── intelligence/            # Theme clustering + marketing briefs
│   │   ├── __init__.py
│   │   ├── theme_clusterer.py   # Weekly theme clustering
│   │   ├── marketing_brief.py   # Monthly marketing intelligence brief
│   │   ├── gap_detector.py       # Knowledge gap detection + classification
│   │   └── sentiment_benchmark.py # External sentiment (bonus)
│   ├── routing/                 # SOP-derived routing logic
│   │   ├── __init__.py
│   │   ├── sop_parser.py        # Extract rules from CS SOP prose
│   │   ├── escalation_rules.py  # SOP Section 7 escalation triggers
│   │   └── channel_router.py    # Multi-channel input routing
│   ├── dashboard/               # Streamlit UI
│   │   ├── app.py               # Main dashboard
│   │   ├── approval_queue.py     # Reply review + KB approval
│   │   ├── theme_viz.py         # Theme visualisation
│   │   └── kb_manager.py        # KB entry management
│   └── tests/                   # Test suite
│       ├── __init__.py
│       ├── test_classifier.py
│       ├── test_retriever.py
│       ├── test_generator.py
│       ├── test_gap_detector.py
│       ├── test_theme_clusterer.py
│       └── test_e2e.py           # End-to-end workflow tests
│
├── n8n/                         # n8n workflow configurations
│   ├── workflows/               # Exported workflow JSONs
│   │   ├── boldr_intelligence_loop.json
│   │   ├── email_intake.json
│   │   ├── instagram_dm_intake.json
│   │   ├── whatsapp_intake.json
│   │   └── chat_intake.json
│   └── credentials/             # Credential templates (no secrets)
│       └── credentials_template.json
│
├── kb/                          # Knowledge Base source files
│   ├── faq/                     # Parsed FAQ entries (markdown)
│   ├── products/                # Parsed product specs (markdown + JSON)
│   ├── rate_cards/              # Engraving + servicing rate cards
│   └── sop/                     # Parsed CS SOP (markdown)
│
├── data/                        # Sample dataset (gitignored)
│   └── .gitkeep
│
├── docs/                        # Documentation
│   ├── setup.md                 # Setup and installation guide
│   ├── configuration.md         # Configuration reference
│   ├── operations.md             # Operational runbook
│   ├── rubric_checklist.md      # Competition rubric self-assessment
│   ├── architecture.md          # Architecture diagrams and data flow
│   └── demo_script.md           # 5-minute demo video script
│
└── scripts/                     # Utility scripts
    ├── index_kb.py              # Index all KB documents into ChromaDB
    ├── test_all_tickets.py      # Run all 70 tickets through the workflow
    ├── generate_gap_log.py      # Generate knowledge gap log output
    └── benchmark_sentiment.py   # External sentiment benchmarking
```

---

## 📊 Dataset

The BOLDR challenge provides 6 files:

| File | Format | Contents |
|---|---|---|
| `01_customer_tickets.csv` | CSV | 70 anonymised inbound tickets (7 types × 10 each, 4 channels, 7 personas) |
| `02_product_reference.docx` | DOCX | 3 model specs, strap catalogue (10 SKUs), quick-answer table |
| `03a_rate_card_engraving.csv` | CSV | 10 engraving services with pricing and turnaround |
| `03b_rate_card_servicing.csv` | CSV | 9 servicing tiers with pricing and turnaround |
| `04_faq_document.pdf` | PDF | 28 FAQ entries across 6 categories |
| `05_cs_sop.docx` | DOCX | CS SOP with tone guidelines, escalation rules, new questions log |

**Key insight:** 50/70 tickets are answerable by KB. 20 require gap handling — 10 are order operations (need Shopify), 10 are true knowledge gaps (sustainability, niche specs, collector queries).

---

## 🏆 Competition Rubric Alignment

| Criterion | Weight | How We Address It |
|---|---|---|
| **Technical Execution** (25%) | 25% | n8n workflow + ChromaDB hybrid search + confidence scoring + full intelligence loop + Docker deployment |
| **SME Impact & Business Value** (25%) | 25% | 60%+ CS time saved; marketing signals from support data; transforms cost centre into revenue driver |
| **Cost Efficiency** (20%) | 20% | ~$20-55/mo operating cost; 20-50× ROI; self-hosted Docker; open-source stack |
| **Responsible AI** (10%) | 10% | Human-in-the-loop on every reply; no auto-send; confidence scoring; KB versioning; PII handling; fail-safe design |
| **Presentation Quality** (20%) | 20% | 5-min demo video; vlog intro; clear non-technical narrative; architecture diagrams |

### Qualification Checklist

| # | Criterion | Status |
|---|---|---|
| 1 | Problem Identification | ✅ §2 of project_plan.md |
| 2 | Workflow Logic & Demonstration | ✅ Architecture in README, demo in video |
| 3 | Business Impact | ✅ §9 of project_plan.md |
| 4 | Cost Analysis | ✅ §12 of project_plan.md |
| 5 | Safeguards & Human Checks | ✅ §10 of project_plan.md |
| 6 | Proof of Execution | ✅ Public repo, Docker Compose, working prototype |

---

## 🔒 Safeguards & Responsible AI

| Principle | Implementation |
|---|---|
| **Human-in-the-loop** | Every drafted reply queued for human approval before sending. No auto-send. |
| **No hallucination** | KB gap detection routes to CS instead of fabricating answers. Confidence scoring prevents low-quality responses. |
| **Transparency** | Every classification decision logged with reasoning. KB entries show source and approval history. |
| **Privacy / PII** | Customer emails processed in workflow, not stored in KB. PII stripped before theme clustering. |
| **Fail-safe** | If LLM is unavailable, ALL enquiries route to CS team (fail-safe, not fail-open). |
| **Data minimisation** | Only ticket intent and persona tags are persisted. Raw email bodies not stored beyond processing. |

---

## 💰 Cost Analysis

| Scenario | Monthly Cost |
|---|---|
| Conservative (self-hosted, GLM-5.1 only) | ~$10-30/mo |
| Recommended (VPS + GLM-5.1 + Claude fallback) | ~$20-55/mo |
| With sponsor credits (LLM offset) | ~$5-10/mo (VPS only) |

**ROI: 20-50× monthly cost** (saves ~36 hrs/mo of CS time at $30/hr blended rate)

---

## 📜 License

This project is developed for the ECHELON 2026 AI Workflow Competition. All code is the intellectual property of Digital Futures Consultancy LLP.

---

## 🙏 Acknowledgements

- **BOLDR Supply Co.** — Challenge partner providing the real-world problem and sample data
- **e27 / ECHELON** — Competition organiser
- **Digital Futures Consultancy LLP** — Development team

---

*Built with 💼 by the Digital Futures Consultancy Secure Agentic Software Delivery Pod*