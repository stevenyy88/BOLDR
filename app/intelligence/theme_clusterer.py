"""
BOLDR Self-Improving Customer Intelligence Engine
Theme Clusterer — Weekly theme clustering and monthly marketing brief generation

Author: Steve Ng, Founder and CEO - Digital Futures Consultancy LLP
"""

import logging
from collections import Counter
from datetime import datetime
from typing import Optional

from app.kb.schemas import BuyerPersona, BRIEF_PERSONAS, DATASET_PERSONAS

logger = logging.getLogger(__name__)


# Theme-to-persona mapping (from brief + dataset analysis)
THEME_PERSONA_MAP = {
    "materials_safety": "health_conscious",
    "sustainability": "health_conscious",
    "engraving": "gifter",
    "strap_compatibility": "enthusiast",
    "product_general": "prospect",
    "servicing": "owner_aftercare",
    "order_status": "transactional",
    "knowledge_gap": "niche_buyer",
}

# Theme-to-marketing-action mapping (from brief)
THEME_MARKETING_ACTIONS = {
    "BPA-free straps": {
        "persona": "Health-Conscious Buyer",
        "action": 'Product badge: "BPA-Free Straps"',
        "priority": "high",
    },
    "vegan materials": {
        "persona": "Sustainability Advocate",
        "action": "Develop vegan strap angle — new product positioning",
        "priority": "high",
    },
    "corporate gifting": {
        "persona": "Gifter",
        "action": "Create bulk pricing KB entry + corporate gifting page",
        "priority": "medium",
    },
    "nickel allergy": {
        "persona": "Health-Conscious Buyer",
        "action": "Add hypoallergenic product page section",
        "priority": "medium",
    },
    "magnetic field resistance": {
        "persona": "Niche Buyer",
        "action": "Add MRI/medical environment safety note to product specs",
        "priority": "low",
    },
    "altitude performance": {
        "persona": "Active / Outdoor Buyer",
        "action": "Add altitude performance specs to product page",
        "priority": "low",
    },
}


