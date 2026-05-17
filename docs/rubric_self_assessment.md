# BOLDR — ECHELON 2026 Rubric Self-Assessment

**Project:** BOLDR — Self-Improving Customer Intelligence Engine  
**Track:** REVENUE ROCKET — Sales, Marketing, and Customer Acquisition  
**Author:** Steve Ng, Founder and CEO — Digital Futures Consultancy LLP (T17LL1937H)  
**Repo:** https://github.com/stevenyy88/BOLDR  
**Date:** 2026-05-17  

---

## Executive Summary

BOLDR is a **self-improving customer intelligence engine** that transforms a 3-person CS team's reactive email support into a closed-loop intelligence system. It classifies every customer enquiry by intent and buyer persona, searches a knowledge base for answers, drafts professional replies for human approval, detects knowledge gaps, auto-drafts KB entries, clusters themes into weekly reports, and generates monthly marketing briefs — all without manual effort.

**31 API endpoints. 9 dashboard tabs. 5 n8n workflows. 4 channel integrations. 13/13 e2e tests. Zero external credentials.**

---

## Criterion 1: Technical Execution (25%)

> *"The workflow works, is stable, and realistically deployable by the SME."*

### Features Implemented

| # | Feature | Value for Judges | Evidence |
|---|---------|-----------------|----------|
| 1 | **5 n8n workflows, all ACTIVE** | Full multi-channel intake — Chat, WhatsApp, Instagram DM, Email — orchestrated end-to-end | `n8n/workflows/*.json`, all verified with 200 OK responses |
| 2 | **31 REST API endpoints** | Comprehensive intelligence loop API covering every function: intake, classification, KB search, reply drafting, gap detection, Shopify lookup, approval queue, audit log, theme clustering, PII stripping, channel webhooks | `app/api.py`, Swagger UI at `/docs` |
| 3 | **Real channel integrations** | Production-ready webhook receivers for WhatsApp Business API, Instagram Graph API, and Email (Mailgun/SendGrid/Postmark + IMAP). Meta verification endpoints included. Judges can test these with real webhook payloads. | `app/channels/__init__.py`, tested with curl |
| 4 | **Hybrid classification** | LLM (GLM-5.1:cloud) with rule-based fallback. 88.6% intent accuracy, 85.7% persona accuracy on 70-ticket test set. Never fails open — always produces a classification. | `app/classifier/`, `app/tests/test_e2e.py` |
| 5 | **Confidence scoring** | Every classification includes a confidence score (0–1). Below threshold (0.5) → CS escalation, not fabrication. Prevents hallucination-based responses. | `app/classifier/intent.py`, `/api/v1/intake` response |
| 6 | **Docker Compose deployment** | All 3 services in Docker: boldr_app (FastAPI + Streamlit via supervisord), ChromaDB, n8n. Single `docker compose up -d` to start. Health checks on all services. | `docker-compose.yml`, `app/Dockerfile` |
| 7 | **Token bucket rate limiting** | 3 tiers: intake (2/sec, 15 burst), general (5/sec, 30 burst), stats (10/sec, 60 burst). X-RateLimit headers on every response. 429 with Retry-After when exceeded. | `app/middleware/rate_limit.py` |
| 8 | **SQLite audit log** | Every classification decision persisted with timestamp, confidence, channel, intent, persona, routing. 3 endpoints: `/audit/recent`, `/audit/summary`, `/audit/ticket/{id}`. | `app/audit/audit_log.py`, `data/boldr_audit.db` |
| 9 | **SQLite approval queue** | Every drafted reply persisted for human review. Approve/reject via API or Streamlit dashboard. | `app/queue/approval_queue.py`, `data/boldr_queue.db` |
| 10 | **13/13 e2e tests passing** | Full test coverage: question types, buyer personas, answerability, escalation, channel distribution, SOP routing, Shopify detection, gap classification, theme clustering, tone guidelines, knowledge gaps, persona taxonomy. | `app/tests/test_e2e.py` |
| 11 | **Shopify product lookup** | Simulated product catalogue (3 watch models, 5 strap types, engraving, servicing, orders). In production, replace with Shopify Storefront API. | `app/shopify/product_lookup.py` |
| 12 | **PII stripping (configurable)** | 8 regex patterns covering Singapore and international formats: email, phone (SG + intl), NRIC/FIN, credit card, postal code, name-in-email, URL-with-PII. Default OFF for competition, ON for production. | `app/privacy/pii_strip.py`, `PII_STRIP_ENABLED` in `.env` |
| 13 | **Fail-safe design** | If LLM unavailable → all tickets route to CS team. No auto-send. Confidence below threshold → escalation. ChromaDB down → keyword fallback. | `app/classifier/intent.py`, `app/routing/channel_router.py` |

