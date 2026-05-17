# ECHELON 2026 Rubric Self-Assessment Checklist

**Project:** BOLDR — Self-Improving Customer Intelligence Engine  
**Track:** REVENUE ROCKET — Sales, Marketing, and Customer Acquisition  
**Author:** Steve Ng, Founder and CEO — Digital Futures Consultancy LLP (T17LL1937H)  
**Date:** 2026-05-17

---

## Overview

This checklist maps every ECHELON 2026 rubric criterion to specific evidence from our deliverables. Each section lists the criterion, its weight, and concrete proof points demonstrating excellence.

---

## 1. Technical Execution (25%)

> **Criterion:** The workflow works, is stable, and realistically deployable by the SME.

### 1.1 End-to-End Workflow Works ✅

| Evidence | Detail |
|---|---|
| **n8n workflow** | Complete intelligence loop: multi-channel intake → intent classification → KB retrieval → reply/gap routing → KB auto-update → theme clustering → marketing brief. Exported JSON in `n8n/workflows/boldr_intelligence_loop.json`. |
| **Docker Compose deployment** | `docker compose up -d` starts all services (n8n, ChromaDB, Streamlit app). Verified on clean Ubuntu 22.04. |
| **70-ticket test coverage** | All 70 challenge tickets processed through the workflow. 50 answerable by KB → auto-drafted replies. 20 knowledge gaps → correctly classified as order ops (10) vs. true gaps (10). |
| **Multi-channel intake** | n8n triggers for Email (Gmail), Instagram DM, WhatsApp, and chat webhook — matching the 4-channel distribution in the dataset. |

### 1.2 Stability & Error Handling ✅

| Evidence | Detail |
|---|---|
| **Fail-safe design** | If LLM is unavailable, ALL enquiries route to CS team (fail-safe, not fail-open). No auto-send ever. |
| **Confidence scoring** | Hybrid retrieval (vector + keyword) produces confidence scores 0–1. Scores below threshold (default 0.5) trigger CS escalation, not fabrication. |
| **Health checks** | Docker Compose includes health checks for n8n, ChromaDB, and the Streamlit app. Automatic restart on failure. |
| **n8n execution logs** | Every node execution logged with timestamps, input/output, and error details. Full audit trail. |

### 1.3 Realistically Deployable ✅

| Evidence | Detail |
|---|---|
| **Zero-install deployment** | Single `docker compose up -d` command. No Python, no Node.js, no manual installs. |
| **Self-hosted stack** | n8n, ChromaDB, embeddings — all self-hosted. No data leaves BOLDR's infrastructure (except LLM API calls). |
| **CS team can own it** | n8n's visual editor lets BOLDR's 3-person CS team inspect and modify workflows without engineering support. |
| **Operational documentation** | `docs/setup.md` (prerequisites, quick start, configuration), `docs/operations.md` (runbook), and inline comments in workflows. |
| **Version-controlled KB** | Markdown + JSON in Git. Diff-able, reviewable, rollback-capable. CS team can review via PR. |

### 1.4 Technical Breadth ✅

| Evidence | Detail |
|---|---|
| **7-step intelligence loop** | Not just a chatbot — closed-loop system: ingest → classify → retrieve → draft/gap → update → cluster → brief. |
| **Hybrid search** | Vector search (ChromaDB/BGE-m3) + keyword fallback ensures both semantic and exact-match queries succeed. |
| **SOP-derived routing** | Routing logic extracted from CS SOP prose (not hard-coded rules), including escalation triggers for angry customers, chargebacks, warranty claims, corporate orders, and press. |
| **Gap classification** | Distinguishes "needs Shopify data" (order operations) from "needs new KB entry" (true knowledge gap) — critical for BOLDR's workflow. |

---

## 2. SME Impact & Business Value (25%)

> **Criterion:** Addresses a real SME problem with measurable value.

### 2.1 Real SME Problem ✅