class ThemeClusterer:
    """Clusters novel questions by theme and generates marketing intelligence."""

    def __init__(self):
        self.theme_counts: Counter = Counter()
        self.persona_theme_map: dict = {}
        self.gap_tickets: list = []

    def add_ticket(self, ticket_id: str, theme: str, persona: str, question: str):
        """Add a knowledge gap ticket to the clusterer.

        Args:
            ticket_id: The ticket ID.
            theme: The detected theme.
            persona: The buyer persona tag.
            question: The customer question text.
        """
        self.theme_counts[theme] += 1
        self.gap_tickets.append({
            "ticket_id": ticket_id,
            "theme": theme,
            "persona": persona,
            "question": question,
            "date": datetime.now().strftime("%Y-%m-%d"),
        })

        # Map theme to persona
        if theme not in self.persona_theme_map:
            self.persona_theme_map[theme] = Counter()
        self.persona_theme_map[theme][persona] += 1

    def get_weekly_theme_report(self) -> dict:
        """Generate a weekly theme clustering report.

        Returns:
            Dict with theme frequencies, persona associations, and recommendations.
        """
        themes = []
        for theme, count in self.theme_counts.most_common():
            primary_persona = THEME_PERSONA_MAP.get(theme, "unknown")
            marketing_action = self._get_marketing_action(theme)

            themes.append({
                "theme": theme,
                "frequency": count,
                "primary_persona": primary_persona,
                "persona_distribution": dict(
                    self.persona_theme_map.get(theme, Counter())
                ),
                "marketing_action": marketing_action,
            })

        return {
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "total_gap_tickets": len(self.gap_tickets),
            "themes": themes,
            "top_themes": [t["theme"] for t in themes[:5]],
        }

    def get_monthly_marketing_brief(self) -> dict:
        """Generate a monthly marketing intelligence brief.

        This is the core output of the intelligence loop — answering:
        "What are customers asking that is NOT on your product pages?"

        Returns:
            Dict with marketing signals, persona insights, and action items.
        """
        theme_report = self.get_weekly_theme_report()

        # Build marketing signals from themes
        marketing_signals = []
        for theme_data in theme_report["themes"]:
            if theme_data["marketing_action"]:
                marketing_signals.append({
                    "signal": theme_data["theme"],
                    "frequency": theme_data["frequency"],
                    "persona": theme_data["primary_persona"],
                    "action": theme_data["marketing_action"],
                    "priority": self._get_priority(theme_data["theme"]),
                })

        # Sort by priority and frequency
        priority_order = {"high": 0, "medium": 1, "low": 2}
        marketing_signals.sort(
            key=lambda x: (priority_order.get(x["priority"], 3), -x["frequency"])
        )

        # Build persona summary
        persona_summary = self._build_persona_summary()

        return {
            "brief_date": datetime.now().strftime("%Y-%m-%d"),
            "title": "Monthly Marketing Intelligence Brief — What Customers Ask That's Not on Your Product Pages",
            "executive_summary": self._generate_executive_summary(theme_report),
            "marketing_signals": marketing_signals,
            "persona_insights": persona_summary,
            "action_items": self._generate_action_items(marketing_signals),
            "knowledge_gaps_to_address": [
                t for t in theme_report["themes"]
                if t["frequency"] >= 2  # Recurring gaps
            ],
        }

    def _get_marketing_action(self, theme: str) -> Optional[str]:
        """Get the marketing action for a theme."""
        for key, config in THEME_MARKETING_ACTIONS.items():
            if key.lower() in theme.lower():
                return config["action"]
        return None

    def _get_priority(self, theme: str) -> str:
        """Get the priority level for a theme."""
        for key, config in THEME_MARKETING_ACTIONS.items():
            if key.lower() in theme.lower():
                return config["priority"]
        return "low"

    def _build_persona_summary(self) -> list:
        """Build a summary of buyer persona distributions across themes."""
        personas = []
        for persona_key, persona_info in DATASET_PERSONAS.items():
            persona_themes = [
                theme for theme, p_counter in self.persona_theme_map.items()
                if persona_key in p_counter
            ]
            if persona_themes:
                personas.append({
                    "persona": persona_key,
                    "label": persona_info["label"],
                    "themes": persona_themes,
                    "total_gaps": sum(
                        self.theme_counts[t] for t in persona_themes
                    ),
                })
        return sorted(personas, key=lambda x: -x["total_gaps"])

    def _generate_executive_summary(self, theme_report: dict) -> str:
        """Generate an executive summary for the marketing brief."""
        total = theme_report["total_gap_tickets"]
        top = theme_report["top_themes"][:3]
        return (
            f"This month, {total} customer enquiries could not be answered from the "
            f"existing Knowledge Base. The top emerging themes are: "
            f"{', '.join(top)}. These represent gaps in product documentation "
            f"and marketing positioning that, if addressed, could unlock new "
            f"customer segments and revenue opportunities."
        )

    def _generate_action_items(self, signals: list) -> list:
        """Generate prioritised action items from marketing signals."""
        actions = []
        for signal in signals:
            actions.append({
                "action": signal["action"],
                "priority": signal["priority"],
                "persona": signal["persona"],
                "theme": signal["signal"],
                "deadline": "2 weeks" if signal["priority"] == "high" else "1 month",
            })
        return actions


if __name__ == "__main__":
    clusterer = ThemeClusterer()

    # Simulate some gap tickets
    clusterer.add_ticket("TKT-001", "materials_safety", "health_conscious", "Is this BPA-free?")
    clusterer.add_ticket("TKT-002", "materials_safety", "health_conscious", "Are the straps nickel-free?")
    clusterer.add_ticket("TKT-003", "sustainability", "health_conscious", "Are your straps vegan?")
    clusterer.add_ticket("TKT-004", "product_general", "niche_buyer", "Magnetic field resistance?")
    clusterer.add_ticket("TKT-005", "engraving", "gifter", "Can I engrave in Arabic?")

    brief = clusterer.get_monthly_marketing_brief()
    import json
    print(json.dumps(brief, indent=2))