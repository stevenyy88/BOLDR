# BOLDR Chat Intake

## Overview
Receives chat messages from the BOLDR website/app widget, normalizes the data, forwards to the Intelligence Engine, and returns an immediate confirmation.

**Status:** ✅ Active  
**Nodes:** 4  
**Credentials:** No external credentials needed (all endpoints use FastAPI internal API)

## Workflow Steps

| # | Node | Type | Description |
|---|------|------|-------------|
| 1 | Chat Webhook | webhook | Receives chat messages from BOLDR website/app widget |
| 2 | Normalize Chat Data | set | Maps chat widget payload to BOLDR intake schema |
| 3 | Forward to Intelligence Loop | httpRequest | POST normalized data to BOLDR Intelligence Engine (FastAPI) |
| 4 | Respond to Chat Widget | respondToWebhook | Returns immediate confirmation to the chat widget |

## API Endpoints Used

- `POST /api/v1/intake`

## Testing

```bash
# Test the webhook
curl -X POST http://192.168.1.85:5678/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How much does the BOLDR Venture cost?", "channel": "chat", "sender_id": "test"}'
```

---
*Author: Steve Ng, Founder & CEO — Digital Futures Consultancy LLP (T17LL1937H) • DigitalFutures.Asia*


## Execution Demo Video

📹 `chat_intake_execution_demo.mp4` — Step-by-step execution walkthrough showing real data flowing through each node.

### Live Test Results

**Input Message:** `Hi, I am interested in the BOLDR Venture watch. How much does it cost?`

**Classification Result:**
```json
{
  "ticket_id": "TKT-61834",
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
  "status": "received",
  "ticket_id": "TKT-61834",
  "message": "Thank you for reaching out to BOLDR. Our team has received your message and will respond within 24 hours."
}
```

**Key Insight:** The response message uses professional BOLDR brand voice — no exclamation marks, courteous and clear.