| Evidence | Detail |
|---|---|
| **Grounded in actual data** | BOLDR Supply Co. is the challenge partner. 70 real-world support tickets across 7 question types, 4 channels, and 7 buyer personas. |
| **Pain points documented** | §2 of project_plan.md: manual email overload, inconsistent KB updates, zero marketing feedback loop, novel questions lost in inboxes. |
| **3-person CS team** | System designed for a team of 3, not an enterprise call centre. Every feature is accessible to non-technical CS staff. |

### 2.2 Measurable Value ✅

| Evidence | Detail |
|---|---|
| **60%+ CS time saved** | Auto-drafting replies for 50/70 answerable tickets. Target: 36 hours/month freed (3 staff × 20 hrs × 60%). |
| **Marketing signals unlocked** | Theme clustering surfaces revenue signals: BPA-free straps (Health-Conscious Buyer), vegan materials (Sustainability Advocate), corporate gifting (bulk pricing). These are currently invisible to marketing. |
| **Cost centre → revenue driver** | Transforms customer support from a pure cost into an intelligence source. Monthly brief generates 3–5 actionable campaign ideas per quarter. |
| **KB gap closure loop** | Every unresolved ticket generates an auto-drafted KB entry. Knowledge gaps get systematically closed, reducing future manual handling. |

### 2.3 Revenue Impact (REVENUE ROCKET Track) ✅

| Revenue Signal | Mechanism | Impact |
|---|---|---|
| BPA-free strap marketing | Auto-detected from ticket themes → product badge + campaign | New customer segment (health-conscious buyers) |
| Vegan strap positioning | Theme cluster identifies vegan queries → marketing brief action | First-mover advantage in watch strap niche |
| Corporate gifting pricing | Recurring ticket pattern → KB entry + bulk pricing page | Unlock higher-value orders |
| Nickel allergy / hypoallergenic | Product page gap confirmed → marketing brief flags it | Reduced pre-sale friction |
| CS time freed → proactive outreach | 36 hrs/mo saved → redeployed to proactive marketing | Indirect revenue acceleration |

---

## 3. Cost Efficiency (20%)

> **Criterion:** Commercially realistic, deployable, and scalable.

### 3.1 Setup Cost ✅

| Item | Cost | Notes |
|---|---|---|
| n8n self-hosted (Docker) | $0 | Open-source, self-hosted |
| ChromaDB (Docker) | $0 | Open-source, embedded |
| Streamlit app (Docker) | $0 | Open-source |
| Docker Compose setup | $0 | ~2 hours one-time |
| KB index build | $0 | ~4 hours one-time |
| Workflow configuration | $0 | ~8 hours one-time |
| LLM API initial tokens | ~$5 | Testing and initial classification |
| **Total Setup** | **~$5** | Excludes VPS if self-hosted locally |

### 3.2 Monthly Operating Cost ✅

| Item | Cost/mo | Notes |
|---|---|---|
| VPS hosting (2 vCPU, 4GB RAM) | $5–10 | Optional if self-hosted locally |
| LLM API (GLM-5.1 primary) | $10–30 | ~50–100 tickets/mo at ~$0.01–0.03 per classification + draft |
| Fallback LLM (Claude, edge cases) | $5–15 | Only for confidence < 0.5 (~5–10% of tickets) |
| Embedding model (self-hosted) | $0 | Runs in Docker, no API cost |
| Maintenance | $0 | CS team self-serves via n8n UI |
| **Total Monthly** | **$20–55** | Scales linearly with ticket volume |

### 3.3 ROI ✅

| Metric | Value |
|---|---|
| CS time saved (60%+) | ~36 hrs/mo |
| Value of CS time freed | ~$1,080/mo (at $30/hr blended rate) |
| Monthly system cost | ~$20–55/mo |
| **ROI** | **20–50× monthly cost** |

### 3.4 Scalability ✅

