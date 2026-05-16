"""
BOLDR Self-Improving Customer Intelligence Engine
SOP Parser — Extract routing rules from CS SOP prose document

Author: Steve Ng, Founder and CEO - Digital Futures Consultancy LLP
"""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class SOPParser:
    """Parses the BOLDR CS SOP document to extract:
    - Enquiry type routing rules
    - Escalation triggers
    - Tone guidelines
    - New questions log
    """

    # Enquiry type routing (from SOP Section 4)
    ENQUIRY_ROUTING = {
        "materials_safety": {
            "source": "Product One-Pager",
            "action": "Check model-specific safety data (BPA-free, nickel-free, hypoallergenic, EU REACH)",
            "kb_sources": ["product_reference", "faq_document"],
        },
        "engraving": {
            "source": "Engraving Rate Card",
            "action": "Check character limits, pricing, amendment rules. Key: up to 40 chars, SGD 25-40, 1-hour free amendment window",
            "kb_sources": ["rate_card_engraving", "faq_document"],
        },
        "strap_compatibility": {
            "source": "Product One-Pager",
            "action": "Check 20mm lug width, strap types. All current models use 20mm quick-release",
            "kb_sources": ["product_reference", "faq_document"],
        },
        "servicing": {
            "source": "Servicing Rate Card",
            "action": "Check tier pricing, turnaround. Battery SGD 35 (3-5 days), Regulation SGD 85 (7-10 days), Full Service SGD 160-220",
            "kb_sources": ["rate_card_servicing", "faq_document"],
        },
        "order_status": {
            "source": "Shopify Admin",
            "action": "Log into Shopify, search by order number or email, check tracking. NEVER guess order status",
            "kb_sources": ["cs_sop"],  # SOP has the procedures
            "requires_shopify": True,
        },
        "knowledge_gap": {
            "source": "New Questions Log",
            "action": "Check with team before replying. Never fabricate answers. Log in New Questions Log spreadsheet",
            "kb_sources": [],  # No KB source by definition
        },
        "product_general": {
            "source": "Product One-Pager + FAQ",
            "action": "Check specs, comparison, pricing. Expedition (40mm, Grade 5 Ti) vs Journey (38mm, Grade 2 Ti)",
            "kb_sources": ["product_reference", "faq_document"],
        },
    }

    # Tone guidelines (from SOP Section 5)
    TONE_GUIDELINES = {
        "friendly_but_not_overly_casual": "We are a premium brand",
        "direct": "Answer the question clearly, don't pad with filler",
        "helpful": "If we can't help directly, point them somewhere useful",
        "never_promise_uncertain": "Never promise what you're not sure about — check first",
    }

    # Good/bad example openings (from SOP Section 5)
    GOOD_OPENINGS = [
        "Hi [Name], thanks for reaching out! Happy to help with that.",
    ]
    BAD_OPENINGS = [
        "Great question!",  # Overly casual
        "Dear Sir/Madam",  # Overly formal
    ]

    # Returns and warranty rules (from SOP)
    RETURNS_RULES = {
        "return_window": "14 days",
        "condition": "Unworn, unaltered, original packaging",
        "engraved_non_returnable": True,
        "engraved_exception": "Manufacturing defect only",
        "warranty_coverage": "2 years on movement",
        "warranty_exclusions": ["Physical damage", "Water damage from misuse", "Normal wear and tear", "Strap wear"],
    }

    # Engraving rules (from SOP)
    ENGRAVING_RULES = {
        "max_characters": 60,
        "standard_pricing": {
            "up_to_20": "SGD 25",
            "21_to_40": "SGD 40",
            "per_additional": "SGD 1.50",
        },
        "cjk_arabic": "SGD 3.00 per character, up to 15 characters",
        "amendment_within_1hr": "Free",
        "amendment_after_1hr": "SGD 15",
        "buckle_engraving": "SGD 15, metal buckles only, up to 10 chars",
        "logo_engraving": "SGD 60, requires vector file (.ai or .svg)",
    }

    def get_routing(self, question_type: str) -> Optional[dict]:
        """Get the routing rule for a question type.

        Args:
            question_type: One of the 7 BOLDR question types.

        Returns:
            Routing dict with source, action, and kb_sources.
        """
        return self.ENQUIRY_ROUTING.get(question_type)

    def get_tone_prompt(self) -> str:
        """Generate a tone guideline prompt for LLM reply drafting.

        Returns:
            String with tone guidelines for the brand voice check.
        """
        return (
            "BOLDR Brand Voice Guidelines:\n"
            f"- {self.TONE_GUIDELINES['friendly_but_not_overly_casual']}\n"
            f"- {self.TONE_GUIDELINES['direct']}\n"
            f"- {self.TONE_GUIDELINES['helpful']}\n"
            f"- {self.TONE_GUIDELINES['never_promise_uncertain']}\n\n"
            f"Good opening: {self.GOOD_OPENINGS[0]}\n"
            f"Bad openings to avoid: {', '.join(self.BAD_OPENINGS)}"
        )

    def requires_shopify(self, question_type: str) -> bool:
        """Check if a question type requires Shopify lookup.

        Args:
            question_type: The classified question type.

        Returns:
            True if this question type needs Shopify data.
        """
        routing = self.get_routing(question_type)
        return routing.get("requires_shopify", False) if routing else False


if __name__ == "__main__":
    parser = SOPParser()

    # Test all routing types
    for qtype in ["materials_safety", "engraving", "strap_compatibility",
                   "servicing", "order_status", "knowledge_gap", "product_general"]:
        routing = parser.get_routing(qtype)
        shopify = parser.requires_shopify(qtype)
        print(f"\n{qtype}:")
        print(f"  Source: {routing['source']}")
        print(f"  Action: {routing['action']}")
        print(f"  Needs Shopify: {shopify}")

    print(f"\nTone prompt:\n{parser.get_tone_prompt()}")