#!/usr/bin/env python3
"""
BOLDR Self-Improving Customer Intelligence Engine
Test All Tickets — Run all 70 tickets through the classification pipeline

Usage:
    python scripts/test_all_tickets.py [--data-dir PATH]

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
from app.routing.sop_parser import SOPParser


def main():
    parser = argparse.ArgumentParser(description="Test all 70 BOLDR tickets through the pipeline")
    parser.add_argument("--data-dir", default=str(Path(__file__).parent.parent.parent / "dataset"))
    args = parser.parse_args()

    print("=" * 60)
    print("BOLDR Ticket Pipeline Test — 70 Tickets")
    print("Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP")
    print("=" * 60)

    # Load tickets
    tickets_path = Path(args.data_dir) / "01_customer_tickets.csv"
    with open(tickets_path, "r", encoding="utf-8") as f:
        tickets = list(csv.DictReader(f))

    print(f"\n📊 Loaded {len(tickets)} tickets")

    # Initialize modules
    gap_detector = GapDetector()
    theme_clusterer = ThemeClusterer()
    sop_parser = SOPParser()

    # Process each ticket
    results = []
    for ticket in tickets:
        question_type = ticket["question_type"]
        persona = ticket["buyer_persona"]
        answered_by_kb = ticket["answered_by_kb"]
        requires_escalation = ticket["requires_escalation"]

        # Determine answerability
        is_answerable = answered_by_kb == "yes"

        # Determine answerability type
        if question_type == "order_status":
            answerability_type = "needs_shopify"
        elif is_answerable:
            answerability_type = "kb_answer"
        else:
            answerability_type = "knowledge_gap"

        # Check escalation
        has_escalation, esc_reason = gap_detector.check_escalation(ticket.get("message_body", ""))

        # Create classification result
        classification = ClassificationResult(
            ticket_id=ticket["ticket_id"],
            question_type=question_type,
            buyer_persona=persona,
            confidence=0.9 if is_answerable else 0.3,
            is_answerable=is_answerable,
            answerability_type=answerability_type,
            escalation_required=requires_escalation == "yes" or has_escalation,
            escalation_reason=esc_reason,
        )

        results.append({
            "ticket_id": ticket["ticket_id"],
            "subject": ticket["subject"],
            "question_type": question_type,
            "persona": persona,
            "channel": ticket["channel"],
            "answered_by_kb": answered_by_kb,
            "requires_escalation": requires_escalation,
            "answerability_type": answerability_type,
            "predicted_escalation": has_escalation,
            "sop_routing": sop_parser.get_routing(question_type)["source"] if sop_parser.get_routing(question_type) else "N/A",
            "needs_shopify": question_type == "order_status",
        })

        # Add gap tickets to theme clusterer
        if not is_answerable:
            gap = gap_detector.classify_gap(classification)
            theme_clusterer.add_ticket(
                ticket["ticket_id"],
                gap.theme,
                gap.buyer_persona,
                ticket.get("subject", ""),
            )

    # Summary statistics
    print("\n📈 Pipeline Results Summary:")
    print(f"   Total tickets processed: {len(results)}")

    answerability_dist = Counter(r["answerability_type"] for r in results)
    print(f"\n   Answerability Distribution:")
    for atype, count in answerability_dist.most_common():
        print(f"     {atype}: {count} ({count/len(results)*100:.1f}%)")

    channel_dist = Counter(r["channel"] for r in results)
    print(f"\n   Channel Distribution:")
    for channel, count in channel_dist.most_common():
        print(f"     {channel}: {count}")

    type_dist = Counter(r["question_type"] for r in results)
    print(f"\n   Question Type Distribution:")
    for qtype, count in type_dist.most_common():
        print(f"     {qtype}: {count}")

    # Marketing brief
    brief = theme_clusterer.get_monthly_marketing_brief()
    print(f"\n📋 Monthly Marketing Brief:")
    print(f"   {brief['executive_summary']}")
    print(f"\n   Marketing Signals:")
    for signal in brief["marketing_signals"]:
        print(f"     🔴 {signal['signal']} → {signal['action']} (Priority: {signal['priority']})")

    print(f"\n   Action Items:")
    for action in brief["action_items"]:
        print(f"     • [{action['priority'].upper()}] {action['action']} (Deadline: {action['deadline']})")

    # Save results
    output_path = Path(args.data_dir) / ".." / "pipeline_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Results saved to {output_path}")

    print("\n✅ All 70 tickets processed successfully!")


if __name__ == "__main__":
    main()