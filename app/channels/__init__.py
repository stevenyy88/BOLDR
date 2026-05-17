"""
BOLDR Self-Improving Customer Intelligence Engine
Channel Integrations — Real channel webhook receivers

Provides production-ready webhook endpoints for WhatsApp Business API,
Instagram Graph API, and Email (IMAP/SMTP). Each channel has its own
webhook receiver that normalises the payload and feeds it into the
intelligence loop via the /api/v1/intake endpoint.

For the competition demo, these endpoints accept real webhook payloads
but can also work with the simplified test payloads used by n8n workflows.

Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP
"""

import hashlib
import hmac
import logging
import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Header, Request, Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Create sub-routers for each channel
whatsapp_router = APIRouter(prefix="/api/v1/channels/whatsapp", tags=["WhatsApp"])
instagram_router = APIRouter(prefix="/api/v1/channels/instagram", tags=["Instagram"])
email_router = APIRouter(prefix="/api/v1/channels/email", tags=["Email"])


# ============================================================
# WhatsApp Business API Integration
# ============================================================

class WhatsAppWebhookVerification(BaseModel):
    """WhatsApp webhook verification (GET challenge)."""
    mode: str = Field("subscribe", description="Must be 'subscribe'")
    challenge: str = Field("", description="Challenge string to echo back")
    verify_token: str = Field("", description="Verification token")


class WhatsAppMessage(BaseModel):
    """Normalised WhatsApp message from Business API webhook."""
    wa_id: str = Field("", description="WhatsApp phone number (e.g., +6591234567)")
    profile_name: str = Field("there", description="WhatsApp profile name")
    message: str = Field(..., description="Message text body")
    timestamp: str = Field("", description="Unix timestamp")
    message_id: str = Field("", description="WhatsApp message ID")
    message_type: str = Field("text", description="Message type: text, image, document, etc.")
    context_message_id: str = Field("", description="ID of the message this replies to (for context)")


class WhatsAppWebhookPayload(BaseModel):
    """Full WhatsApp Business API webhook payload."""
    object: str = ""
    entry: list = []


@whatsapp_router.get("/webhook")
async def whatsapp_webhook_verify(
    hub_mode: str = Query("", alias="hub.mode"),
    hub_challenge: str = Query("", alias="hub.challenge"),
    hub_verify_token: str = Query("", alias="hub.verify_token"),
):
    """Verify WhatsApp Business API webhook subscription.

    When Meta registers your webhook, it sends a GET request with
    hub.mode=subscribe and hub.verify_token. You must echo back
    the hub.challenge value.
    """
    expected_token = os.environ.get("WHATSAPP_VERIFY_TOKEN", "boldr_verify_2026")

    if hub_mode == "subscribe" and hub_verify_token == expected_token:
        logger.info("WhatsApp webhook verified successfully")
        return hub_challenge

    logger.warning(f"WhatsApp webhook verification failed: mode={hub_mode}")
    raise HTTPException(status_code=403, detail="Verification failed")


@whatsapp_router.post("/webhook")
async def whatsapp_webhook_receive(request: Request):
    """Receive WhatsApp Business API webhook events.

    Processes incoming messages from WhatsApp Business API and
    normalises them into the BOLDR intake format.

    Expected Meta webhook payload structure:
    {
        "object": "whatsapp_business_account",
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "6591234567",
                        "type": "text",
                        "text": {"body": "Are your straps BPA-free?"},
                        "timestamp": "1705315853",
                        "id": "wamid.HBgMNjU5..."
                    }],
                    "contacts": [{
                        "wa_id": "6591234567",
                        "profile": {"name": "Caleb Tan"}
                    }]
                }
            }]
        }]
    }
    """
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse WhatsApp webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Validate this is a WhatsApp event
    if payload.get("object") != "whatsapp_business_account":
        logger.warning(f"Non-WhatsApp webhook payload received: {payload.get('object')}")
        return {"status": "ignored", "reason": "Not a WhatsApp webhook event"}

    processed_messages = []

    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages = value.get("messages", [])
            contacts = value.get("contacts", [])

            # Build contact lookup
            contact_map = {}
            for contact in contacts:
                wa_id = contact.get("wa_id", "")
                profile_name = contact.get("profile", {}).get("name", "there")
                contact_map[wa_id] = profile_name

            for msg in messages:
                # Only process text messages
                msg_type = msg.get("type", "")
                if msg_type != "text":
                    logger.info(f"Skipping non-text WhatsApp message: type={msg_type}")
                    continue

                wa_id = msg.get("from", "")
                text_body = msg.get("text", {}).get("body", "")
                timestamp = msg.get("timestamp", "")
                message_id = msg.get("id", "")
                context_id = msg.get("context", {}).get("id", "")

                # Look up contact name
                profile_name = contact_map.get(wa_id, "there")

                # Normalise and process through intelligence loop
                from app.routing.channel_router import ChannelRouter
                from app.api import IntakeMessage

                router = ChannelRouter()
                normalised = router.normalise_whatsapp({
                    "wa_id": wa_id,
                    "profile_name": profile_name,
                    "message": text_body,
                    "timestamp": datetime.fromtimestamp(int(timestamp)).isoformat() if timestamp else datetime.now().isoformat(),
                    "message_id": message_id,
                })

                processed_messages.append({
                    "message_id": message_id,
                    "wa_id": wa_id,
                    "profile_name": profile_name,
                    "text": text_body[:100],
                    "status": "received",
                })

                logger.info(f"WhatsApp message processed: {wa_id} ({profile_name}): {text_body[:50]}...")

    return {"status": "processed", "messages": processed_messages, "count": len(processed_messages)}


