#!/usr/bin/env python3
"""
BOLDR Self-Improving Customer Intelligence Engine
Generate Knowledge Gap Log — Analyse the 70-ticket dataset for knowledge gaps

Usage:
    python scripts/generate_gap_log.py [--data-dir PATH] [--output PATH]

Author: Steve Ng, Founder and CEO - Digital Futures Consultancy LLP
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.kb.schemas import ClassificationResult, AnswerabilityResult
from app.intelligence.gap_detector import GapDetector
from app.intelligence.theme_clusterer import ThemeClusterer


def main():
    parser = argparse.ArgumentParser(description="Generate BOLDR Knowledge Gap Log from 70-ticket dataset")
    parser.add_argument("--data-dir", default=str(Path(__file__).parent.parent / "dataset"))
    parser.add_argument("--output", default=str(Path(__file__).parent.parent / "data" / "gap_log.json"))
    args = parser.parse_args()

    print("=" * 60)
    print("BOLDR Knowledge Gap Log Generator")
    print("Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP")
    print("=" * 60)

    # Load tickets
    tickets_path = Path(args.data_dir) / "01_customer_tickets.csv"
    with open(tickets_path, "r", encoding="utf-8") as f:
        tickets = list(csv.DictReader(f))

    print(f"\n📊 Loaded {len(tickets)} tickets")

    # Process gaps
    gap_detector = GapDetector()
    theme_clusterer = ThemeClusterer()

    gap_entries = []
    for ticket in tickets:
        if ticket["answered_by_kb"] == "no":
            # Determine answerability type
            if ticket["question_type"] == "order_status":
                answerability_type = "needs_shopify"
            else:
                answerability_type = "knowledge_gap"

            classification = ClassificationResult(
                ticket_id=ticket["ticket_id"],
                question_type=ticket["question_type"],
                buyer_persona=ticket["buyer_persona"],
                confidence=0.3,
                is_answerable=False,
                answerability_type=answerability_type,
                escalation_required=ticket["requires_escalation"] == "yes",
            )

            gap = gap_detector.classify_gap(classification)
            theme_clusterer.add_ticket(
                ticket["ticket_id"],
                gap.theme,
                gap.buyer_persona,
                ticket.get("subject", ""),
            )

            gap_entries.append({
                "ticket_id": ticket["ticket_id"],
                "subject": ticket["subject"],
                "question_type": ticket["question_type"],
                "persona": ticket["buyer_persona"],
                "channel": ticket["channel"],
                "answerability_type": answerability_type,
                "theme": gap.theme,
                "marketing_signal": gap.has_marketing_signal,
                "escalation": ticket["requires_escalation"] == "yes",
            })

    # Categorise gaps
    shopify_gaps = [g for g in gap_entries if g["answerability_type"] == "needs_shopify"]
    true_gaps = [g for g in gap_entries if g["answerability_type"] == "knowledge_gap"]

    print(f"\n📋 Knowledge Gap Analysis:")
    print(f"   Total not answerable by KB: {len(gap_entries)}")
    print(f"   Order operations (need Shopify): {len(shopify_gaps)}")
    print(f"   True knowledge gaps: {len(true_gaps)}")

    # Theme distribution
    theme_dist = Counter(g["theme"] for g in true_gaps)
    print(f"\n   True gap themes:")
    for theme, count in theme_dist.most_common():
        print(f"     {theme}: {count}")

    # Marketing signals
    signals = [g for g in true_gaps if g["marketing_signal"]]
    print(f"\n   Marketing signals detected: {len(signals)}")

    # Generate monthly brief
    brief = theme_clusterer.get_monthly_marketing_brief()

    # Save output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output = {
        "summary": {
            "total_tickets": len(tickets),
            "total_gaps": len(gap_entries),
            "shopify_gaps": len(shopify_gaps),
            "true_knowledge_gaps": len(true_gaps),
            "marketing_signals": len(signals),
            "theme_distribution": dict(theme_dist),
        },
        "gap_log": gap_entries,
        "marketing_brief": brief,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Gap log saved to {output_path}")
    print("\n✅ Knowledge gap log generated successfully!")


if __name__ == "__main__":
    main()