### Technical Execution Score: **9.5/10**

Rationale: Full closed-loop intelligence system with real channel webhooks, Dockerised deployment, rate limiting, audit logging, PII stripping, confidence scoring, 31 endpoints, and 13/13 tests. Only gap: no automated CI/CD pipeline and no load testing.

---

## Criterion 2: SME Impact & Business Value (25%)

> *"Addresses a real SME problem with measurable value."*

### Features Implemented

| # | Feature | Value for Judges | Evidence |
|---|---------|-----------------|----------|
| 1 | **Real BOLDR data** | 70 actual support tickets from BOLDR Supply Co. across 7 question types, 4 channels, and 7 buyer personas. Not synthetic. | `dataset/tickets.json`, `app/tests/test_e2e.py` |
| 2 | **3-person CS team pain point** | System designed for a team of 3, not an enterprise call centre. Every feature is accessible to non-technical CS staff via Streamlit dashboard and n8n visual editor. | `project_plan.md` §2, `docs/demo_script.md` |
| 3 | **60%+ CS time saved** | Auto-drafts replies for 50/70 answerable tickets. 36 hours/month freed (3 staff × 20 hrs × 60%). CS team focuses on escalations, not repetitive enquiries. | `/api/v1/stats`, Dashboard KPI cards |
| 4 | **Marketing signals unlocked** | Theme clustering surfaces revenue signals: BPA-free straps (Health-Conscious Buyer), vegan materials (Sustainability Advocate), corporate gifting (bulk pricing). These are currently invisible to marketing. | `app/intelligence/theme_clusterer.py`, `/api/v1/themes/weekly` |
| 5 | **Cost centre → revenue driver** | Transforms customer support from a pure cost into an intelligence source. Monthly brief generates 3–5 actionable campaign ideas per quarter. | `/api/v1/themes/monthly-brief` |
| 6 | **KB gap closure loop** | Every unresolved ticket generates an auto-drafted KB entry. Knowledge gaps get systematically closed, reducing future manual handling. | `app/intelligence/gap_detector.py`, `/api/v1/kb/auto-draft` |
| 7 | **Quantified ROI** | SGD 1,080/mo CS savings, SGD 22-57/mo operating cost, 19-49× ROI. Setup cost SGD 600-800. | `README.md`, `project_plan.md` §12 |
| 8 | **Dashboard KPI cards** | 5 executive metrics: Tickets Processed, KB Answer Rate, CS Time Saved (~9 hrs/wk, 60% reduction), Monthly Savings (SGD 1,080), ROI (19-49×). Gives SME managers an instant business impact snapshot. | `app/dashboard/app.py` |
| 9 | **Professional BOLDR brand voice** | All drafted responses use courteous, professional language — no exclamation marks, no informality. Matches BOLDR's brand identity. | `app/generator/reply.py`, `app/routing/sop_parser.py` |

### SME Impact Score: **9/10**

Rationale: Real BOLDR data, quantified ROI, transforms cost centre to revenue driver. Marketing signals from support data is genuinely novel. Revenue recovery estimates (SGD 3,000-5,000/mo) are industry assumptions, not BOLDR-specific data.

---

## Criterion 3: Cost Efficiency (20%)

> *"Commercially realistic, deployable, and scalable."*

### Features Implemented

