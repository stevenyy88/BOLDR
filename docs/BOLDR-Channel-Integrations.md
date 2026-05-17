# BOLDR — Channel Integration Setup Guide

**Production-Level Setup for WhatsApp Business API, Instagram Graph API, and Gmail**

**Author:** Steve Ng, Founder and CEO — Digital Futures Consultancy LLP (T17LL1937H)  
**Date:** 2026-05-17  
**Status:** Competition Demo + Production Ready

---

## Overview

BOLDR's channel integration layer supports 4 customer channels: WhatsApp, Instagram, Email, and Chat. Each channel has a webhook receiver built into the FastAPI application that normalises incoming messages into a unified format and processes them through the intelligence loop.

**For the ECHELON competition demo**, all 5 n8n workflows use internal FastAPI webhooks — no external credentials required. The channel integration endpoints documented here are for **production deployment** when you connect real platform APIs.

**Architecture:**

```
WhatsApp/Instagram/Email Platform
        │
        │ (webhook POST)
        ▼
BOLDR FastAPI Channel Receiver
  /api/v1/channels/{channel}/webhook
        │
        │ (normalise)
        ▼
BOLDR Intelligence Loop
  /api/v1/intake
        │
        ▼
  Classify → Search KB → Draft Reply → Queue for Approval
```

---

## Prerequisites

| Requirement | Details |
|---|---|
| **Domain** | A public domain (e.g., `boldr.digitalfutures.asia`) with SSL certificate |
| **BOLDR API** | Running and accessible at `https://yourdomain.com` (port 443) |
| **Meta Business Account** | Required for both WhatsApp and Instagram (one account covers both) |
| **Meta Developer Account** | Required to create apps and configure webhooks |

---

## 1. WhatsApp Business API Setup

### 1.1 Create Meta Business Account

