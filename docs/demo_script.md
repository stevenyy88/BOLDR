# BOLDR — 5-Minute Demo Video Script

**Project:** BOLDR — Self-Improving Customer Intelligence Engine  
**Track:** REVENUE ROCKET — Sales, Marketing, and Customer Acquisition  
**Author:** Steve Ng, Founder and CEO — Digital Futures Consultancy LLP  
**Date:** 2026-05-17  
**Duration:** 5:00 (300 seconds)

---

## Segment 1: Problem Statement (0:00–0:30)

**Duration:** 30 seconds

### 🖥️ On Screen
- Title card: "BOLDR — Self-Improving Customer Intelligence Engine"
- Subtitle: "Digital Futures Consultancy LLP | ECHELON 2026"
- BOLDR watch product image
- Infographic: 3-person CS team, 70 tickets, 4 channels, 0 marketing feedback

### 🗣️ Narration

> "Meet BOLDR — a Singapore watch micro-brand with a 3-person customer service team. They're drowning in manual email support across Gmail, Instagram DMs, WhatsApp, and live chat. Every enquiry is handled by hand. Their knowledge base is updated inconsistently. And critically — there's zero feedback loop from support to marketing. The questions customers ask — about BPA-free straps, vegan materials, corporate gifting — these are revenue signals that are currently invisible to the business."

### 🔄 Transition
> "So we built BOLDR — not a chatbot, but a self-improving intelligence engine that gets smarter with every ticket."

**[CUT TO: Architecture diagram]**

---

## Segment 2: Workflow Logic Walkthrough (0:30–1:30)

**Duration:** 60 seconds

### 🖥️ On Screen
- Animated system architecture diagram (from `docs/architecture.md`)
- Highlight each step as it's narrated:
  1. Multi-channel intake (Email, Instagram DM, WhatsApp, Chat)
  2. Intent extraction + persona classification
  3. Hybrid KB search (ChromaDB vector + keyword)
  4. Decision: answer found → draft reply; no answer → gap detection
  5. Human approval queue
  6. KB auto-draft for gaps → human approval → index
  7. Weekly theme clustering → monthly marketing brief

### 🗣️ Narration

> "Here's how BOLDR works. It's a 7-step closed-loop intelligence system, orchestrated by n8n.

> Step 1 — Multi-channel intake. Tickets come in from Gmail, Instagram DMs, WhatsApp, and chat webhooks. n8n triggers on each channel.

> Step 2 — Classification. Every ticket is classified by intent — what they're asking — and tagged with a buyer persona — who they are. Seven personas: Health-Conscious, Gifter, Enthusiast, Niche Buyer, Owner Aftercare, Prospect, and Transactional.

> Step 3 — Knowledge Base search. We use hybrid retrieval: vector search through ChromaDB for semantic matching, with keyword fallback for exact matches like model names and prices.

> Step 4 — The decision point. If the KB has an answer, we draft a reply in BOLDR's brand voice. If it doesn't, we flag it as a knowledge gap. Critically, we distinguish between 'needs Shopify data' — like order tracking — and 'needs a new KB entry' — like questions about vegan straps.

> Step 5 — Human approval. Every drafted reply goes to a queue. No auto-send. Ever.

> Step 6 — KB auto-update. When a gap is resolved by CS, we auto-draft a KB entry for one-click human approval. The knowledge base literally fixes itself.

> Step 7 — Intelligence output. Weekly theme clustering groups emerging questions. Monthly marketing briefs surface actionable signals — with specific campaign recommendations tagged by buyer persona."

### 🔄 Transition
> "Let's see this in action with a real ticket."

**[CUT TO: Live n8n workflow + Streamlit dashboard]**

---

## Segment 3: Live Demo with a Sample Ticket (1:30–2:30)

**Duration:** 60 seconds

### 🖥️ On Screen
- Split screen: n8n workflow editor (left) + Streamlit dashboard (right)
- Feed a sample ticket through the workflow in real-time

**Sample ticket (choose one from dataset):**

