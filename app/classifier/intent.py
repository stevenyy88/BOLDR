"""
intent.py — BOLDR Question Type & Routing Classification Module

Classifies inbound customer support tickets into one of 7 question types and
determines whether the ticket is KB-answerable or requires Shopify/order data.

Question Types
--------------
1. strap_compatibility  — Strap fitment, length, material, interchange questions
2. servicing             — Watch servicing, repair, water-resistance re-test, warranty
3. product_general       — Pricing, availability, specs, comparisons, price matching
4. order_status          — Shipping, tracking, customs, delivery, order modifications
5. materials_safety       — Material safety, dye toxicity, titanium grade, skin concerns
6. knowledge_gap         — Niche/spec-collector questions outside current KB scope
7. engraving             — Engraving options, pricing, character limits, multi-line

Sub-Classification (routing intent)
------------------------------------
- kb_answerable    → The KB has sufficient information to draft a reply
- shopify_required  → An order operation requiring Shopify data (order status, tracking, etc.)

Both the primary question_type and the routing sub-classification are produced
with a confidence score (0–1) and a rule-based fallback when the LLM is unavailable.

Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field, asdict
from typing import Optional

from openai import OpenAI

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

QUESTION_TYPES = [
    "strap_compatibility",
    "servicing",
    "product_general",
    "order_status",
    "materials_safety",
    "knowledge_gap",
    "engraving",
]

ROUTING_INTENTS = [
    "kb_answerable",
    "shopify_required",
]

# Confidence threshold below which we fall back to the rule-based classifier
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))

# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------


@dataclass
class IntentResult:
    """Result of intent classification for a single ticket.

    Attributes:
        question_type: One of the 7 BOLDR question types.
        question_type_confidence: Confidence score (0–1) for question_type.
        routing_intent: Either 'kb_answerable' or 'shopify_required'.
        routing_intent_confidence: Confidence score (0–1) for routing_intent.
        method: 'llm' or 'rule_based' — which classifier produced this result.
        raw_llm_response: The raw JSON string from the LLM (for debugging), if any.
    """

    question_type: str
    question_type_confidence: float
    routing_intent: str
    routing_intent_confidence: float
    method: str = "unknown"
    raw_llm_response: Optional[str] = None

    def to_dict(self) -> dict:
        """Serialise to a plain dict."""
        return asdict(self)

    def is_confident(self, threshold: float = CONFIDENCE_THRESHOLD) -> bool:
        """Return True if both confidence scores meet the threshold."""
        return (
            self.question_type_confidence >= threshold
            and self.routing_intent_confidence >= threshold
        )


# ---------------------------------------------------------------------------
# Rule-Based Fallback Classifier
# ---------------------------------------------------------------------------

# Keyword patterns per question type.  Each entry is a list of (regex, weight)
# tuples.  The classifier sums weights for all matching patterns and picks the
# type with the highest total.  This gives us deterministic, LLM-free
# classification for when the API is unavailable.

_INTENT_KEYWORDS: dict[str, list[tuple[str, float]]] = {
    "strap_compatibility": [
        (r"\bstrap\b", 3.0),
        (r"\bband\b", 2.0),
        (r"\brubber\b", 2.0),
        (r"\bsilicone\b", 1.5),
        (r"\bnato\b", 2.0),
        (r"\blug\b", 2.0),
        (r"\blength.*wrist\b", 2.0),
        (r"\binterchangeab", 2.0),
        (r"\bfit.*strap\b", 2.0),
        (r"\b20mm\b", 1.0),
        (r"\b22mm\b", 1.0),
        (r"\bm(?:esh|ilanese)\b", 2.5),
        (r"\bbracelet\b", 2.0),
        (r"\bthird.?party\b", 2.0),
    ],
    "servicing": [
        (r"\bservic(e|ing)\b", 3.0),
        (r"\brepair\b", 3.0),
        (r"\bre-test\b", 2.0),
        (r"\bretest\b", 2.0),
        (r"\bwater\s*resist", 2.0),
        (r"\bwarrenty\b", 2.0),  # common misspelling
        (r"\bwarranty\b", 2.0),
        (r"\bcrown\b", 1.0),
        (r"\bcrystal\b", 1.0),
        (r"\bbattery\s*replac", 2.0),
        (r"\bmaintenance\b", 2.0),
        (r"\bpolish\b", 1.0),
        (r"\b overhaul\b", 2.0),
    ],
    "product_general": [
        (r"\bprice\b", 2.0),
        (r"\bpric(e|ing)\b", 2.0),
        (r"\bprice\s*match\b", 3.0),
        (r"\bdiscount\b", 2.0),
        (r"\bavailable\b", 2.0),
        (r"\bsold\s*out\b", 2.0),
        (r"\blimited\s*edition\b", 2.5),
        (r"\bcollab\b", 2.0),
        (r"\bspecif", 1.5),
        (r"\bweight\b", 1.0),
        (r"\bdimension\b", 1.0),
        (r"\bcompare\b", 1.5),
        (r"\bdiffer\b", 1.0),
        (r"\bmodel\b", 1.0),
        (r"\bwarranty\b", 2.5),
        (r"\breturn\s*policy\b", 2.5),
        (r"\bbulk\b", 3.0),
        (r"\bwholesale\b", 3.0),
        (r"\bcorporate\b", 2.0),
        (r"\bgift.*\bemployee\b", 2.0),
        (r"\bdiscount\s*code\b", 3.0),
    ],
    "order_status": [
        (r"\border\b", 3.0),
        (r"\bshipping\b", 3.0),
        (r"\bship\b", 2.0),
        (r"\bdeliver\b", 2.5),
        (r"\btrack(ing)?\b", 3.0),
        (r"\bcustoms\b", 2.5),
        (r"\bdut(y|ies)\b", 2.5),
        (r"\bexpress\s*ship", 3.0),
        (r"\bdispatch\b", 2.0),
        (r"\btransit\b", 2.0),
        (r"\breturn\b", 1.5),
        (r"\brefund\b", 2.0),
        (r"\bcancel\b", 2.0),
        (r"\barriv", 1.5),
        (r"\bwrong\s*item\b", 3.0),
        (r"\breceived.*order\b", 3.0),
        (r"\border\s*#\b", 3.5),
        (r"\bbld-\b", 3.5),
    ],
    "materials_safety": [
        (r"\btoxic\b", 3.0),
        (r"\bnon-toxic\b", 3.0),
        (r"\bdye\b", 3.0),
        (r"\bsafety\b", 3.0),
        (r"\bsafe(ty|ness)?\b", 2.0),
        (r"\ballerg", 2.5),
        (r"\bhypoallerg", 3.5),
        (r"\bskin\b", 1.5),
        (r"\bmaterial\b", 2.0),
        (r"\btitanium\s*grade\b", 3.0),
        (r"\bgrade\s*[25]\b", 2.5),
        (r"\bnickel\b", 2.5),
        (r"\blead\b", 2.0),
        (r"\bchemical\b", 2.0),
        (r"\b316l\b", 2.0),
        (r"\bsweat\b", 2.0),
        (r"\bbleed\b", 2.0),
        (r"\bbpa\b", 4.0),
        (r"\bbpa-free\b", 4.0),
        (r"\bcertif", 3.0),
        (r"\beu\b.*\bsafet", 3.5),
        (r"\bvegan\b", 3.0),
        (r"\brecycl", 2.5),
        (r"\bcarbon\s*footprint\b", 3.0),
        (r"\bsustainab", 3.0),
        (r"\bsilicone\b.*\bmaterial\b", 3.0),
        (r"\bstainless\s*steel\b.*\bv\b", 3.0),
        (r"\bresale\b.*\btitanium\b", 2.5),
    ],
    "knowledge_gap": [
        (r"\bmagnetic\b", 3.5),
        (r"\bmagnet\b", 2.0),
        (r"\bluminous\b", 3.5),
        (r"\bluminov?a\b", 3.5),
        (r"\bsuper-luminov?a\b", 3.5),
        (r"\bsustainab", 3.5),
        (r"\benvironment", 2.5),
        (r"\beco-friendly\b", 2.5),
        (r"\bcertifi", 2.5),
        (r"\bcos?c\b", 3.0),
        (r"\bchronomet", 3.0),
        (r"\baccuracy\b", 2.0),
        (r"\bcollector\b", 2.5),
        (r"\bvintage\b", 1.5),
        (r"\bheritage\b", 1.5),
        (r"\biso\b", 2.5),
        (r"\baltitude\b", 3.5),
        (r"\bextreme\s*sport", 3.5),
        (r"\bdiving\b.*\bdepth\b", 2.5),
        (r"\bcarbon\s*footprint\b", 4.0),
        (r"\bvegan\b", 3.0),
        (r"\brecycl\b", 2.0),
        (r"\bresale\b.*\bvalue\b", 3.0),
        (r"\barabic\b", 3.5),
        (r"\bperformance\b", 1.5),
        (r"\bcarbon.?neutral\b", 4.0),
        (r"\brecycl.*programme\b", 3.5),
        (r"\btake.?back\b", 3.5),
        (r"\bdispose.*responsibl", 3.0),
    ],
    "engraving": [
        (r"\bengrav", 4.0),
        (r"\binscrip", 3.0),
        (r"\bpersonaliz", 2.5),
        (r"\bmonogram", 2.5),
        (r"\bcaseback\b.*\btext\b", 3.0),
        (r"\bcharacter\b", 3.0),
        (r"\bcharacter\s*limit\b", 4.0),
        (r"\bfont\b", 2.0),
        (r"\bgift.*engrav", 3.0),
        (r"\bturnaround\b.*\bengrav", 3.5),
        (r"\bper\s*character\b", 4.0),
        (r"\btext\b.*\bcaseback\b", 3.0),
    ],
}

# Routing intent keyword patterns
_ROUTING_KEYWORDS: dict[str, list[tuple[str, float]]] = {
    "shopify_required": [
        (r"\border\b", 3.0),
        (r"\btracking\b", 3.0),
        (r"\bship\b", 2.0),
        (r"\bshipping\b", 2.5),
        (r"\bdeliver\b", 2.5),
        (r"\bcustoms\b", 3.0),
        (r"\bdut(y|ies)\b", 3.0),
        (r"\bexpress\b", 2.0),
        (r"\bdispatch\b", 2.0),
        (r"\btransit\b", 2.0),
        (r"\breturn\s*policy\b", 1.5),
        (r"\breturn\b", 1.5),
        (r"\brefund\b", 2.0),
        (r"\bcancel\b", 2.0),
        (r"\bwhere\s*is\s*my\b", 3.0),
        (r"\border\s*#\b", 3.0),
        (r"\border\s*status\b", 3.0),
        (r"\bhas\s*my\s*order\b", 3.0),
        (r"\bwhen\s*will\s*i\s*receive\b", 2.5),
        (r"\bcheckout\b", 3.0),
        (r"\bdiscount\s*code\b", 3.0),
        (r"\bsubmitted\b", 2.0),
        (r"\bplaced\s*the\s*order\b", 3.0),
        (r"\bjust\s*ordered\b", 3.0),
        (r"\bcan\s*i\s*change\b", 2.0),
        (r"\bwrong\s*text\b", 2.5),
        (r"\bcorrection\b", 1.5),
        (r"\brecycl(ing|e)\b", 2.0),
        (r"\btake.?back\b", 2.0),
        (r"\bresale\b", 2.0),
        (r"\baltitude\b", 2.0),
        (r"\bextreme\s*sport", 2.0),
        (r"\bcollabor(at|or)\b", 2.0),
        (r"\bindependent\s*watchmak", 2.5),
        (r"\bshock\s*resist\b", 2.0),
        (r"\barabic\b", 2.0),
        (r"\bvegan\b", 2.0),
        (r"\bmagnetic\b", 2.0),
        (r"\bluminov?a\b", 2.0),
        (r"\bfootprint\b", 2.0),
        (r"\bcarbon.?neutral\b", 2.0),
    ],
    "kb_answerable": [
        (r"\bstrap\b", 1.0),
        (r"\bservic", 1.5),
        (r"\bengrav", 1.0),
        (r"\bprice\b", 1.0),
        (r"\bspec\b", 1.0),
        (r"\bmaterial\b", 1.0),
        (r"\btoxic\b", 1.0),
        (r"\bsafety\b", 1.0),
        (r"\bwarranty\b", 1.5),
        (r"\bwater\s*resist", 1.5),
        (r"\bcompatib\b", 1.0),
        (r"\bavailable\b", 1.0),
        (r"\bbattery\b", 1.0),
        (r"\bdye\b", 1.0),
        (r"\bhypoallerg\b", 1.0),
    ],
}


def _score_text(text: str, keyword_map: dict[str, list[tuple[str, float]]]) -> dict[str, float]:
    """Score *text* against every category in *keyword_map* and return a
    ``{category: total_weight}`` mapping.
    """
    text_lower = text.lower()
    scores: dict[str, float] = {}
    for category, patterns in keyword_map.items():
        total = 0.0
        for pattern, weight in patterns:
            if re.search(pattern, text_lower):
                total += weight
        scores[category] = total
    return scores


def _softmax_to_confidence(scores: dict[str, float], winning_category: str) -> float:
    """Derive a pseudo-confidence from keyword scores using a simple normalisation.

    If the winning score is S_w and the sum of all positive scores is S_total,
    confidence ≈ S_w / S_total, clamped to [0.5, 1.0] for the winner and
    [0.0, 0.5] for others.  For rule-based we want to be honest: if only
    one category matched at all, confidence is high; if many overlap, lower.
    """
    total = sum(max(v, 0) for v in scores.values())
    if total == 0:
        return 0.5  # no signal at all
    raw = scores.get(winning_category, 0) / total
    # Scale into [0.4, 0.95] — rule-based is inherently less confident
    return round(0.4 + 0.55 * raw, 3)


def classify_intent_rule_based(
    subject: str,
    message_body: str,
) -> IntentResult:
    """Classify ticket intent using deterministic keyword matching.

    This is the fallback classifier used when the LLM API is unavailable.
    It uses weighted regex patterns per question type and routing intent
    to score the combined ``subject + message_body`` text.

    Args:
        subject: The ticket subject line.
        message_body: The full message body.

    Returns:
        An :class:`IntentResult` with ``method='rule_based'``.
    """
    combined = f"{subject} {message_body}"

    # --- Question type ---
    qt_scores = _score_text(combined, _INTENT_KEYWORDS)
    best_qt = max(qt_scores, key=lambda k: qt_scores[k]) if any(v > 0 for v in qt_scores.values()) else "product_general"
    qt_conf = _softmax_to_confidence(qt_scores, best_qt)

    # --- Routing intent ---
    ri_scores = _score_text(combined, _ROUTING_KEYWORDS)
    # If the best question type is order_status, boost shopify_required
    if best_qt == "order_status":
        ri_scores["shopify_required"] = ri_scores.get("shopify_required", 0) + 5.0
    best_ri = max(ri_scores, key=lambda k: ri_scores[k]) if any(v > 0 for v in ri_scores.values()) else "kb_answerable"
    ri_conf = _softmax_to_confidence(ri_scores, best_ri)

    return IntentResult(
        question_type=best_qt,
        question_type_confidence=qt_conf,
        routing_intent=best_ri,
        routing_intent_confidence=ri_conf,
        method="rule_based",
    )


# ---------------------------------------------------------------------------
# LLM-Based Classifier
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are a customer-support ticket classifier for BOLDR Supply Co., a Singapore-based \
watch micro-brand. You receive a ticket subject and message body and must output a \
JSON object with exactly these keys:

- "question_type": one of {question_types}
- "question_type_confidence": float 0.0–1.0
- "routing_intent": one of {routing_intents}
- "routing_intent_confidence": float 0.0–1.0

Definitions:
- "kb_answerable": the question can be fully answered using BOLDR's product specs, \
FAQ, rate cards, or CS SOP documentation.
- "shopify_required": the question requires real-time order, shipping, or customer \
data from Shopify (e.g. order status, tracking, customs/duties for a specific order, \
returns/refunds on a placed order).

Guidelines:
- Strap, fitment, and compatibility questions → strap_compatibility
- Service, repair, warranty, water-resistance questions → servicing
- Pricing, availability, comparison, specs questions → product_general
- Shipping, tracking, customs, delivery, returns questions → order_status
- Material safety, toxicity, allergen, grade questions → materials_safety
- Niche/collector/spec questions outside normal KB → knowledge_gap
- Engraving, personalization, caseback text → engraving
- If a ticket mentions an order number or asks about a specific order's status, \
it needs Shopify data → shopify_required.
- If a ticket is about product information that could be in a KB → kb_answerable.
- Return ONLY the JSON object, no additional text.
""".format(
    question_types=json.dumps(QUESTION_TYPES),
    routing_intents=json.dumps(ROUTING_INTENTS),
)


