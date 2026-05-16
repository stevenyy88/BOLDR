"""
BOLDR Self-Improving Customer Intelligence Engine
End-to-End Workflow Tests

Validates the full intelligence loop against the 70-ticket dataset.

Author: Steve Ng, Founder and CEO - Digital Futures Consultancy LLP
"""

import csv
import os
import sys
from pathlib import Path

# Ensure app modules are importable
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.kb.schemas import QuestionType, BuyerPersona, AnswerabilityResult
from app.intelligence.gap_detector import GapDetector
from app.intelligence.theme_clusterer import ThemeClusterer
from app.routing.sop_parser import SOPParser


DATASET_PATH = os.getenv(
    "DATASET_PATH",
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "dataset", "01_customer_tickets.csv"),
)


def load_tickets(path: str = DATASET_PATH) -> list[dict]:
    """Load customer tickets from the dataset CSV."""
    tickets = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tickets.append(row)
    return tickets


class TestEndToEnd:
    """End-to-end tests for the BOLDR intelligence loop."""

    @classmethod
    def setup_class(cls):
        cls.tickets = load_tickets()
        cls.gap_detector = GapDetector()
        cls.theme_clusterer = ThemeClusterer()
        cls.sop_parser = SOPParser()

    def test_tickets_loaded(self):
        """Test that all 70 tickets load correctly."""
        assert len(self.tickets) == 70, f"Expected 70 tickets, got {len(self.tickets)}"

    def test_question_types(self):
        """Test that all 7 question types are present with 10 tickets each."""
        type_counts = {}
        for t in self.tickets:
            qt = t["question_type"]
            type_counts[qt] = type_counts.get(qt, 0) + 1

        expected_types = {
            "strap_compatibility", "servicing", "product_general",
            "order_status", "materials_safety", "knowledge_gap", "engraving",
        }
        assert set(type_counts.keys()) == expected_types, f"Unexpected types: {set(type_counts.keys())}"

        for qt, count in type_counts.items():
            assert count == 10, f"Expected 10 tickets for {qt}, got {count}"

    def test_buyer_personas(self):
        """Test that all 7 buyer personas are present."""
        persona_counts = {}
        for t in self.tickets:
            p = t["buyer_persona"]
            persona_counts[p] = persona_counts.get(p, 0) + 1

        expected_personas = {
            "health_conscious", "gifter", "enthusiast",
            "niche_buyer", "owner_aftercare", "prospect", "transactional",
        }
        assert set(persona_counts.keys()) == expected_personas

    def test_kb_answerability_split(self):
        """Test the KB answerability split (50 answerable, 20 gaps)."""
        answerable = sum(1 for t in self.tickets if t["answered_by_kb"] == "yes")
        not_answerable = sum(1 for t in self.tickets if t["answered_by_kb"] == "no")
        assert answerable == 50, f"Expected 50 answerable, got {answerable}"
        assert not_answerable == 20, f"Expected 20 not answerable, got {not_answerable}"

    def test_escalation_distribution(self):
        """Test escalation distribution."""
        requires_esc = sum(1 for t in self.tickets if t["requires_escalation"] == "yes")
        no_esc = sum(1 for t in self.tickets if t["requires_escalation"] == "no")
        assert requires_esc == 26, f"Expected 26 escalation required, got {requires_esc}"
        assert no_esc == 44, f"Expected 44 no escalation, got {no_esc}"

    def test_channel_distribution(self):
        """Test multi-channel distribution (4 channels)."""
        channels = set(t["channel"] for t in self.tickets)
        expected = {"email", "chat", "instagram_dm", "whatsapp"}
        assert channels == expected, f"Expected {expected}, got {channels}"

    def test_sop_routing(self):
        """Test SOP routing rules for all question types."""
        for qt in ["materials_safety", "engraving", "strap_compatibility",
                    "servicing", "order_status", "knowledge_gap", "product_general"]:
            routing = self.sop_parser.get_routing(qt)
            assert routing is not None, f"No routing for {qt}"
            assert "source" in routing
            assert "action" in routing

    def test_shopify_detection(self):
        """Test that order_status questions are flagged as needing Shopify."""
        assert self.sop_parser.requires_shopify("order_status") == True
        assert self.sop_parser.requires_shopify("materials_safety") == False
        assert self.sop_parser.requires_shopify("knowledge_gap") == False

    def test_gap_detector_distinguishes_shopify(self):
        """Test that gap detector distinguishes Shopify lookups from true gaps."""
        from app.kb.schemas import ClassificationResult

        # Order status ticket → should need Shopify, not be a KB gap
        order_ticket = ClassificationResult(
            ticket_id="TKT-1002",
            question_type="order_status",
            buyer_persona="transactional",
            confidence=0.9,
            is_answerable=False,
            answerability_type="needs_shopify",
            escalation_required=False,
        )
        result = self.gap_detector.determine_answerability(order_ticket, kb_confidence=0.2)
        assert result == AnswerabilityResult.NEEDS_SHOPIFY

        # Materials safety ticket → should be a true knowledge gap
        gap_ticket = ClassificationResult(
            ticket_id="TKT-1046",
            question_type="knowledge_gap",
            buyer_persona="niche_buyer",
            confidence=0.3,
            is_answerable=False,
            answerability_type="knowledge_gap",
            escalation_required=True,
        )
        result = self.gap_detector.determine_answerability(gap_ticket, kb_confidence=0.2)
        assert result == AnswerabilityResult.NOT_ANSWERABLE

    def test_theme_clusterer(self):
        """Test theme clustering with sample gap tickets."""
        clusterer = ThemeClusterer()
        clusterer.add_ticket("TKT-001", "materials_safety", "health_conscious", "Is this BPA-free?")
        clusterer.add_ticket("TKT-002", "sustainability", "health_conscious", "Are your straps vegan?")
        clusterer.add_ticket("TKT-003", "product_general", "niche_buyer", "Magnetic field resistance?")

        report = clusterer.get_weekly_theme_report()
        assert report["total_gap_tickets"] == 3
        assert len(report["themes"]) == 3

        brief = clusterer.get_monthly_marketing_brief()
        assert "executive_summary" in brief
        assert "marketing_signals" in brief
        assert "action_items" in brief

    def test_tone_guidelines(self):
        """Test that tone guidelines are extracted from SOP."""
        tone = self.sop_parser.get_tone_prompt()
        assert "friendly" in tone.lower()
        assert "direct" in tone.lower()
        assert "never promise" in tone.lower()

    def test_knowledge_gap_analysis(self):
        """Test knowledge gap analysis: 10 order ops + 10 true gaps."""
        gap_tickets = [t for t in self.tickets if t["answered_by_kb"] == "no"]

        # Order operations (need Shopify, not KB gaps)
        order_ops = [t for t in gap_tickets if t["question_type"] == "order_status"]
        true_gaps = [t for t in gap_tickets if t["question_type"] != "order_status"]

        assert len(gap_tickets) == 20, f"Expected 20 gaps, got {len(gap_tickets)}"
        # Note: Some knowledge_gap type tickets are also in the true gaps
        assert len(order_ops) == 10, f"Expected 10 order ops, got {len(order_ops)}"

    def test_persona_taxonomy(self):
        """Test that we handle both 5-persona (brief) and 7-persona (dataset) taxonomies."""
        from app.kb.schemas import BRIEF_PERSONAS, DATASET_PERSONAS

        assert len(BRIEF_PERSONAS) == 5, "Brief should define 5 personas"
        assert len(DATASET_PERSONAS) == 7, "Dataset should have 7 personas"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])