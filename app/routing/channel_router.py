"""
BOLDR Self-Improving Customer Intelligence Engine
Channel Router — Multi-channel intake normalisation and routing

Author: Steve Ng, Founder and CEO - Digital Futures Consultancy LLP
"""

import logging
import re
from datetime import datetime
from typing import Optional

from app.kb.schemas import Channel

logger = logging.getLogger(__name__)


class ChannelRouter:
    """Normalises multi-channel intake messages into a common schema
    and routes them to the appropriate processing pipeline.

    BOLDR receives customer messages from 4 channels:
    - Email (Gmail)
    - Instagram DM
    - WhatsApp
    - Chat (website widget)

    Each channel has different payload formats. This module normalises
    them into a unified BOLDRIntakeMessage format.
    """

    # Escalation keyword detection (from SOP Section 7)
    ESCALATION_KEYWORDS = [
        "chargeback", "refund", "angry", "furious", "unacceptable",
        "complaint", "lawyer", "legal", "sue", "report", "bbb",
        "better business bureau", "negative review", "social media",
    ]

    # Corporate/bulk order detection
    CORPORATE_KEYWORDS = [
        "bulk", "corporate", "wholesale", "large order", "team",
        "company", "business", "gifts for", "employee", "partner",
        "volume discount", "5 units", "10 units", "corporate@",
    ]

    def normalise_email(self, payload: dict) -> dict:
        """Normalise a Gmail/IMAP email payload.

        Expected payload keys: from, subject, body, date, thread_id, message_id
        """
        sender_email = payload.get("from", "")
        sender_name = self._extract_name_from_email(sender_email)
        subject = payload.get("subject", "")
        body = payload.get("body", "")
        thread_id = payload.get("thread_id", "")
        message_id = payload.get("message_id", "")

        return {
            "message": f"{subject}\n\n{body}" if subject else body,
            "subject": subject,
            "channel": "email",
            "sender_id": sender_email,
            "sender_name": sender_name,
            "timestamp": payload.get("date", datetime.now().isoformat()),
            "thread_id": thread_id,
            "source_id": message_id,
            "raw_payload": payload,
        }

    def normalise_instagram_dm(self, payload: dict) -> dict:
        """Normalise an Instagram DM webhook payload.

        Expected payload keys: sender_id, sender_name, message, timestamp, message_id
        """
        return {
            "message": payload.get("message", ""),
            "subject": "",
            "channel": "instagram_dm",
            "sender_id": payload.get("sender_id", ""),
            "sender_name": payload.get("sender_name", "there"),
            "timestamp": payload.get("timestamp", datetime.now().isoformat()),
            "thread_id": payload.get("sender_id", ""),
            "source_id": payload.get("message_id", ""),
            "raw_payload": payload,
        }

    def normalise_whatsapp(self, payload: dict) -> dict:
        """Normalise a WhatsApp webhook payload.

        Expected payload keys: wa_id, profile_name, message, timestamp, message_id
        """
        return {
            "message": payload.get("message", ""),
            "subject": "",
            "channel": "whatsapp",
            "sender_id": payload.get("wa_id", ""),
            "sender_name": payload.get("profile_name", "there"),
            "timestamp": payload.get("timestamp", datetime.now().isoformat()),
            "thread_id": payload.get("wa_id", ""),
            "source_id": payload.get("message_id", ""),
            "raw_payload": payload,
        }

    def normalise_chat(self, payload: dict) -> dict:
        """Normalise a website chat widget payload.

        Expected payload keys: session_id, user_name, message, timestamp
        """
        return {
            "message": payload.get("message", ""),
            "subject": "",
            "channel": "chat",
            "sender_id": payload.get("session_id", ""),
            "sender_name": payload.get("user_name", "there"),
            "timestamp": payload.get("timestamp", datetime.now().isoformat()),
            "thread_id": payload.get("session_id", ""),
            "source_id": payload.get("session_id", ""),
            "raw_payload": payload,
        }

    def normalise(self, payload: dict, channel: str) -> dict:
        """Normalise any channel payload into the common BOLDR schema.

        Args:
            payload: Raw channel-specific payload.
            channel: One of 'email', 'instagram_dm', 'whatsapp', 'chat'.

        Returns:
            Normalised message dict with: message, subject, channel,
            sender_id, sender_name, timestamp, thread_id, source_id.
        """
        normalisers = {
            "email": self.normalise_email,
            "instagram_dm": self.normalise_instagram_dm,
            "whatsapp": self.normalise_whatsapp,
            "chat": self.normalise_chat,
        }

        normaliser = normalisers.get(channel)
        if not normaliser:
            logger.error(f"Unknown channel: {channel}")
            raise ValueError(f"Unsupported channel: {channel}. Supported: {list(normalisers.keys())}")

        return normaliser(payload)

    def detect_escalation(self, message: str) -> tuple[bool, Optional[str]]:
        """Detect if a message needs immediate escalation.

        From SOP Section 7: escalate when customer is angry/threatening,
        chargeback risk, media enquiry, or corporate/bulk order.

        Args:
            message: The normalised message text.

        Returns:
            Tuple of (needs_escalation, reason).
        """
        message_lower = message.lower()

        # Check for escalation keywords
        for keyword in self.ESCALATION_KEYWORDS:
            if keyword in message_lower:
                return True, f"Escalation keyword detected: '{keyword}'"

        # Check for corporate/bulk order
        for keyword in self.CORPORATE_KEYWORDS:
            if keyword in message_lower:
                return True, f"Corporate/bulk enquiry detected: '{keyword}'"

        return False, None

    def route(self, normalised_message: dict) -> dict:
        """Route a normalised message to the appropriate processing pipeline.

        Args:
            normalised_message: Normalised message dict from normalise().

        Returns:
            Routing dict with pipeline, priority, and escalation status.
        """
        # Check for escalation
        message = normalised_message.get("message", "")
        needs_escalation, esc_reason = self.detect_escalation(message)

        if needs_escalation:
            return {
                "pipeline": "human_escalation",
                "priority": "high",
                "escalation": True,
                "escalation_reason": esc_reason,
                "auto_draft": False,
            }

        # All non-escalated messages go through the standard intelligence loop
        return {
            "pipeline": "intelligence_loop",
            "priority": "normal",
            "escalation": False,
            "escalation_reason": None,
            "auto_draft": True,
        }

    def _extract_name_from_email(self, email_str: str) -> str:
        """Extract display name from email string.

        Handles formats like:
        - "John Doe <john@example.com>" → "John Doe"
        - "john@example.com" → "there"
        """
        match = re.match(r'"?([^"<]+)"?\s*(?:<.+>)?', email_str)
        if match and match.group(1).strip():
            name = match.group(1).strip()
            if "@" not in name and name.lower() not in ("unknown", "noreply"):
                return name
        return "there"