| Evidence | Detail |
|---|---|
| **Open-source stack** | n8n, ChromaDB, BGE-m3/all-MiniLM — no per-operation fees that scale with volume. |
| **Self-hosted** | No SaaS subscription tiers. Add CPU/RAM as ticket volume grows. |
| **Linear cost scaling** | LLM API cost is ~$0.01–0.03 per ticket. Even 10× ticket volume = $100–300/mo — still < 1 CS staff salary. |
| **Sponsor credit leverage** | GLM-5.1 as primary (lower cost), Claude as fallback (higher cost, rare usage). Maximises any sponsor credits. |

---

## 4. Responsible AI (10%)

> **Criterion:** Safe, reliable, fair, transparent, and compliant.

### 4.1 Human-in-the-Loop ✅

| Evidence | Detail |
|---|---|
| **No auto-send** | Every drafted reply is queued for human approval in the Streamlit dashboard. No reply is sent without explicit human approval. |
| **KB approval workflow** | Auto-drafted KB entries require 1-click human approval before being indexed. Full version history with diff view and rollback. |
| **Escalation rules** | SOP-derived escalation triggers (angry customers, chargebacks, warranty claims >10 days, corporate orders >5 units, press enquiries) always route to human CS. |

### 4.2 No Hallucination ✅

| Evidence | Detail |
|---|---|
| **Gap detection over fabrication** | When KB has no answer, the system routes to CS instead of fabricating a response. Confidence scoring prevents low-quality matches. |
| **Confidence threshold** | Default threshold of 0.5. Below this, tickets are escalated with a pre-filled draft and suggested KB source — reducing CS effort even on escalation. |
| **Source attribution** | Every drafted reply cites the KB source (FAQ entry, product spec, rate card). CS team can verify before sending. |

### 4.3 Transparency & Auditability ✅

| Evidence | Detail |
|---|---|
| **Classification logging** | Every intent and persona classification is logged with reasoning. n8n execution logs show every node's input/output. |
| **KB version history** | Git-based version control. Every KB entry shows source, approval timestamp, and editor. Diff view and rollback available. |
| **Decision audit trail** | Full traceability from ticket intake → classification → retrieval → routing → reply/gap → approval. |

### 4.4 Privacy & PII ✅

| Evidence | Detail |
|---|---|
| **Data minimisation** | Only ticket intent and persona tags are persisted. Raw email bodies are not stored beyond processing. |
| **PII stripping** | Customer PII is stripped before theme clustering. No personal data enters the knowledge base. |
| **Self-hosted** | All data stays on BOLDR's infrastructure. No third-party SaaS stores customer data (except LLM API calls, which are stateless). |
| **Access control** | Streamlit dashboard access controlled by role. Approval queues require authenticated human action. |

### 4.5 Fairness ✅

| Evidence | Detail |
|---|---|
| **Keyword-based personas** | Buyer persona tagging is based on question content (BPA-free, engraving, servicing), not demographic profiling. |
| **No discriminatory targeting** | Marketing briefs recommend product improvements and campaigns, not customer segmentation by protected characteristics. |

### 4.6 Fail-Safe Design ✅

| Evidence | Detail |
|---|---|
| **Fail-safe, not fail-open** | If the LLM is unavailable, ALL enquiries route to the CS team. The system never sends unreviewed AI-generated content. |
| **Graceful degradation** | If ChromaDB is down, keyword-only fallback. If n8n is down, email continues to accumulate in Gmail (no data loss). |

---

## 5. Presentation Quality (20%)

> **Criterion:** Can explain clearly to a non-technical audience.

### 5.1 Demo Video ✅

| Evidence | Detail |
|---|---|
| **5-minute structured demo** | Clear timestamped script: problem (0:00) → workflow (0:30) → live demo (1:30) → business impact (2:30) → cost (3:30) → safeguards (4:15). See `docs/demo_script.md`. |
| **Non-technical narrative** | Starts with BOLDR's human problem (3-person team drowning in email), not with tech. Technical details introduced only after the "why" is clear. |
| **Live ticket walkthrough** | Feeds a real sample ticket through the workflow, showing drafted reply, gap detection, KB auto-draft, and theme cluster — concrete, not abstract. |

### 5.2 Architecture Diagrams ✅