> **Subject:** "BPA-free strap options for Expedition?"  
> **Channel:** Instagram DM  
> **Buyer persona:** Health-Conscious  
> **Content:** "Hi, I love the Expedition but I'm very particular about materials. Are your straps BPA-free? I have a nickel allergy too — any hypoallergenic options?"

### 🗣️ Narration

> "Let's trace a real ticket through the system. A customer messages BOLDR on Instagram asking about BPA-free straps and hypoallergenic options.

> The workflow ingests the message via n8n's Instagram trigger. Within milliseconds, the classifier tags this as 'materials_safety' intent and 'health_conscious' persona.

> The retriever searches the knowledge base — FAQ entries on materials, product specs for the Expedition, and rate cards. It finds relevant matches with high confidence.

> The reply drafter generates a response in BOLDR's brand voice — friendly but direct, never promising what we're not sure about — citing the specific KB sources. This is what the CS agent sees in the approval queue.

> [Switch to Streamlit dashboard showing the drafted reply]

> The CS agent reviews it, approves, and the reply is sent. Total time from intake to queued draft: under 10 seconds. What used to take 15–20 minutes of manual lookup now takes a 30-second review.

> Now let's see what happens when the KB doesn't have an answer."

**[CUT TO: Gap detection demo]**

> "Here's a ticket asking about magnetic field resistance for MRI environments. The retriever returns a low confidence score — 0.32 — below our threshold. The system correctly flags this as a knowledge gap, routes it to CS with a pre-filled draft, and auto-drafts a KB entry template for when the team resolves it.

> [Show gap detection and KB auto-draft in Streamlit]

> This is the closed loop: every unanswered question feeds back into the system, making it smarter for the next time."

### 🔄 Transition
> "But BOLDR doesn't just answer tickets — it turns them into revenue signals."

**[CUT TO: Business impact slide]**

---

## Segment 4: Business Impact (2:30–3:30)

**Duration:** 60 seconds

### 🖥️ On Screen
- Animated infographic:
  - Before: CS team drowning in email, 0 marketing feedback
  - After: 60%+ CS time saved, automated marketing signals
- Revenue signal table (from project_plan.md §9)
- Monthly marketing brief mockup

### 🗣️ Narration

> "Here's the business impact. BOLDR's CS team saves 60% or more of their time — that's 36 hours per month freed from repetitive email handling. But the real value goes beyond time savings.

> Every week, the theme clusterer groups emerging questions. Every month, it produces a marketing brief with specific actions.

> [Show theme cluster visualisation]

> Let me give you three concrete examples:

> First — BPA-free strap queries keep appearing from Health-Conscious Buyers. The brief recommends: add a 'BPA-Free' product badge and launch a targeted campaign. That's a new customer segment.

> Second — Vegan material questions come from Sustainability Advocates. The brief flags: create a 'Vegan-Friendly' strap collection page. First-mover advantage in a growing niche.

> Third — Corporate gifting questions from multiple personas. The brief suggests: build a bulk pricing page. Higher average order value.

> [Show monthly brief mockup with persona tags and action items]

> These signals were invisible before. BOLDR's customer support was a cost centre. Now it's a revenue intelligence engine — and the loop keeps improving itself."

### 🔄 Transition
> "Now, what does all this cost?"

**[CUT TO: Cost analysis slide]**

---

## Segment 5: Cost Analysis (3:30–4:15)

**Duration:** 45 seconds

### 🖥️ On Screen
- Cost breakdown table:
  - Setup: ~$5
  - Monthly: $20–55
  - ROI: 20–50×
- Comparison chart: BOLDR engine vs. hiring additional CS staff
- Stack comparison: Our open-source stack vs. SaaS alternatives (Make + GPT-4o + Pinecone = $150–650/mo)

### 🗣️ Narration

> "The entire system costs about five dollars to set up and twenty to fifty-five dollars per month to run.

> Setup is essentially free — n8n, ChromaDB, and Streamlit are all open-source and run in Docker. The only setup cost is a few dollars in LLM API tokens for initial testing.

