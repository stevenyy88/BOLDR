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