if __name__ == "__main__":
    router = ChannelRouter()

    # Test email normalisation
    email_payload = {
        "from": "Caleb Tan <caleb@example.com>",
        "subject": "Strap dye safety",
        "body": "Hi, are your BPA-free straps also nickel-free? I have sensitive skin.",
        "date": "2026-01-15T10:30:00+08:00",
        "thread_id": "thread-123",
        "message_id": "msg-456",
    }
    normalised = router.normalise(email_payload, "email")
    routing = router.route(normalised)
    print("Email normalised:", normalised)
    print("Routing:", routing)

    # Test escalation detection
    angry_payload = {
        "from": "angry@example.com",
        "subject": "Refund now or I chargeback!",
        "body": "This is unacceptable. I want a refund immediately or I'm filing a chargeback.",
        "date": "2026-01-15T14:00:00+08:00",
        "thread_id": "thread-789",
        "message_id": "msg-012",
    }
    normalised_angry = router.normalise(angry_payload, "email")
    routing_angry = router.route(normalised_angry)
    print("\nAngry email routing:", routing_angry)

    # Test Instagram DM
    ig_payload = {
        "sender_id": "ig_user_456",
        "sender_name": "watchlover_sg",
        "message": "Hey is the Expedition BPA-free?",
        "timestamp": "2026-01-15T11:00:00+08:00",
        "message_id": "ig_msg_789",
    }
    normalised_ig = router.normalise(ig_payload, "instagram_dm")
    print("\nInstagram DM normalised:", normalised_ig)