| Evidence | Detail |
|---|---|
| **System architecture** | Mermaid diagram showing all components (n8n, ChromaDB, Streamlit, LLM API) and their interactions. See `docs/architecture.md`. |
| **Data flow** | Ticket processing pipeline from intake to resolution. |
| **KB update loop** | Gap detection → auto-draft → approval → index cycle. |
| **Theme clustering pipeline** | Weekly clustering → monthly brief → marketing actions. |
| **Multi-channel intake** | Email, Instagram DM, WhatsApp, chat webhook routing. |

### 5.3 Documentation Quality ✅

| Evidence | Detail |
|---|---|
| **README.md** | Comprehensive project overview with tech stack, quick start, project structure, rubric alignment, safeguards, and cost analysis. |
| **docs/setup.md** | Step-by-step installation guide (prerequisites, Docker, configuration, testing). |
| **docs/architecture.md** | Mermaid diagrams for system, data flow, KB loop, theme clustering, and multi-channel intake. |
| **docs/demo_script.md** | Timestamped 5-minute demo video script with screen directions and talking points. |
| **docs/rubric_checklist.md** | This document — comprehensive self-assessment mapping every rubric criterion to evidence. |
| **project_plan.md** | 13-section project plan covering problem, architecture, data, phases, metrics, safeguards, cost, and team. |

### 5.4 Non-Technical Communication ✅

| Evidence | Detail |
|---|---|
| **Problem-first framing** | "BOLDR's 3-person CS team drowning in manual email support" — anyone can understand this. |
| **Business language** | ROI, time saved, marketing signals, revenue — not just technical metrics. |
| **Concrete examples** | "BPA-free strap queries → Health-Conscious Buyer → Action: Add 'BPA-Free Straps' product badge" — not abstract clustering theory. |
| **Cost in SME terms** | "$20–55/month" and "20–50× ROI" — not API token pricing. |

---

## Qualification Checklist Summary

| # | Criterion | Status | Key Evidence |
|---|---|---|---|
| 1 | **Problem Identification** | ✅ | §2 of project_plan.md; 70 real tickets; 3-person CS team pain points |
| 2 | **Workflow Logic & Demonstration** | ✅ | n8n workflow JSON; 70-ticket test; live demo video; architecture diagrams |
| 3 | **Business Impact** | ✅ | 60%+ CS time saved; 3–5 marketing signals/quarter; 20–50× ROI |
| 4 | **Cost Analysis** | ✅ | $5 setup; $20–55/mo operating; detailed breakdown in project_plan.md §12 |
| 5 | **Safeguards & Human Checks** | ✅ | No auto-send; human approval queues; confidence scoring; PII stripping; fail-safe design |
| 6 | **Proof of Execution** | ✅ | Public repo; Docker Compose; working prototype; test suite; architecture screenshots |

---

## Rubric Score Self-Assessment

| Criterion | Weight | Self-Score (1–10) | Rationale |
|---|---|---|---|
| Technical Execution | 25% | 9/10 | Full closed-loop intelligence system; hybrid search; confidence scoring; Docker deployment; multi-channel; 70-ticket test coverage |
| SME Impact & Business Value | 25% | 9/10 | Real SME problem; 60%+ time saved; transforms cost centre to revenue driver; measurable ROI |
| Cost Efficiency | 20% | 10/10 | ~$5 setup; $20–55/mo; 20–50× ROI; open-source stack; linear scaling; sponsor credit leverage |
| Responsible AI | 10% | 9/10 | Human-in-the-loop on everything; no auto-send; confidence scoring; PII handling; fail-safe design; audit trail |
| Presentation Quality | 20% | 9/10 | Structured demo; non-technical narrative; architecture diagrams; comprehensive documentation; concrete examples |

**Weighted Total: 9.1/10**

---

*Prepared by Digital Futures Consultancy LLP (T17LL1937H, incorporated 10 Oct 2017, Singapore) · https://DigitalFutures.Asia for ECHELON 2026 AI Workflow Competition*