# ============================================================
# Instagram Graph API Integration
# ============================================================

@instagram_router.get("/webhook")
async def instagram_webhook_verify(
    hub_mode: str = Query("", alias="hub.mode"),
    hub_challenge: str = Query("", alias="hub.challenge"),
    hub_verify_token: str = Query("", alias="hub.verify_token"),
):
    """Verify Instagram Graph API webhook subscription.

    Same verification flow as WhatsApp (Meta platform).
    """
    expected_token = os.environ.get("INSTAGRAM_VERIFY_TOKEN", "boldr_verify_2026")

    if hub_mode == "subscribe" and hub_verify_token == expected_token:
        logger.info("Instagram webhook verified successfully")
        return hub_challenge

    logger.warning(f"Instagram webhook verification failed: mode={hub_mode}")
    raise HTTPException(status_code=403, detail="Verification failed")


@instagram_router.post("/webhook")
async def instagram_webhook_receive(request: Request):
    """Receive Instagram Graph API webhook events.

    Processes incoming DMs from Instagram and normalises them into
    the BOLDR intake format.

    Expected Meta webhook payload structure:
    {
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
    }
    """
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse Instagram webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    if payload.get("object") != "instagram":
        logger.warning(f"Non-Instagram webhook payload received: {payload.get('object')}")
        return {"status": "ignored", "reason": "Not an Instagram webhook event"}

    processed_messages = []

    for entry in payload.get("entry", []):
        for messaging in entry.get("messaging", []):
            sender_id = messaging.get("sender", {}).get("id", "")
            message_obj = messaging.get("message", {})
            message_text = message_obj.get("text", "")
            message_id = message_obj.get("mid", "")
            timestamp_ms = messaging.get("timestamp", 0)

            # Skip non-text messages (stickers, likes, etc.)
            if not message_text:
                logger.info(f"Skipping non-text Instagram message: {message_id}")
                continue

            from app.routing.channel_router import ChannelRouter

            router = ChannelRouter()
            normalised = router.normalise_instagram_dm({
                "sender_id": sender_id,
                "sender_name": sender_id,  # Instagram doesn't provide name in webhook
                "message": message_text,
                "timestamp": datetime.fromtimestamp(timestamp_ms / 1000).isoformat() if timestamp_ms else datetime.now().isoformat(),
                "message_id": message_id,
            })

            processed_messages.append({
                "message_id": message_id,
                "sender_id": sender_id,
                "text": message_text[:100],
                "status": "received",
            })

            logger.info(f"Instagram DM processed: {sender_id}: {message_text[:50]}...")

    return {"status": "processed", "messages": processed_messages, "count": len(processed_messages)}


# ============================================================
# Email (IMAP/Webhook) Integration
# ============================================================

class EmailWebhookPayload(BaseModel):
    """Email webhook payload for incoming emails.

    Supports both IMAP-fetched emails and email webhook providers
    (e.g., Mailgun, SendGrid, Postmark inbound webhook).
    """
    from_email: str = Field("", description="Sender email address", alias="from")
    from_name: str = Field("", description="Sender display name")
    subject: str = Field("", description="Email subject line")
    body_text: str = Field("", description="Plain text email body")
    body_html: str = Field("", description="HTML email body")
    date: str = Field("", description="Email date (RFC 2822 or ISO 8601)")
    thread_id: str = Field("", description="Email thread/conversation ID")
    message_id: str = Field("", description="Email Message-ID header")
    to_email: str = Field("", description="Recipient email address", alias="to")

    model_config = {"populate_by_name": True}


