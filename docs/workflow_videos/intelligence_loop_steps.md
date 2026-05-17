# BOLDR Intelligence Loop

## Overview
The core intelligence pipeline: receives multi-channel messages, classifies intent and persona, searches the knowledge base, drafts BOLDR-brand replies, logs knowledge gaps, and returns a structured response.

**Status:** ✅ Active  
**Nodes:** 7  
**Credentials:** No external credentials needed (all endpoints use FastAPI internal API)

## Workflow Steps

| # | Node | Type | Description |
|---|------|------|-------------|
| 1 | Multi-Channel Intake Webhook | webhook | Receives POST requests from any channel (chat, WhatsApp, Instagram, email) |
| 2 | Normalize Intake Data | set | Maps incoming payload to BOLDR intake schema (message, channel, sender_id) |
| 3 | Process via Intelligence Engine | httpRequest | Classifies intent, persona, and answerability via FastAPI /api/v1/intake |
| 4 | Search Knowledge Base | httpRequest | Searches ChromaDB via FastAPI /api/v1/kb/search for relevant answers |
| 5 | Draft BOLDR Reply | httpRequest | Drafts a BOLDR-brand reply via FastAPI /api/v1/reply/draft |
| 6 | Log Knowledge Gap | httpRequest | Logs unanswered questions via FastAPI /api/v1/gap/log for self-improvement |
| 7 | Send Response | respondToWebhook | Returns structured response with ticket_id, classification, and status |

## API Endpoints Used

- `POST /api/v1/gap`
- `POST /api/v1/intake`
- `POST /api/v1/kb`
- `POST /api/v1/reply`

## Testing

```bash
# Test the webhook
curl -X POST http://192.168.1.85:5678/webhook/boldr-intake \
  -H "Content-Type: application/json" \
  -d '{"message": "How much does the BOLDR Venture cost?", "channel": "chat", "sender_id": "test"}'
```

---
*Author: Steve Ng, Founder & CEO — Digital Futures Consultancy LLP (T17LL1937H) • DigitalFutures.Asia*


## Execution Demo Video

📹 `intelligence_loop_execution_demo.mp4` — Step-by-step execution walkthrough showing real data flowing through each node.

### Live Test Results

**Input Message:** `How much does the BOLDR Venture cost?`

**Classification Result:**
```json
{
  "ticket_id": "TKT-72535",
  "question_type": "product_general",
  "buyer_persona": "prospect",
  "confidence": 1.0,
  "is_answerable": true,
  "answerability_type": "kb_answerable",
  "escalation_required": false,
  "escalation_reason": null,
  "sop_routing": "Product One-Pager + FAQ",
  "needs_shopify": false
}
```

**Final Response:**
```json
{
  "status": "processed",
  "ticket_id": "TKT-72535",
  "question_type": "product_general",
  "persona": "prospect",
  "is_answerable": false,
  "message": "Thank you for reaching out to BOLDR. Your message has been processed and our team will follow up within 24 hours."
}
```

**Key Insight:** The response message uses professional BOLDR brand voice — no exclamation marks, courteous and clear.
