"""
BOLDR Self-Improving Customer Intelligence Engine
Gap Detector — Knowledge gap detection and classification

Author: Steve Ng, Founder and CEO - Digital Futures Consultancy LLP
"""

import logging
from datetime import datetime
from typing import Optional

from app.kb.schemas import (
    ClassificationResult,
    KnowledgeGap,
    AnswerabilityResult,
)

logger = logging.getLogger(__name__)


class GapDetector:
    """Detects knowledge gaps and distinguishes between:
    1. True knowledge gaps (product info not in KB)
    2. Shopify lookup needed (order operations)
    3. Low-confidence KB matches (escalation recommended)
    """

    # Order-related question types that need Shopify data, not KB
    SHOPIFY_QUESTION_TYPES = {
        "order_status",  # Order tracking, shipping status, refunds
    }

    # SOP-defined escalation triggers
    ESCALATION_KEYWORDS = {
        "angry": "angry_customer",
        "chargeback": "chargeback_threat",
        "dispute": "chargeback_threat",
        "refund": "refund_outstanding",
        "corporate": "corporate_bulk_order",
        "bulk": "corporate_bulk_order",
        "press": "media_press",
        "media": "media_press",
        "journalist": "media_press",
    }

    # Knowledge gap themes with marketing signal flags
    GAP_THEMES = {
        "sustainability": {"marketing_signal": True, "persona_bias": "health_conscious"},
        "materials_safety": {"marketing_signal": True, "persona_bias": "health_conscious"},
        "product_specs": {"marketing_signal": False, "persona_bias": "niche_buyer"},
        "sales_corporate": {"marketing_signal": True, "persona_bias": "prospect"},
        "servicing_legacy": {"marketing_signal": False, "persona_bias": "owner_aftercare"},
    }

    def classify_gap(self, classification: ClassificationResult) -> KnowledgeGap:
        """Create a KnowledgeGap from a classification result.

        Args:
            classification: The classification result for a ticket.

        Returns:
            KnowledgeGap with theme, marketing signal flag, and persona.
        """
        theme = self._determine_theme(classification)
        marketing_signal = self._is_marketing_signal(theme, classification)

        return KnowledgeGap(
            ticket_id=classification.ticket_id,
            question="",  # Will be filled from ticket data
            theme=theme,
            frequency=1,
            buyer_persona=classification.buyer_persona,
            marketing_signal=marketing_signal,
            kb_draft_status="pending",
        )

    def determine_answerability(
        self, classification: ClassificationResult, kb_confidence: float
    ) -> AnswerabilityResult:
        """Determine the type of answerability for a ticket.

        Distinguishes between:
        - ANSWERABLE: KB has the answer with sufficient confidence
        - NEEDS_SHOPIFY: Order operations requiring Shopify lookup
        - NOT_ANSWERABLE: True knowledge gap

        Args:
            classification: Classification result.
            kb_confidence: Confidence score from KB retrieval.

        Returns:
            AnswerabilityResult indicating the type.
        """
        # Order operations need Shopify, not KB
        if classification.question_type in self.SHOPIFY_QUESTION_TYPES:
            logger.info(
                f"Ticket {classification.ticket_id}: Shopify lookup needed "
                f"(type={classification.question_type})"
            )
            return AnswerabilityResult.NEEDS_SHOPIFY

        # High-confidence KB match
        if kb_confidence >= 0.5 and classification.is_answerable:
            return AnswerabilityResult.ANSWERABLE

        # Everything else is a knowledge gap
        return AnswerabilityResult.NOT_ANSWERABLE

    def check_escalation(self, message_body: str) -> tuple[bool, Optional[str]]:
        """Check if a ticket matches SOP escalation triggers.

        Args:
            message_body: The customer's message text.

        Returns:
            Tuple of (requires_escalation, escalation_reason).
        """
        message_lower = message_body.lower()

        for keyword, reason in self.ESCALATION_KEYWORDS.items():
            if keyword in message_lower:
                logger.info(f"Escalation trigger found: {keyword} → {reason}")
                return True, reason

        # Corporate order: 5+ units mentioned
        import re
        unit_match = re.search(r"(\d+)\s*(watch|piece|unit)", message_lower)
        if unit_match and int(unit_match.group(1)) >= 5:
            return True, "corporate_bulk_order"

        return False, None

    def _determine_theme(self, classification: ClassificationResult) -> str:
        """Determine the theme of a knowledge gap.

        Args:
            classification: Classification result.

        Returns:
            Theme string.
        """
        # Map question types to gap themes
        type_to_theme = {
            "materials_safety": "materials_safety",
            "knowledge_gap": "product_specs",
            "strap_compatibility": "product_specs",
            "servicing": "servicing_legacy",
            "product_general": "product_specs",
            "order_status": "order_operations",
            "engraving": "product_specs",
        }
        return type_to_theme.get(classification.question_type, "other")

    def _is_marketing_signal(
        self, theme: str, classification: ClassificationResult
    ) -> bool:
        """Determine if a knowledge gap represents a marketing signal.

        Args:
            theme: The gap theme.
            classification: Classification result.

        Returns:
            True if this gap should be flagged for marketing.
        """
        theme_config = self.GAP_THEMES.get(theme, {})
        return theme_config.get("marketing_signal", False)

    def generate_gap_log_entry(self, gap: KnowledgeGap) -> dict:
        """Generate a knowledge gap log entry in output schema format.

        Args:
            gap: KnowledgeGap object.

        Returns:
            Dict matching the gap log output schema.
        """
        return {
            "date_detected": datetime.now().strftime("%Y-%m-%d"),
            "ticket_id": gap.ticket_id,
            "question_theme": gap.theme,
            "buyer_persona": gap.buyer_persona,
            "frequency": gap.frequency,
            "marketing_signal": gap.marketing_signal,
            "kb_draft_status": gap.kb_draft_status,
            "suggested_answer": gap.suggested_answer,
        }


if __name__ == "__main__":
    detector = GapDetector()
    print("Gap Detector initialised.")