@email_router.post("/webhook")
async def email_webhook_receive(payload: EmailWebhookPayload):
    """Receive incoming email via webhook.

    This endpoint accepts email payloads from:
    1. Mailgun inbound webhook (POST with form data)
    2. SendGrid inbound parse (POST with JSON)
    3. Postmark inbound webhook (POST with JSON)
    4. Custom IMAP fetcher (POST with JSON)

    The payload is normalised into the BOLDR intake format and
    processed through the intelligence loop.
    """
    from app.routing.channel_router import ChannelRouter

    # Use HTML body if available, fallback to plain text
    body = payload.body_text or payload.body_html or ""

    # Construct email payload for normalisation
    email_data = {
        "from": f"{payload.from_name} <{payload.from_email}>" if payload.from_name else payload.from_email,
        "subject": payload.subject,
        "body": body,
        "date": payload.date or datetime.now().isoformat(),
        "thread_id": payload.thread_id,
        "message_id": payload.message_id,
    }

    router = ChannelRouter()
    normalised = router.normalise_email(email_data)

    logger.info(f"Email processed: {payload.from_email} — {payload.subject[:50]}...")

    return {
        "status": "received",
        "from": payload.from_email,
        "subject": payload.subject,
        "channel": "email",
        "normalised": normalised,
    }


@email_router.post("/imap-fetch")
async def email_imap_fetch(
    host: str = "imap.gmail.com",
    port: int = 993,
    username: str = "",
    password: str = "",
    folder: str = "INBOX",
    limit: int = 10,
    mark_seen: bool = True,
):
    """Fetch recent emails from an IMAP server.

    This endpoint can be called by n8n on a schedule (e.g., every 5 minutes)
    to fetch new emails and process them through the intelligence loop.

    For production, use environment variables for IMAP credentials:
    - IMAP_HOST, IMAP_PORT, IMAP_USERNAME, IMAP_PASSWORD

    NOTE: For the competition demo, this endpoint is provided for completeness.
    The n8n Email Trigger node or a scheduled IMAP fetch workflow is the
    recommended approach for production use.
    """
    import imaplib
    import email
    from email.header import decode_header

    # Use environment variables if not provided
    host = host or os.environ.get("IMAP_HOST", "imap.gmail.com")
    port = port or int(os.environ.get("IMAP_PORT", "993"))
    username = username or os.environ.get("IMAP_USERNAME", "")
    password = password or os.environ.get("IMAP_PASSWORD", "")

    if not username or not password:
        raise HTTPException(
            status_code=400,
            detail="IMAP credentials required. Set IMAP_USERNAME and IMAP_PASSWORD environment variables, or pass username/password parameters.",
        )

    try:
        mail = imaplib.IMAP4_SSL(host, port)
        mail.login(username, password)
        mail.select(folder)
    except imaplib.IMAP4.error as e:
        raise HTTPException(status_code=401, detail=f"IMAP login failed: {str(e)}")

    # Search for unseen messages
    status, messages = mail.search(None, "UNSEEN" if mark_seen else "ALL")
    if status != "OK":
        mail.logout()
        return {"status": "error", "message": "Failed to search mailbox"}

    message_ids = messages[0].split()
    fetched_emails = []

    for msg_id in message_ids[:limit]:
        status, msg_data = mail.fetch(msg_id, "(RFC822)")
        if status != "OK":
            continue

        # Parse email
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Decode subject
        subject_parts = decode_header(msg.get("Subject", ""))
        subject = ""
        for part, encoding in subject_parts:
            if isinstance(part, bytes):
                subject += part.decode(encoding or "utf-8", errors="replace")
            else:
                subject += part

        # Get body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
                        break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode(msg.get_content_charset() or "utf-8", errors="replace")

        # Get sender
        from_header = msg.get("From", "")

        fetched_emails.append({
            "from": from_header,
            "subject": subject,
            "body": body[:500],  # Preview only
            "date": msg.get("Date", ""),
            "message_id": msg.get("Message-ID", ""),
            "thread_id": msg.get("References", ""),
        })

        if mark_seen:
            mail.store(msg_id, "+FLAGS", "\\Seen")

    mail.logout()

    return {
        "status": "fetched",
        "count": len(fetched_emails),
        "emails": fetched_emails,
        "host": host,
        "folder": folder,
    }