> Monthly operating cost: five to ten dollars for a VPS, ten to thirty for GLM-5.1 API calls, and five to fifteen for Claude as a fallback on low-confidence edge cases — which is only about 5% of tickets. Embeddings run locally. Zero cost.

> Compare that to SaaS alternatives: Make.com plus GPT-4o plus Pinecone would cost one hundred fifty to six hundred fifty dollars per month — and sends your customer data to third parties. Our stack keeps everything on BOLDR's infrastructure.

> The ROI? BOLDR saves thirty-six hours per month of CS time — valued at over a thousand dollars — for twenty to fifty-five dollars in monthly cost. That's a twenty to fifty times return on investment.

> This is commercially realistic for any SME. And it scales linearly — even at ten times the ticket volume, you're still under three hundred dollars a month."

### 🔄 Transition
> "Finally, let's talk about the safeguards that make this responsible AI."

**[CUT TO: Safeguards slide]**

---

## Segment 6: Safeguards & Proof of Execution (4:15–5:00)

**Duration:** 45 seconds

### 🖥️ On Screen
- Safeguards infographic:
  - 🔒 Human-in-the-loop: every reply requires approval
  - 🚫 No auto-send: system never sends without human sign-off
  - 🎯 Confidence scoring: low confidence = escalation, not fabrication
  - 🔐 PII handling: customer data stripped before processing
  - 🛡️ Fail-safe: LLM down → all tickets route to CS
- Proof of execution:
  - GitHub repo URL
  - `docker compose up -d` screenshot
  - Test suite passing

### 🗣️ Narration

> "Responsible AI isn't an afterthought — it's built into every layer.

> First — human-in-the-loop. Every drafted reply goes to an approval queue. No auto-send. Ever. The CS team always has final say.

> Second — no hallucination. When the knowledge base doesn't have an answer, we don't fabricate one. We flag the gap, route it to CS, and auto-draft a KB entry template for when it's resolved. The system admits what it doesn't know.

> Third — confidence scoring. Every retrieval result has a confidence score. Below 0.5, it escalates with a pre-filled draft — saving CS time even on hard cases.

> Fourth — privacy. Customer PII is stripped before theme clustering. Raw email bodies aren't stored. Data stays on BOLDR's infrastructure.

> And fifth — fail-safe design. If the LLM goes down, every enquiry routes to the CS team. The system fails safely, not silently.

> [Show GitHub repo and Docker Compose]

> Everything is public — the repo, the Docker Compose, the test results. One command to start the entire system. This is real, deployable, and owned by BOLDR's team.

> BOLDR isn't a chatbot. It's a self-improving intelligence engine that transforms customer support from a cost centre into a revenue driver — and it gets smarter with every ticket.

> Thank you."

**[END CARD]**

- GitHub repo URL
- "Digital Futures Consultancy LLP | ECHELON 2026"
- BOLDR logo

---

## Production Notes

### Recording Setup
- **Screen recording:** n8n workflow editor + Streamlit dashboard
- **Camera:** Presenter in corner (optional — vlog style)
- **Resolution:** 1920×1080 minimum
- **Audio:** External mic recommended; noise-free environment

### Assets Needed
| Asset | Source |
|---|---|
| BOLDR product images | Challenge brief or boldrsupply.co |
| Architecture diagram (animated) | `docs/architecture.md` — render Mermaid to animated sequence |
| Streamlit dashboard screenshots | Local `docker compose up` |
| n8n workflow screenshots | Local n8n editor |
| Monthly brief mockup | Generate from theme clusterer output |
| Cost comparison chart | `project_plan.md` §12 data |

### Tips
- Practice live demo segment multiple times; have a backup recording in case of latency
- Keep on-screen text minimal — let narration carry the story
- Use real data from the 70-ticket dataset, not synthetic examples
- Emphasise "no auto-send" and "human approval" early — judges value responsible AI
- End with the GitHub repo URL visible for 5+ seconds

---

*Prepared by Digital Futures Consultancy LLP for ECHELON 2026 AI Workflow Competition*