# BOLDR Instagram DM Intake

## Overview
Receives Instagram DM messages via webhook, normalizes the data, forwards to the Intelligence Engine, and returns an immediate confirmation.

**Status:** ✅ Active  
**Nodes:** 4  
**Credentials:** No external credentials needed (all endpoints use FastAPI internal API)

## Workflow Steps

| # | Node | Type | Description |
|---|------|------|-------------|
| 1 | Instagram DM Webhook | webhook | Receives Instagram DM messages via webhook |
| 2 | Normalize Instagram Data | set | Maps Instagram DM payload to BOLDR intake schema |
| 3 | Forward to Intelligence Loop | httpRequest | POST normalized data to BOLDR Intelligence Engine (FastAPI) |
| 4 | Respond to Instagram | respondToWebhook | Returns immediate confirmation to Instagram |

## API Endpoints Used

- `POST /api/v1/intake`

## Testing

```bash
# Test the webhook
curl -X POST http://192.168.1.85:5678/webhook/instagram-dm \
  -H "Content-Type: application/json" \
  -d '{"message": "How much does the BOLDR Venture cost?", "channel": "chat", "sender_id": "test"}'
```

---
*Author: Steve Ng, Founder & CEO — Digital Futures Consultancy LLP (T17LL1937H) • DigitalFutures.Asia*

## Execution Demo Video

📹 `instagram_intake_execution_demo.mp4` — Step-by-step execution walkthrough showing real data flowing through each node.

### Real Test Results

**Input Message:** `Do you offer engraving services?`

**Classification Result:**
```json
{
  "ticket_id": "TKT-25129",
  "question_type": "engraving",
  "buyer_persona": "gifter",
  "confidence": 1.0,
  "is_answerable": true,
  "answerability_type": "kb_answerable",
  "escalation_required": false,
  "escalation_reason": null,
  "sop_routing": "Engraving Rate Card",
  "needs_shopify": false
}
```

**Final Response:**
```json
{
  "status": "received",
  "message": "Your Instagram message has been received. We'll respond shortly!"
}
```