def classify_intent_llm(
    subject: str,
    message_body: str,
    *,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
) -> IntentResult:
    """Classify ticket intent using GLM-5.1 via an OpenAI-compatible API.

    The LLM is prompted to return structured JSON with question type,
    routing intent, and confidence scores.  If the LLM call fails or
    returns unparseable output, the function falls back to the rule-based
    classifier and logs a warning.

    Args:
        subject: The ticket subject line.
        message_body: The full message body.
        api_key: OpenAI-compatible API key. Falls back to ``GLM_API_KEY`` or
            ``OPENAI_API_KEY`` environment variable.
        base_url: API base URL. Falls back to ``GLM_BASE_URL`` env var or
            ``https://open.bigmodel.cn/api/paas/v4``.
        model: Model name. Falls back to ``GLM_MODEL`` env var or ``glm-5.1``.

    Returns:
        An :class:`IntentResult` with ``method='llm'`` on success, or
        ``method='rule_based'`` on fallback.
    """
    api_key = api_key or os.getenv("GLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = base_url or os.getenv("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
    model = model or os.getenv("GLM_MODEL", "glm-5.1")

    if not api_key:
        logger.warning("No API key available; falling back to rule-based classifier.")
        return classify_intent_rule_based(subject, message_body)

    user_content = f"Subject: {subject}\n\nMessage:\n{message_body}"

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content.strip()
        parsed = json.loads(raw)

        qt = parsed.get("question_type", "")
        if qt not in QUESTION_TYPES:
            logger.warning("LLM returned unknown question_type '%s'; falling back to rule-based.", qt)
            return classify_intent_rule_based(subject, message_body)

        ri = parsed.get("routing_intent", "")
        if ri not in ROUTING_INTENTS:
            logger.warning("LLM returned unknown routing_intent '%s'; falling back to rule-based.", ri)
            return classify_intent_rule_based(subject, message_body)

        qt_conf = float(parsed.get("question_type_confidence", 0.5))
        ri_conf = float(parsed.get("routing_intent_confidence", 0.5))
        qt_conf = max(0.0, min(1.0, qt_conf))
        ri_conf = max(0.0, min(1.0, ri_conf))

        return IntentResult(
            question_type=qt,
            question_type_confidence=qt_conf,
            routing_intent=ri,
            routing_intent_confidence=ri_conf,
            method="llm",
            raw_llm_response=raw,
        )

    except json.JSONDecodeError as exc:
        logger.warning("LLM returned invalid JSON (%s); falling back to rule-based.", exc)
        return classify_intent_rule_based(subject, message_body)
    except Exception as exc:
        logger.warning("LLM call failed (%s: %s); falling back to rule-based.", type(exc).__name__, exc)
        return classify_intent_rule_based(subject, message_body)


# ---------------------------------------------------------------------------
# Unified Classifier
# ---------------------------------------------------------------------------


def classify_intent(
    subject: str,
    message_body: str,
    *,
    prefer_llm: bool = True,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
) -> IntentResult:
    """Classify a BOLDR ticket's intent (question type + routing).

    Attempts LLM classification first (when ``prefer_llm=True``) and
    automatically falls back to the rule-based classifier if the LLM
    is unavailable or returns low-confidence results.

    Args:
        subject: The ticket subject line.
        message_body: The full message body.
        prefer_llm: If True (default), try the LLM classifier first.
        api_key: Optional override for the LLM API key.
        base_url: Optional override for the LLM API base URL.
        model: Optional override for the LLM model name.

    Returns:
        An :class:`IntentResult` with the best available classification.
    """
    if prefer_llm:
        result = classify_intent_llm(
            subject,
            message_body,
            api_key=api_key,
            base_url=base_url,
            model=model,
        )
        if result.method == "llm" and result.is_confident():
            return result
        # LLM failed or low confidence — fall through to rule-based
        logger.info("LLM result not confident (qt=%.2f, ri=%.2f); using rule-based fallback.",
                     result.question_type_confidence, result.routing_intent_confidence)

    return classify_intent_rule_based(subject, message_body)


# ---------------------------------------------------------------------------
# Test / Validation
# ---------------------------------------------------------------------------


def _run_tests(dataset_path: str | None = None) -> None:
    """Validate the classifier against the 70-ticket dataset.

    Runs the rule-based classifier over all tickets and prints per-class
    accuracy and overall accuracy.  This function is invoked when the
    module is run directly::

        python -m app.classifier.intent

    Args:
        dataset_path: Path to the CSV dataset. Defaults to the project's
            ``01_customer_tickets.csv``.
    """
    import csv
    from pathlib import Path

    if dataset_path is None:
        # Default path relative to this file
        dataset_path = str(
            Path(__file__).resolve().parents[3] / "dataset" / "01_customer_tickets.csv"
        )

    if not Path(dataset_path).exists():
        # Try the workspace-level path
        alt_path = Path("/home/steve/.openclaw/workspace/e27/1. BOLDR/dataset/01_customer_tickets.csv")
        if alt_path.exists():
            dataset_path = str(alt_path)
        else:
            print(f"ERROR: Dataset not found at {dataset_path}")
            return

    with open(dataset_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Loaded {len(rows)} tickets from {dataset_path}")
    print("=" * 70)

    correct_qt = 0
    correct_ri = 0
    total = len(rows)
    per_type_correct: dict[str, int] = {t: 0 for t in QUESTION_TYPES}
    per_type_total: dict[str, int] = {t: 0 for t in QUESTION_TYPES}

    misclassified = []

    for row in rows:
        subject = row.get("subject", "")
        message = row.get("message_body", "")
        expected_qt = row.get("question_type", "")
        expected_ri = "kb_answerable" if row.get("answered_by_kb", "").lower() == "yes" else "shopify_required"

        result = classify_intent_rule_based(subject, message)

        if result.question_type == expected_qt:
            correct_qt += 1
            per_type_correct[expected_qt] = per_type_correct.get(expected_qt, 0) + 1
        else:
            misclassified.append({
                "ticket_id": row.get("ticket_id", "?"),
                "expected": expected_qt,
                "predicted": result.question_type,
                "subject": subject[:60],
            })

        if result.routing_intent == expected_ri:
            correct_ri += 1

        per_type_total[expected_qt] = per_type_total.get(expected_qt, 0) + 1

    print(f"\n{'QUESTION TYPE CLASSIFICATION':^70}")
    print("-" * 70)
    for qt in QUESTION_TYPES:
        total_t = per_type_total.get(qt, 0)
        correct_t = per_type_correct.get(qt, 0)
        pct = (correct_t / total_t * 100) if total_t > 0 else 0
        print(f"  {qt:<25} {correct_t:>3}/{total_t:>3}  ({pct:5.1f}%)")

    print("-" * 70)
    print(f"  {'OVERALL':<25} {correct_qt:>3}/{total:>3}  ({correct_qt/total*100:5.1f}%)")
    print()
    print(f"{'ROUTING INTENT CLASSIFICATION':^70}")
    print("-" * 70)
    print(f"  {'Overall accuracy':<25} {correct_ri:>3}/{total:>3}  ({correct_ri/total*100:5.1f}%)")

    if misclassified:
        print(f"\n{'MISCLASSIFIED TICKETS':^70}")
        print("-" * 70)
        for m in misclassified:
            print(f"  {m['ticket_id']:>10}  expected={m['expected']:<20} predicted={m['predicted']:<20}  \"{m['subject']}\"")

    print("\n" + "=" * 70)
    print("Intent classifier validation complete (rule-based).")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _run_tests()