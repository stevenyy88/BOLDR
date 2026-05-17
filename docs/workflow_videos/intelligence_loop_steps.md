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