| # | Feature | Value for Judges | Evidence |
|---|---------|-----------------|----------|
| 1 | **~SGD 5 setup cost** | Only cost is initial LLM API tokens for testing. All software is open-source. Docker Compose runs on any VPS. | `project_plan.md` §12 |
| 2 | **SGD 22-57/month operating** | n8n (free), ChromaDB (free), Streamlit (free), FastAPI (free). Only cost is LLM API calls at SGD 0.01-0.03 per classification. | `project_plan.md` §12 |
| 3 | **19-49× ROI** | SGD 1,080/mo CS savings on SGD 22-57/mo operating cost. Even at 10× ticket volume, still under SGD 300/mo. | `README.md` |
| 4 | **Fully open-source stack** | n8n, ChromaDB, FastAPI, Streamlit, sentence-transformers — no per-operation SaaS fees. No vendor lock-in. | `docker-compose.yml`, `app/requirements.txt` |
| 5 | **Self-hosted LLM** | Ollama GLM-5.1:cloud via local inference. No per-token API costs for primary classification. OpenAI-compatible API means easy model swap. | `app/classifier/intent.py`, `.env` |
| 6 | **Linear cost scaling** | LLM cost is SGD 0.01-0.03 per ticket. Even 10× volume = SGD 100-300/mo — still less than 1 CS staff salary. | `project_plan.md` §12 |
| 7 | **Docker Compose one-command deploy** | `docker compose up -d` starts everything. No Python, no Node.js, no manual installs. Health checks auto-restart failed services. | `docker-compose.yml` |
| 8 | **Supervisord for dual processes** | FastAPI + Streamlit in one container. One Docker image, one service, one health check. | `app/Dockerfile` |
| 9 | **CPU-only PyTorch** | Multi-stage Docker build uses CPU-only PyTorch (~2-3GB image vs ~10GB with CUDA). Runs on any VPS without GPU. | `app/Dockerfile` |

### Cost Efficiency Score: **9.5/10**

Rationale: Extremely lean cost structure. Open-source stack, self-hosted LLM, linear scaling. Docker Compose makes deployment trivial. Only gap: GLM-5.1:cloud model name suggests cloud dependency, but it runs on local Ollama.

---

## Criterion 4: Responsible AI (10%)

> *"Safe, reliable, fair, transparent, and compliant."*

### Features Implemented

| # | Feature | Value for Judges | Evidence |
|---|---------|-----------------|----------|
| 1 | **Human-in-the-loop on everything** | No auto-send. Every drafted reply queued for human approval in Streamlit dashboard. No reply is sent without explicit human action. | `app/queue/approval_queue.py`, `/api/v1/queue/replies/pending` |
| 2 | **KB approval workflow** | Auto-drafted KB entries require 1-click human approval before being indexed. Full version history with diff view and rollback. | `/api/v1/queue/kb`, `/api/v1/queue/kb/{id}/approve` |
| 3 | **Confidence scoring** | Default threshold 0.5. Below this → CS escalation with pre-filled draft, not fabrication. | `app/classifier/intent.py`, `/api/v1/intake` response |
| 4 | **PII stripping (configurable)** | 8 regex patterns covering GDPR/PDPA-required PII types. Configurable via `PII_STRIP_ENABLED` in `.env` (default OFF for demo, ON for production). Per-request override with `?enabled=true`. | `app/privacy/pii_strip.py`, `/api/v1/pii/strip`, `/api/v1/pii/status` |
| 5 | **SQLite audit log** | Every classification decision persisted with timestamp, confidence, channel, intent, persona, and routing. 3 queryable endpoints. | `app/audit/audit_log.py`, `/api/v1/audit/*` |
| 6 | **Fail-safe, not fail-open** | LLM unavailable → all tickets route to CS. ChromaDB down → keyword fallback. n8n down → 503 retryable. System never sends unreviewed AI content. | `app/routing/channel_router.py`, `app/classifier/intent.py` |
| 7 | **Escalation rules** | SOP-derived escalation triggers: angry customers, chargebacks, warranty >10 days, corporate >5 units, press enquiries. Always route to human CS. | `app/routing/channel_router.py` |
| 8 | **Source attribution** | Every drafted reply cites the KB source (FAQ entry, product spec, rate card). CS team can verify before sending. | `app/generator/reply.py` |
| 9 | **Rate limiting** | Token bucket prevents API abuse. Intake endpoints: 2/sec sustained. 429 with Retry-After header. | `app/middleware/rate_limit.py` |
| 10 | **Keyword-based personas** | Buyer persona tagging based on question content (BPA-free, engraving, servicing), not demographic profiling. No discriminatory targeting. | `app/classifier/persona.py` |
| 11 | **Data minimisation** | Only ticket intent and persona tags are persisted in audit log. Raw email bodies are not stored beyond processing. PII stripping available when enabled. | `app/audit/audit_log.py`, `app/privacy/pii_strip.py` |

