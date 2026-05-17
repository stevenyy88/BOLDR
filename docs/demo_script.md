# BOLDR — 5-Minute Demo Video Script

**Project:** BOLDR — Self-Improving Customer Intelligence Engine  
**Track:** REVENUE ROCKET — Sales, Marketing, and Customer Acquisition  
**Author:** Steve Ng, Founder and CEO — Digital Futures Consultancy LLP (T17LL1937H)  
**Date:** 2026-05-17  
**Duration:** 5:00 (300 seconds)

---

## Segment 1: Problem Statement (0:00–0:30)

**Duration:** 30 seconds

### On Screen
- Title card: "BOLDR — Self-Improving Customer Intelligence Engine"
- Subtitle: "Digital Futures Consultancy LLP | ECHELON 2026"
- Key metrics: 70 tickets/day, 4 channels, 3-person CS team, 0 marketing feedback

### Narration
> "Meet BOLDR — a Singapore watch micro-brand with a 3-person customer service team. They handle 70+ customer enquiries per day across Gmail, Instagram DMs, WhatsApp, and live chat. Every ticket starts from zero. There's no feedback loop from support to marketing. The questions customers ask — about BPA-free straps, vegan materials, corporate gifting — these are revenue signals that are currently invisible."

> "We built BOLDR — not a chatbot, but a self-improving intelligence engine that gets smarter with every ticket."

---

## Segment 2: Architecture & Tech Stack (0:30–1:15)

**Duration:** 45 seconds

### On Screen
- Architecture diagram: 4 channels → n8n → FastAPI Intelligence Engine → ChromaDB + GLM-5.1
- Tech stack: n8n (workflow), FastAPI (API), ChromaDB (vector store), GLM-5.1 via Ollama (LLM), all-MiniLM-L6-v2 (embeddings), Streamlit (dashboard)

### Narration
> "The architecture is simple and powerful. Customer enquiries from any channel — chat, WhatsApp, Instagram, email — hit an n8n webhook. n8n normalises the message and forwards it to the Intelligence Engine."

> "The engine classifies intent, tags the buyer persona, searches the knowledge base, and either drafts a professional reply or detects a knowledge gap. Every gap feeds back into the KB. Every theme cluster generates marketing signals."

> "The entire stack is self-hosted. No external API keys. No OAuth credentials. Zero vendor lock-in."

---

## Segment 3: Live Workflow Demo (1:15–3:30)

**Duration:** 2 minutes 15 seconds

### On Screen
- Step-by-step execution of all 5 n8n workflows with real data

### 3a: Chat Intake (1:15–1:35)
- POST to /webhook/chat with a real customer message
- n8n receives, normalises, forwards to Intelligence Engine
- Response: ticket_id, question_type, buyer_persona, is_answerable, confidence
- Professional BOLDR response: "Thank you for reaching out to BOLDR..."

### 3b: WhatsApp Intake (1:35–1:55)
- POST to /webhook/whatsapp
- Same intelligence loop, WhatsApp-specific normalisation
- Response includes full classification output

### 3c: Instagram DM Intake (1:55–2:15)
- POST to /webhook/instagram-dm
- Instagram message format
- Full intelligence output returned

### 3d: Email Intake (2:15–2:35)
- POST to /webhook/email
- Email with subject line
- Webhook-based intake (no Gmail OAuth required)

### 3e: Intelligence Loop (2:35–3:30)
- POST to /webhook/boldr-intake with a materials_safety question
- Step-by-step: webhook → normalise → classify intent → classify persona → KB search → draft reply → log gap → respond
- Show the professional BOLDR reply in brand voice
- Show gap detection for unanswered questions
- Show theme clustering output

---

## Segment 4: Dashboard & Self-Improvement Loop (3:30–4:15)

**Duration:** 45 seconds

### On Screen
- Streamlit dashboard: Live Pipeline, Theme Analysis, KB Management, Gap Log, Marketing Brief
- KB search: live query returning results from ChromaDB
- Theme clustering: visualisation of customer enquiry themes
- Marketing brief: prioritised action items with revenue signals

### Narration
> "The Streamlit dashboard gives BOLDR's CS team full visibility. Live pipeline stats show how many tickets were processed, by channel, by intent, and by persona."

> "Every knowledge gap is logged with its theme and persona. Every theme cluster surfaces marketing signals — BPA-free straps for health-conscious buyers, vegan materials for sustainability advocates, corporate gifting for prospects."

> "And the self-improvement loop: when a gap is resolved, the system auto-drafts a KB entry for one-click human approval. The knowledge base gets smarter. Future tickets on the same topic get answered automatically."

---

## Segment 5: Business Impact & ROI (4:15–4:45)

**Duration:** 30 seconds

### On Screen
- ROI metrics: 9 hrs/week saved, SGD 1,080/month CS savings, 19-49× ROI
- Setup cost: SGD 600-800
- Operating cost: SGD 22-57/month
- Revenue recovery: SGD 3,000-5,000/month

### Narration
> "The numbers speak for themselves. 9 hours per week saved. Over SGD 1,000 per month in CS time savings alone. Setup costs under SGD 800. Monthly operating costs between SGD 22 and 57. That's a 19 to 49 times return on investment."

> "And the revenue impact: faster response times convert more product enquiries into sales. Marketing signals from support data unlock new customer segments. This turns a cost centre into a revenue driver."

---

## Segment 6: Closing (4:45–5:00)

**Duration:** 15 seconds

### On Screen
- "BOLDR — Self-Improving Customer Intelligence Engine"
- "Every unanswered question makes the system smarter. Every ticket closes the loop."
- Zero credentials. Self-hosted. Self-improving.
- Steve Ng, Founder & CEO — Digital Futures Consultancy LLP (T17LL1937H)
- https://DigitalFutures.Asia

### Narration
> "BOLDR. Every unanswered question makes the system smarter. Every ticket closes the loop. Self-hosted, zero credentials, and self-improving by design."

> "Thank you."

---

## Key Differentiators to Emphasise

1. **Zero External Credentials** — All 5 workflows use internal FastAPI HTTP endpoints. No OAuth. No API keys. No vendor lock-in.
2. **Self-Improving Loop** — Knowledge gaps auto-generate KB drafts. The system gets smarter with every ticket.
3. **Professional Brand Voice** — All responses use courteous, professional language. No exclamation marks. No screaming.
4. **Human-in-the-Loop** — Every drafted reply requires human approval. No auto-send. Fail-safe, not fail-open.
5. **Marketing Signals** — Theme clustering surfaces revenue opportunities from support data that would otherwise be invisible.
6. **19-49× ROI** — SGD 22-57/month operating cost. SGD 1,080/month in CS savings alone.

## Competition Rubric Mapping

| Rubric Criterion | Video Segment | Evidence |
|---|---|---|
| Technical Execution (25%) | Segments 2-3 | 5 active n8n workflows, 13/13 e2e tests passing, 70/70 tickets processed |
| SME Impact & Business Value (25%) | Segment 5 | 9 hrs/week saved, SGD 1,080/mo savings, 19-49× ROI |
| Innovation (25%) | Segments 3e-4 | Self-improving KB loop, marketing signals from support data |
| Presentation Quality (25%) | All segments | Professional narration, step-by-step demos, architecture diagrams |