1. Go to [business.facebook.com](https://business.facebook.com)
2. Click **Create Account**
3. Enter business name: `BOLDR Supply Co` (or your business name)
4. Enter your name and business email
5. Complete verification (may require business documents)

### 1.2 Create Meta App

1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Click **My Apps** → **Create App**
3. Select **Business** as the app type
4. Enter app name: `BOLDR Customer Intelligence`
5. Enter your business email
6. Click **Create App**

### 1.3 Add WhatsApp Business API

1. In your Meta App dashboard, click **Add Product**
2. Find **WhatsApp** and click **Set Up**
3. You'll get a temporary access token and test phone number
4. Note down:
   - **Phone Number ID** (from WhatsApp > Phone Numbers)
   - **WhatsApp Business Account ID** (from WhatsApp > Settings)
   - **Access Token** (temporary, from WhatsApp > Settings)

### 1.4 Configure Webhook

1. In your Meta App dashboard, go to **WhatsApp** → **Configuration**
2. Click **Edit** next to **Webhook**
3. Enter your callback URL:
   ```
   https://yourdomain.com/api/v1/channels/whatsapp/webhook
   ```
4. Enter your verify token. This must match the `WHATSAPP_VERIFY_TOKEN` in your `.env` file:
   ```
   WHATSAPP_VERIFY_TOKEN=your_secure_random_token_here
   ```
   **Important:** Generate a secure random token for production, e.g.:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
5. Click **Verify and Save** — Meta will send a GET request with `hub.mode=subscribe&hub.challenge=XXX&hub.verify_token=your_secure_random_token_here`. BOLDR's endpoint will echo back the challenge string.
6. Subscribe to webhook fields:
   - ✅ `messages`
   - ✅ `message_status`

### 1.5 Test WhatsApp Integration

**Step 1: Verify webhook registration**

```bash
# Test the verification endpoint (Meta does this automatically)
curl -s "https://yourdomain.com/api/v1/channels/whatsapp/webhook?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=your_secure_random_token_here"
# Expected response: "test123"
```

**Step 2: Send a test message webhook**

```bash
curl -X POST https://yourdomain.com/api/v1/channels/whatsapp/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "object": "whatsapp_business_account",
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "6591234567",
            "type": "text",
            "text": {"body": "Are your straps BPA-free?"},
            "timestamp": "1705315853",
            "id": "wamid.HBgMNjU5MTIzNDU2Nw=="
          }],
          "contacts": [{
            "wa_id": "6591234567",
            "profile": {"name": "Caleb Tan"}
          }]
        }
      }]
    }]
  }'
```

**Expected response:**
```json
{
  "status": "processed",
  "messages": [
    {
      "message_id": "wamid.HBgMNjU5MTIzNDU2Nw==",
      "wa_id": "6591234567",
      "profile_name": "Caleb Tan",
      "text": "Are your straps BPA-free?",
      "status": "received"
    }
  ],
  "count": 1
}
```

**Step 3: Verify the message was processed through the intelligence loop**

```bash
# Check audit log for the processed ticket
curl -s "https://yourdomain.com/api/v1/audit/recent?limit=1" | python3 -m json.tool

# Check the approval queue for the drafted reply
curl -s "https://yourdomain.com/api/v1/queue/replies/pending" | python3 -m json.tool
```

### 1.6 WhatsApp Pricing

| Item | Cost |
|---|---|
| Meta Business Account | Free |
| WhatsApp Business API | Free (pay per conversation) |
| Per conversation (Singapore) | ~SGD 0.01–0.05 |
| 1,000 conversations/month | ~SGD 10–50 |
| **Estimated monthly for BOLDR** | **~SGD 15–30** |

---

## 2. Instagram Graph API Setup

### 2.1 Prerequisites

- Meta Business Account (same as WhatsApp — you already have this)
- An **Instagram Professional Account** (Business or Creator) linked to a **Facebook Page**
- Your Meta App (same one used for WhatsApp)

### 2.2 Link Instagram to Facebook Page

1. Go to [instagram.com](https://instagram.com) and log in to your business account
2. Go to **Settings** → **Account** → **Connected Accounts**
3. Connect to your Facebook Page
4. Or go to [business.facebook.com](https://business.facebook.com) → **Business Settings** → **Instagram Accounts** → **Add**

### 2.3 Add Instagram Graph API to Your App

1. In your Meta App dashboard, click **Add Product**
2. Find **Instagram** and click **Set Up**
3. Under **Instagram Login**, configure:
   - **Valid OAuth Redirect URIs:** `https://yourdomain.com/instagram/callback`
   - **Deauthorize Callback URL:** `https://yourdomain.com/instagram/deauthorize`
   - **Data Deletion Request URL:** `https://yourdomain.com/instagram/data-deletion`

### 2.4 Configure Instagram Webhook

1. In your Meta App dashboard, go to **Webhooks** → **Instagram**
2. Click **Add Callback URL**:
   ```
   https://yourdomain.com/api/v1/channels/instagram/webhook
   ```
3. Enter your verify token (same as WhatsApp or different):
   ```
   INSTAGRAM_VERIFY_TOKEN=your_secure_random_token_here
   ```
4. Subscribe to webhook fields:
   - ✅ `messages` (for Instagram DMs)

### 2.5 Test Instagram Integration

**Step 1: Verify webhook registration**

```bash
curl -s "https://yourdomain.com/api/v1/channels/instagram/webhook?hub.mode=subscribe&hub.challenge=ig_test_456&hub.verify_token=your_secure_random_token_here"
# Expected response: "ig_test_456"
```

**Step 2: Send a test Instagram DM webhook**

```bash
curl -X POST https://yourdomain.com/api/v1/channels/instagram/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "object": "instagram",
    "entry": [{
      "messaging": [{
        "sender": {"id": "ig_user_456"},
        "recipient": {"id": "ig_business_account"},
        "timestamp": 1705315853000,
        "message": {
          "mid": "m_abc123",
          "text": "Hey is the Expedition BPA-free?"
        }
      }]
    }]
  }'
```

**Expected response:**
```json
{
  "status": "processed",
  "messages": [
    {
      "message_id": "m_abc123",
      "sender_id": "ig_user_456",
      "text": "Hey is the Expedition BPA-free?",
      "status": "received"
    }
  ],
  "count": 1
}
```

**Step 3: Verify processing through the intelligence loop**

```bash
curl -s "https://yourdomain.com/api/v1/audit/recent?limit=1" | python3 -m json.tool
```

### 2.6 Instagram Pricing

| Item | Cost |
|---|---|
| Instagram Graph API | **Free** |
| Instagram DMs via API | **Free** |
| **Estimated monthly for BOLDR** | **SGD 0** |

---

## 3. Email (Gmail) Setup

You have two options for email integration: **IMAP polling** (simpler, no webhook needed) or **Mailgun webhook** (real-time, recommended for production).

### Option A: Gmail IMAP Polling (Simplest — No Additional Service)

#### 3A.1 Enable Gmail App Password

1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** if not already enabled
3. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
4. Create a new app password:
   - App name: `BOLDR Customer Intelligence`
   - Click **Create**
5. Copy the 16-character password (you won't see it again)

#### 3A.2 Configure Environment Variables

Add to your `.env` file:

```bash
# IMAP Configuration (Gmail)
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
IMAP_USERNAME=your_email@gmail.com
IMAP_PASSWORD=xxxx xxxx xxxx xxxx   # Your 16-char app password (no spaces)
```

#### 3A.3 Test IMAP Connection

```bash
curl -X POST http://localhost:8000/api/v1/channels/email/imap-fetch \
  -H "Content-Type: application/json" \
  -d '{
    "host": "imap.gmail.com",
    "port": 993,
    "username": "your_email@gmail.com",
    "password": "xxxx xxxx xxxx xxxx",
    "folder": "INBOX",
    "limit": 5,
    "mark_seen": true
  }'
```

**Expected response:**
```json
{
  "status": "fetched",
  "count": 3,
  "emails": [
    {
      "from": "Customer Name <customer@example.com>",
      "subject": "Question about BOLDR Expedition",
      "body": "Hi, I wanted to ask about...",
      "date": "Sun, 14 Jan 2026 10:30:00 +0800",
      "message_id": "<msg123@mail.gmail.com>",
      "thread_id": "<thread456@mail.gmail.com>"
    }
  ],
  "host": "imap.gmail.com",
  "folder": "INBOX"
}
```

#### 3A.4 Set Up Scheduled Polling with n8n

Create an n8n scheduled trigger that calls the IMAP fetch endpoint every 5 minutes:

1. Open n8n at `http://localhost:5678`
2. Create a new workflow: **BOLDR Gmail Poller**
3. Add node: **Schedule Trigger** → Every 5 minutes
4. Add node: **HTTP Request** → POST `http://boldr_app:8000/api/v1/channels/email/imap-fetch` (or `http://192.168.1.85:8000/api/v1/channels/email/imap-fetch` if app runs locally)
5. Add node: **HTTP Request** (for each email) → POST `http://boldr_app:8000/api/v1/channels/email/webhook` with the email data
6. Activate the workflow

**Note:** If using Docker, use `http://boldr_app:8000` (container name). If running locally, use `http://192.168.1.85:8000` (host IP).

### Option B: Mailgun Webhook (Recommended for Production — Real-Time)

#### 3B.1 Sign Up for Mailgun

1. Go to [mailgun.com](https://mailgun.com) and create an account
2. Add your domain (e.g., `mail.boldr.watch` or `mail.digitalfutures.asia`)
3. Verify domain ownership via DNS records

#### 3B.2 Configure Mailgun Route

1. Go to **Receiving** → **Routes** in Mailgun dashboard
2. Create a new route:
   - **Expression Type:** Match Recipient
   - **Recipient:** `support@yourdomain.com` (or `boldr@yourdomain.com`)
   - **Forward to:** `https://yourdomain.com/api/v1/channels/email/webhook`
   - **Priority:** 0
3. Save the route

#### 3B.3 Test Email Webhook

```bash
curl -X POST http://localhost:8000/api/v1/channels/email/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "from_email": "customer@example.com",
    "from_name": "Caleb Tan",
    "subject": "Are your straps BPA-free?",
    "body_text": "Hi, I wanted to ask if the Venture straps are BPA-free. I have sensitive skin.",
    "date": "2026-01-15T10:30:00+08:00",
    "message_id": "msg-456@mailgun.example.com"
  }'
```

**Expected response:**
```json
{
  "status": "received",
  "from": "customer@example.com",
  "subject": "Are your straps BPA-free?",
  "channel": "email",
  "normalised": {
    "message": "Are your straps BPA-free?\n\nHi, I wanted to ask if the Venture straps are BPA-free. I have sensitive skin.",
    "subject": "Are your straps BPA-free?",
    "channel": "email",
    "sender_id": "Caleb Tan <customer@example.com>",
    "sender_name": "Caleb Tan",
    "timestamp": "2026-01-15T10:30:00+08:00",
    "thread_id": "",
    "source_id": "msg-456@mailgun.example.com",
    "raw_payload": { ... }
  }
}
```

### 3.4 Email Pricing

| Option | Cost |
|---|---|
| **Gmail IMAP Polling** | **Free** (included with Google account) |
| **Mailgun** (5,000 emails/mo) | **Free tier** |
| **Mailgun** (production) | ~SGD 15/month |
| **SendGrid** (100 emails/day) | **Free tier** |
| **Postmark** (100 emails/mo) | **Free tier** |

---

## 4. Chat Widget Setup

The Chat channel is the simplest — it's a webhook that any chat widget can call.

### 4.1 Integration Point

```javascript
// Example: Add to your website's chat widget
fetch('https://yourdomain.com/api/v1/intake', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: userInput,
    channel: 'chat',
    sender_name: userName,
    sender_id: sessionId,
  })
})
.then(response => response.json())
.then(data => console.log('Ticket processed:', data));
```

### 4.2 Test Chat Integration

```bash
curl -X POST http://localhost:8000/api/v1/intake \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hi, I am looking for a gift for my dad. He likes rugged watches.",
    "channel": "chat",
    "sender_name": "Sarah"
  }'
```

**Expected response:**
```json
{
  "ticket_id": "TKT-XXXXX",
  "question_type": "product_recommendation",
  "buyer_persona": "gift_buyer",
  "confidence": 0.92,
  "is_answerable": true,
  "answerability_type": "kb_answerable",
  "escalation_required": false,
  "sop_routing": "Product Recommendation → Catalogue + Customisation Options",
  "needs_shopify": false
}
```

---

## 5. PII Stripping Configuration

### 5.1 Enable PII Stripping (Production)

When going live with real customer data, enable PII stripping to comply with PDPA (Singapore) and GDPR:

```bash
# In .env
PII_STRIP_ENABLED=true
```

### 5.2 PII Patterns Covered

| Pattern | Example Input | Redacted Output |
|---|---|---|
| **Email** | `john@example.com` | `[EMAIL_REDACTED]` |
| **SG Phone** | `+65 9123 4567` | `[PHONE_REDACTED]` |
| **International Phone** | `+1-234-567-8901` | `[PHONE_REDACTED]` |
| **NRIC/FIN** | `S1234567A` | `[NRIC_REDACTED]` |
| **Credit Card** | `4111 1111 1111 1111` | `[CARD_REDACTED]` |
| **SG Postal Code** | `018956` | `[POSTAL_REDACTED]` |
| **Name in Email** | `"John Doe" <john@example.com>` | `[NAME_REDACTED]` |
| **URL with PII** | `https://example.com?email=john@test.com` | `[URL_REDACTED]` |

### 5.3 Test PII Stripping

```bash
# With PII stripping enabled
curl -X POST "http://localhost:8000/api/v1/pii/strip?text=My+email+is+john%40example.com+and+my+phone+is+%2B65+9123+4567&enabled=true"

# Check status
curl http://localhost:8000/api/v1/pii/status

# In intake endpoint, PII is automatically stripped when PII_STRIP_ENABLED=true
curl -X POST http://localhost:8000/api/v1/intake \
  -H "Content-Type: application/json" \
  -d '{"message": "My email is john@example.com and my NRIC is S1234567A", "channel": "chat", "sender_name": "John"}'
```

### 5.4 Per-Request Override

Force PII stripping for a single request even when globally disabled:

```bash
# This works regardless of PI_STRIP_ENABLED setting
curl -X POST "http://localhost:8000/api/v1/pii/strip?enabled=true&text=My+email+is+test%40test.com"
```

---

## 6. SSL / HTTPS Setup (Required for Production Webhooks)

Meta (WhatsApp/Instagram) requires HTTPS webhooks. Here's the quickest setup:

### Option A: Cloudflare Tunnel (Free, No Domain Needed)

```bash
# Install cloudflared
brew install cloudflared   # macOS
# or: curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared

# Create a tunnel
cloudflared tunnel --url http://localhost:8000

# This gives you a URL like: https://random-name.trycloudflare.com
# Use this as your webhook URL
```

### Option B: Nginx + Let's Encrypt (Production)

```bash
# Install nginx and certbot
sudo apt install nginx certbot python3-certbot-nginx

# Create nginx config for BOLDR
sudo tee /etc/nginx/sites-available/boldr << 'EOF'
server {
    listen 80;
    server_name boldr.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/boldr /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d boldr.yourdomain.com

# Auto-renew
sudo certbot renew --dry-run
```

---

## 7. n8n Workflow Configuration for Production

Once your webhooks are registered with Meta, update the n8n workflow URLs:

### 7.1 Update n8n Webhook URLs

Currently, the n8n workflows call `http://192.168.1.85:8000/api/v1/intake`. For production, update to your public domain:

```bash
# Use the import script with --url flag
cd /path/to/BOLDR
python scripts/import_workflows.py --activate --force --base-url https://boldr.yourdomain.com
```

Or update manually in n8n:
1. Open each workflow in the n8n editor
2. Edit each HTTP Request node
3. Change the URL from `http://192.168.1.85:8000/api/v1/...` to `https://boldr.yourdomain.com/api/v1/...`
4. Save and activate

### 7.2 n8n Gmail Poller (Optional — for IMAP-based email)

If you chose Gmail IMAP (Option A), create a new n8n workflow:

1. **Schedule Trigger** → Every 5 minutes
2. **HTTP Request** → POST `http://boldr_app:8000/api/v1/channels/email/imap-fetch` (Docker) or `http://192.168.1.85:8000/api/v1/channels/email/imap-fetch` (local)
3. **Split In Batches** → Process each email
4. **HTTP Request** → POST `http://boldr_app:8000/api/v1/channels/email/webhook` with each email's data

---

## 8. Integration Testing Checklist

Use this checklist to confirm each channel is working end-to-end:

### WhatsApp ✅

- [ ] Meta Business Account created
- [ ] Meta App created with WhatsApp Business API product
- [ ] Webhook URL configured: `https://yourdomain.com/api/v1/channels/whatsapp/webhook`
- [ ] Verify token matches `.env` `WHATSAPP_VERIFY_TOKEN`
- [ ] GET verification returns challenge string
- [ ] POST webhook processes messages correctly
- [ ] Audit log shows WhatsApp tickets
- [ ] Approval queue shows drafted replies
- [ ] Test with real WhatsApp message

### Instagram ✅

- [ ] Instagram Professional Account linked to Facebook Page
- [ ] Instagram Graph API added to Meta App
- [ ] Webhook URL configured: `https://yourdomain.com/api/v1/channels/instagram/webhook`
- [ ] Verify token matches `.env` `INSTAGRAM_VERIFY_TOKEN`
- [ ] GET verification returns challenge string
- [ ] POST webhook processes DMs correctly
- [ ] Audit log shows Instagram tickets
- [ ] Approval queue shows drafted replies
- [ ] Test with real Instagram DM

### Gmail (IMAP) ✅

- [ ] Gmail 2FA enabled
- [ ] Gmail App Password created
- [ ] `.env` updated with `IMAP_HOST`, `IMAP_USERNAME`, `IMAP_PASSWORD`
- [ ] IMAP fetch returns emails successfully
- [ ] Emails normalised into BOLDR intake format
- [ ] Audit log shows email tickets
- [ ] n8n Gmail Poller workflow created and activated (if using IMAP)

### Gmail (Mailgun) ✅

- [ ] Mailgun account created and domain verified
- [ ] Route configured: `support@yourdomain.com` → `https://yourdomain.com/api/v1/channels/email/webhook`
- [ ] POST webhook processes emails correctly
- [ ] Audit log shows email tickets
- [ ] Approval queue shows drafted replies

### PII Stripping ✅

- [ ] `PII_STRIP_ENABLED=true` in `.env`
- [ ] `/api/v1/pii/status` returns `{"pii_stripping_enabled": true}`
- [ ] `/api/v1/pii/strip?enabled=true&text=...` strips PII correctly
- [ ] Intake endpoint strips PII from messages before classification
- [ ] Audit log shows PII-stripped versions

### SSL/HTTPS ✅

- [ ] Domain DNS configured (A record pointing to server IP)
- [ ] SSL certificate installed (Let's Encrypt or Cloudflare)
- [ ] `https://yourdomain.com/api/v1/health` returns `{"status": "healthy"}`
- [ ] Webhook verification works over HTTPS

---

## 9. Environment Variables Reference

Add these to your `.env` file for production:

```bash
# ============================================================
# Channel Integration (Production)
# ============================================================

# WhatsApp Business API
WHATSAPP_VERIFY_TOKEN=<your-secure-random-token>

# Instagram Graph API
INSTAGRAM_VERIFY_TOKEN=<your-secure-random-token>

# Gmail IMAP (for scheduled email polling)
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
IMAP_USERNAME=your_email@gmail.com
IMAP_PASSWORD=xxxx xxxx xxxx xxxx

# PII Stripping (enable for production)
PII_STRIP_ENABLED=true

# ============================================================
# SSL Configuration (Production)
# ============================================================
# If using a reverse proxy (nginx, cloudflare tunnel):
# APP_HOST=0.0.0.0
# APP_PORT=8000
# SSL is handled by the reverse proxy, not by FastAPI directly
```

---

## 10. Troubleshooting

### WhatsApp Webhook Verification Fails

| Symptom | Solution |
|---|---|
| `403 Forbidden` | Check that `WHATSAPP_VERIFY_TOKEN` in `.env` matches the token in Meta App Dashboard |
| `500 Internal Server Error` | Check FastAPI logs: `docker logs boldr_app` or `tail -f /tmp/boldr_api.log` |
| Meta doesn't send verification | Ensure your domain is publicly accessible with HTTPS |
| Verification succeeds but no messages arrive | Subscribe to `messages` webhook field in Meta App Dashboard |

### Instagram Webhook Not Receiving DMs

| Symptom | Solution |
|---|---|
| No DMs received | Ensure Instagram account is Professional (Business or Creator), not Personal |
| DMs arrive but empty | Check webhook field subscriptions — must subscribe to `messages` |
| `403 Forbidden` | Check `INSTAGRAM_VERIFY_TOKEN` matches Meta App Dashboard |

### Gmail IMAP Connection Failed

| Symptom | Solution |
|---|---|
| `IMAP login failed` | Use App Password (16 chars), not your regular Gmail password |
| `No emails fetched` | Check that `mark_seen=false` for testing (so you don't mark emails as read) |
| `Connection timeout` | Ensure your server can reach `imap.gmail.com:993` (check firewall) |

### PII Stripping Not Working

| Symptom | Solution |
|---|---|
| `pii_stripping_enabled: false` | Set `PII_STRIP_ENABLED=true` in `.env` and restart the server |
| PII still visible in audit log | PII is stripped before classification but original message may be in raw_payload |
| `/api/v1/pii/strip` returns unchanged text | Check that `?enabled=true` parameter is set (or `PII_STRIP_ENABLED=true` in `.env`) |

---

*Prepared by Digital Futures Consultancy LLP (T17LL1937H, incorporated 10 Oct 2017, Singapore) · https://DigitalFutures.Asia*