### Responsible AI Score: **9/10**

Rationale: Comprehensive HITL, confidence scoring, audit trail, PII stripping, and fail-safe design. Gaps: no bias/fairness testing across persona groups, no data retention policy (how long is data kept), PII stripping is off by default.

---

## Criterion 5: Presentation Quality (20%)

> *"Can explain clearly to a non-technical audience."*

### Features Implemented

| # | Feature | Value for Judges | Evidence |
|---|---------|-----------------|----------|
| 1 | **Comprehensive README** | 31-endpoint API reference, 2 deployment modes (Docker + venv), cost analysis, architecture overview, project structure, business metrics. | `README.md` |
| 2 | **Architecture docs with Mermaid** | System architecture, data flow, KB update loop, theme clustering, multi-channel intake. All as Mermaid diagrams. | `docs/architecture.md` |
| 3 | **Demo script** | Timestamped 5-minute walkthrough: problem → workflow → live demo → business impact → cost → safeguards. | `docs/demo_script.md` |
| 4 | **Interactive demo script** | `scripts/record_demo.sh` — 7-section script with curl commands for every endpoint. Judges can run this to see the system in action. | `scripts/record_demo.sh` |
| 5 | **Swagger UI** | 31 endpoints documented at `http://localhost:8000/docs` with request/response schemas. | FastAPI auto-generated |
| 6 | **9-tab Streamlit dashboard** | Live Pipeline, Approval Queue, Ticket Timeline, Channel Analytics, Theme Analysis, KB Management, Gap Log, Marketing Brief, Audit Log. KPI cards showing business metrics. | `app/dashboard/app.py` |
| 7 | **Problem-first narrative** | "BOLDR's 3-person CS team drowning in manual email support" — anyone can understand this. Technical details introduced only after the "why" is clear. | `docs/demo_script.md`, `README.md` |
| 8 | **Business language** | ROI, time saved, marketing signals, revenue — not just technical metrics. Concrete examples: "BPA-free strap queries → Health-Conscious Buyer → Action: Add 'BPA-Free Straps' product badge". | `README.md`, `project_plan.md` |
| 9 | **Concrete examples** | Every claim backed by data: 70 tickets, 93 KB chunks, 88.6% intent accuracy, 85.7% persona accuracy, SGD 1,080/mo savings, 19-49× ROI. | `app/tests/test_e2e.py`, `/api/v1/stats` |
| 10 | **Self-assessment document** | This document — honest scoring with specific evidence for every claim. | `docs/rubric_self_assessment.md` |

### Presentation Quality Score: **8.5/10**

Rationale: Comprehensive documentation, interactive demo script, 31-endpoint Swagger UI, and 9-tab dashboard. Gap: no live screen recording video showing n8n executing in real-time. PIL flowcharts are diagrams, not actual n8n canvas screenshots.

---

## Summary Scorecard

| Criterion | Weight | Score | Weighted | Key Strengths | Key Gaps |
|---|--------|-------|----------|---------------|-----------|
| Technical Execution | 25% | 9.5/10 | 2.38 | 31 endpoints, real channel webhooks, Dockerised, PII stripping, rate limiting, audit log | No CI/CD, no load testing |
| SME Impact & Business Value | 25% | 9.0/10 | 2.25 | Real BOLDR data, quantified ROI, marketing signals, CS time savings | Revenue recovery estimates are industry assumptions |
| Cost Efficiency | 20% | 9.5/10 | 1.90 | SGD 5 setup, SGD 22-57/mo, 19-49× ROI, open-source, linear scaling | GLM-5.1:cloud naming suggests cloud dependency |
| Responsible AI | 10% | 9.0/10 | 0.90 | HITL, confidence scoring, PII stripping, audit trail, fail-safe | No bias testing, no data retention policy, PII default OFF |
| Presentation Quality | 20% | 8.5/10 | 1.70 | 31-endpoint Swagger, 9-tab dashboard, interactive demo script, business language | No live n8n screen recording video |

