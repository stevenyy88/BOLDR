"""
BOLDR Self-Improving Customer Intelligence Engine
Reply Generator — Drafts BOLDR-brand-voice replies using LLM

Author: Steve Ng, Founder and CEO - Digital Futures Consultancy LLP
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class ReplyGenerator:
    """Generates customer replies in BOLDR's brand voice using LLM.

    Follows SOP tone guidelines:
    - Friendly but not overly casual (premium brand)
    - Direct — answer clearly, no filler
    - Helpful — point somewhere useful if we can't help directly
    - Never promise uncertain information
    """

    def __init__(
        self,
        model: str = "glm-5.1",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
    ):
        self.model = model
        self.api_key = api_key or os.getenv("GLM_API_KEY", "")
        self.api_base = api_base or os.getenv("GLM_API_BASE", "https://open.bigmodel.cn/api/paas/v4")
        self.fallback_model = os.getenv("FALLBACK_MODEL", "claude-3-haiku-20240307")

    def draft_reply(
        self,
        ticket_id: str,
        customer_name: str,
        subject: str,
        question_type: str,
        persona: str,
        kb_answer: str,
        sop_routing: str,
        channel: str = "email",
        escalation: bool = False,
        confidence: float = 1.0,
    ) -> dict:
        """Draft a reply in BOLDR brand voice.

        Args:
            ticket_id: The ticket ID.
            customer_name: Customer's name (or "there" if unknown).
            subject: Ticket subject line.
            question_type: Classified question type.
            persona: Buyer persona tag.
            kb_answer: Answer retrieved from KB (or gap message).
            sop_routing: SOP routing source.
            channel: Communication channel (email, chat, instagram_dm, whatsapp).
            escalation: Whether this needs human escalation.
            confidence: KB confidence score (0-1).

        Returns:
            Dict with draft_reply, confidence, needs_approval, channel.
        """
        if escalation:
            return self._draft_escalation_reply(
                ticket_id, customer_name, subject, channel
            )

        if confidence < 0.5:
            return self._draft_low_confidence_reply(
                ticket_id, customer_name, subject, question_type, channel
            )

        return self._draft_kb_reply(
            ticket_id, customer_name, subject, question_type, persona,
            kb_answer, sop_routing, channel, confidence
        )

    def _draft_kb_reply(
        self,
        ticket_id: str,
        customer_name: str,
        subject: str,
        question_type: str,
        persona: str,
        kb_answer: str,
        sop_routing: str,
        channel: str,
        confidence: float,
    ) -> dict:
        """Draft a reply using KB answer in BOLDR brand voice."""

        # Channel-appropriate greetings and sign-offs
        greetings = {
            "email": f"Hi {customer_name},\n\nThanks for reaching out! Happy to help with that.",
            "chat": f"Hi {customer_name}! Happy to help.",
            "instagram_dm": f"Hey {customer_name}! 👋",
            "whatsapp": f"Hi {customer_name}! 👍",
        }
        signoffs = {
            "email": "Best regards,\nBOLDR CS Team",
            "chat": "— BOLDR CS Team",
            "instagram_dm": "— BOLDR CS Team 🏔️",
            "whatsapp": "— BOLDR CS Team",
        }

        greeting = greetings.get(channel, greetings["email"])
        signoff = signoffs.get(channel, signoffs["email"])

        # Build the reply body
        reply_body = self._format_answer(kb_answer, question_type, persona)

        draft = f"{greeting}\n\n{reply_body}\n\n{signoff}"

        return {
            "ticket_id": ticket_id,
            "draft_reply": draft,
            "confidence": confidence,
            "needs_approval": confidence < 0.8,  # Lower confidence needs human check
            "channel": channel,
            "source": "kb",
            "sop_routing": sop_routing,
        }

    def _format_answer(self, kb_answer: str, question_type: str, persona: str) -> str:
        """Format the KB answer based on question type and persona."""

        # Persona-aware additions
        persona_additions = {
            "health_conscious": "All BOLDR straps are BPA-free and our titanium cases are hypoallergenic.",
            "gifter": "Engraving makes it a truly personal gift — see our rate card for pricing.",
            "enthusiast": "As a fellow watch enthusiast, you'll appreciate the Miyota 9015 movement.",
            "niche_buyer": "",
            "owner_aftercare": "",
            "prospect": "",
            "transactional": "",
        }

        addition = persona_additions.get(persona, "")

        if addition:
            return f"{kb_answer}\n\n{addition}"
        return kb_answer

    def _draft_escalation_reply(
        self, ticket_id: str, customer_name: str, subject: str, channel: str
    ) -> dict:
        """Draft a polite handoff reply for escalated tickets."""

        greetings = {
            "email": f"Hi {customer_name},\n\nThanks for reaching out about \"{subject}.\"",
            "chat": f"Hi {customer_name}, thanks for your question.",
            "instagram_dm": f"Hey {customer_name}, thanks for reaching out!",
            "whatsapp": f"Hi {customer_name}, thanks for your question.",
        }

        greeting = greetings.get(channel, greetings["email"])

        draft = (
            f"{greeting}\n\n"
            f"This needs a closer look from our team — I want to make sure we get you the "
            f"right answer. I've flagged this with our CS lead and they'll follow up within "
            f"24 hours.\n\n"
            f"In the meantime, if it's urgent, you can also reach us at cs@boldr.co.\n\n"
            f"Best regards,\nBOLDR CS Team"
        )

        return {
            "ticket_id": ticket_id,
            "draft_reply": draft,
            "confidence": 0.0,
            "needs_approval": True,
            "channel": channel,
            "source": "escalation",
            "sop_routing": "Human CS Lead",
        }

    def _draft_low_confidence_reply(
        self, ticket_id: str, customer_name: str, subject: str,
        question_type: str, channel: str
    ) -> dict:
        """Draft a reply for low-confidence KB matches (knowledge gaps)."""

        greetings = {
            "email": f"Hi {customer_name},\n\nThanks for reaching out!",
            "chat": f"Hi {customer_name}!",
            "instagram_dm": f"Hey {customer_name}! 👋",
            "whatsapp": f"Hi {customer_name}!",
        }
        greeting = greetings.get(channel, greetings["email"])

        draft = (
            f"{greeting}\n\n"
            f"Great question — I want to make sure I give you an accurate answer. "
            f"I'm checking with our team and will get back to you within 24 hours.\n\n"
            f"In the meantime, you might find useful info at boldr.co/faq.\n\n"
            f"Best regards,\nBOLDR CS Team"
        )

        return {
            "ticket_id": ticket_id,
            "draft_reply": draft,
            "confidence": 0.0,
            "needs_approval": True,
            "channel": channel,
            "source": "knowledge_gap",
            "sop_routing": "New Questions Log",
        }


class KBAutoDrafter:
    """Auto-drafts KB entries when knowledge gaps are resolved.

    When a team member provides an answer to a knowledge gap ticket,
    this module generates a structured KB entry for 1-click approval
    in the Streamlit dashboard.
    """

    def draft_entry(
        self,
        question: str,
        answer: str,
        theme: str,
        persona: str,
        source: str = "cs_team",
    ) -> dict:
        """Generate a structured KB entry from a resolved gap.

        Args:
            question: The original customer question.
            answer: The team-provided answer.
            theme: Detected theme category.
            persona: Buyer persona tag.
            source: Who provided the answer (cs_team, product_team, etc.)

        Returns:
            Dict with the auto-drafted KB entry, ready for approval.
        """
        # Generate a short title from the question
        title = question.strip().rstrip("?").capitalize()
        if len(title) > 80:
            title = title[:77] + "..."

        return {
            "id": f"kb-auto-{theme}-{hash(question) % 10000:04d}",
            "title": title,
            "question": question,
            "answer": answer,
            "theme": theme,
            "persona": persona,
            "source": source,
            "status": "pending_approval",
            "auto_generated": True,
            "categories": self._suggest_categories(theme, persona),
            "related_topics": self._suggest_related(theme),
        }

    def _suggest_categories(self, theme: str, persona: str) -> list[str]:
        """Suggest KB categories for the entry."""
        category_map = {
            "materials_safety": ["Safety", "Materials", "Straps"],
            "sustainability": ["Sustainability", "Materials", "FAQ"],
            "engraving": ["Services", "Personalisation", "Pricing"],
            "strap_compatibility": ["Products", "Straps", "Compatibility"],
            "servicing": ["Services", "Warranty", "Pricing"],
            "order_status": ["Orders", "Shipping", "FAQ"],
            "product_general": ["Products", "Specifications", "FAQ"],
            "knowledge_gap": ["FAQ", "New"],
        }
        return category_map.get(theme, ["FAQ"])

    def _suggest_related(self, theme: str) -> list[str]:
        """Suggest related topics for cross-linking."""
        related_map = {
            "materials_safety": ["BPA-free straps", "hypoallergenic", "nickel-free"],
            "sustainability": ["vegan straps", "recycling", "carbon-neutral"],
            "engraving": ["personalisation", "gift ideas", "corporate"],
            "strap_compatibility": ["20mm straps", "quick-release", "FKM rubber"],
            "servicing": ["warranty", "battery replacement", "regulation"],
            "order_status": ["shipping", "tracking", "returns"],
            "product_general": ["Expedition", "Journey", "comparison"],
            "knowledge_gap": [],
        }
        return related_map.get(theme, [])


if __name__ == "__main__":
    # Demo: draft a reply for a materials_safety ticket
    generator = ReplyGenerator()
    drafter = KBAutoDrafter()

    # Draft a KB-backed reply
    reply = generator.draft_reply(
        ticket_id="TKT-1016",
        customer_name="Caleb",
        subject="Strap dye safety",
        question_type="materials_safety",
        persona="health_conscious",
        kb_answer="All BOLDR FKM rubber and Nylon NATO straps are BPA-free and use non-toxic dyes. The coloured straps (including Red, Navy, and Olive) are designed for active wear and are safe for skin contact even with heavy sweating.",
        sop_routing="Product One-Pager",
        channel="email",
        confidence=0.92,
    )
    print("=== DRAFT REPLY ===")
    print(reply["draft_reply"])
    print(f"\nConfidence: {reply['confidence']}")
    print(f"Needs approval: {reply['needs_approval']}")

    # Draft a KB auto-entry
    entry = drafter.draft_entry(
        question="Are your straps vegan-friendly?",
        answer="Our FKM rubber straps are 100% vegan — no animal products used. Our leather straps are not vegan. Our Nylon NATO straps are also vegan-friendly.",
        theme="sustainability",
        persona="health_conscious",
    )
    print("\n=== AUTO-DRAFTED KB ENTRY ===")
    import json
    print(json.dumps(entry, indent=2))