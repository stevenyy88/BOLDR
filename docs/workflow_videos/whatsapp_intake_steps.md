# BOLDR WhatsApp Intake

## Overview
Receives WhatsApp messages via webhook, normalizes the data, forwards to the Intelligence Engine, and returns an immediate confirmation.

**Status:** ✅ Active  
**Nodes:** 4  
**Credentials:** No external credentials needed (all endpoints use FastAPI internal API)

## Workflow Steps

| # | Node | Type | Description |
|---|------|------|-------------|
| 1 | WhatsApp Webhook | webhook | Receives WhatsApp messages via webhook |
| 2 | Normalize WhatsApp Data | set | Maps WhatsApp payload to BOLDR intake schema |
| 3 | Forward to Intelligence Loop | httpRequest | POST normalized data to BOLDR Intelligence Engine (FastAPI) |
| 4 | Respond to WhatsApp | respondToWebhook | Returns immediate confirmation to WhatsApp |

## API Endpoints Used

- `POST /api/v1/intake`

## Testing

```bash
# Test the webhook
curl -X POST http://192.168.1.85:5678/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"message": "How much does the BOLDR Venture cost?", "channel": "chat", "sender_id": "test"}'
```

---
*Author: Steve Ng, Founder & CEO — Digital Futures Consultancy LLP (T17LL1937H) • DigitalFutures.Asia*


## Execution Demo Video

📹 `whatsapp_intake_execution_demo.mp4` — Step-by-step execution walkthrough showing real data flowing through each node.

### Live Test Results

**Input Message:** `My BOLDR Expedition is not keeping time accurately`

**Classification Result:**
```json
{
  "ticket_id": "TKT-76701",
  "question_type": "servicing",
  "buyer_persona": "owner_aftercare",
  "confidence": 0.95,
  "is_answerable": true,
  "answerability_type": "kb_answerable",
  "escalation_required": false,
  "escalation_reason": null,
  "sop_routing": "Servicing Rate Card",
  "needs_shopify": false
}
```

**Final Response:**
```json
{
  "ticket_id": "TKT-76701",
  "question_type": "servicing",
  "buyer_persona": "owner_aftercare",
  "confidence": 0.95,
  "is_answerable": false,
  "answerability_type": "no",
  "escalation_required": false,
  "escalation_reason": null,
  "sop_routing": "Servicing Rate Card",
  "needs_shopify": false
}
```

**Key Insight:** The response message uses professional BOLDR brand voice — no exclamation marks, courteous and clear.