**Total Weighted Score: 9.13/10**

---

## What Makes BOLDR Stand Out

1. **It's not a chatbot.** It's a closed-loop intelligence system that classifies, answers, detects gaps, auto-updates KB, clusters themes, and generates marketing briefs — without manual effort.

2. **Zero external credentials.** Every n8n workflow uses internal FastAPI HTTP endpoints. No Gmail OAuth, no Google Sheets API, no WhatsApp Business API keys required for the demo. Real webhook receivers are ready for production.

3. **Self-improving.** Every ticket makes the system smarter. Knowledge gaps auto-draft KB entries. Theme clusters surface marketing signals. The monthly brief turns customer support data into revenue intelligence.

4. **Human-in-the-loop on everything.** No auto-send. Every reply requires human approval. Every KB entry requires human approval. Confidence scores prevent low-quality matches from reaching customers.

5. **31 API endpoints.** Not a demo hack — a production-grade API with rate limiting, audit logging, PII stripping, approval queues, and real channel integrations.

6. **Deployable with one command.** `docker compose up -d` starts everything. Health checks auto-restart. Supervisord keeps both FastAPI and Streamlit running.

7. **19-49× ROI.** SGD 1,080/mo in CS time savings on SGD 22-57/mo operating cost. That's not theoretical — it's based on 70 real BOLDR tickets and a SGD 28/hr blended CS rate.

---

## Features Checklist (for Quick Reference)

### Intelligence Loop
- [x] Multi-channel intake (Chat, WhatsApp, Instagram, Email)
- [x] LLM-powered intent classification (7 question types)
- [x] LLM-powered persona tagging (7 buyer personas)
- [x] Hybrid classification (LLM + rule-based fallback)
- [x] Confidence scoring (0–1, threshold 0.5)
- [x] KB search (ChromaDB vector + keyword hybrid)
- [x] Professional reply drafting in BOLDR brand voice
- [x] Knowledge gap detection (true gaps vs. Shopify lookups)
- [x] KB auto-drafting for gaps
- [x] Theme clustering (weekly reports)
- [x] Marketing intelligence briefs (monthly)
- [x] SOP-derived escalation routing

### Channel Integration
- [x] WhatsApp Business API webhook (Meta verification + message processing)
- [x] Instagram Graph API webhook (Meta verification + DM processing)
- [x] Email inbound webhook (Mailgun/SendGrid/Postmark compatible)
- [x] IMAP email fetcher (for scheduled polling)
- [x] Chat widget webhook
- [x] All channels normalise into unified BOLDR intake format

### API & Infrastructure
- [x] 31 REST API endpoints across 12 functional groups
- [x] Token bucket rate limiting (3 tiers, X-RateLimit headers)
- [x] SQLite audit log (every classification decision persisted)
- [x] SQLite approval queue (reply + KB approval with persistence)
- [x] Shopify product lookup (simulated, production-ready interface)
- [x] PII stripping (8 patterns, configurable, GDPR/PDPA)
- [x] Docker Compose deployment (3 services with health checks)
- [x] Multi-stage Dockerfile (supervisord for FastAPI + Streamlit)
- [x] Two deployment modes (Docker Compose or venv)

### Dashboard
- [x] 9 tabs: Live Pipeline, Approval Queue, Ticket Timeline, Channel Analytics, Theme Analysis, KB Management, Gap Log, Marketing Brief, Audit Log
- [x] KPI cards (Tickets Processed, KB Answer Rate, CS Time Saved, Monthly Savings, ROI)
- [x] Live data from FastAPI endpoints
- [x] Auto-refresh toggle (10-second intervals)

### Testing & Quality
- [x] 13/13 e2e tests passing (70-ticket coverage)
- [x] 93 KB document chunks from 5 source files
- [x] Professional BOLDR brand voice (no exclamation marks)
- [x] Swagger UI at `/docs` with full request/response schemas
- [x] Interactive demo script (`scripts/record_demo.sh`)

---

*Prepared by Digital Futures Consultancy LLP (T17LL1937H, incorporated 10 Oct 2017, Singapore) · https://DigitalFutures.Asia for ECHELON 2026 AI Workflow Competition*