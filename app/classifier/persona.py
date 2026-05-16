"""
persona.py — BOLDR Buyer Persona Tagging Module

Tags inbound customer support tickets against 7 buyer personas based on
the content of the ticket subject and message body.

Buyer Personas
--------------
1. health_conscious  — Concerned about material safety, allergens, skin reactions
2. gifter            — Buying as a gift, asking about engraving, packaging, delivery times
3. enthusiast        — Knowledgeable about watches, asks technical strap/servicing questions
4. niche_buyer       — Collector or specialist asking niche/spec questions outside normal KB
5. owner_aftercare   — Existing owner asking about servicing, repairs, warranty, maintenance
6. prospect          — Pre-purchase questions: pricing, availability, comparisons
7. transactional     — Focused on logistics: shipping, tracking, customs, order status

The module provides both an LLM-based classifier (using GLM-5.1 via an
OpenAI-compatible endpoint) and a rule-based fallback that uses weighted
keyword patterns.  The unified :func:`classify_persona` tries LLM first
and falls back to rules when unavailable or low-confidence.

Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, asdict
from typing import Optional

from openai import OpenAI

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BUYER_PERSONAS = [
    "health_conscious",
    "gifter",
    "enthusiast",
    "niche_buyer",
    "owner_aftercare",
    "prospect",
    "transactional",
]

# Confidence threshold below which we fall back to the rule-based classifier
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))

# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------


@dataclass
class PersonaResult:
    """Result of persona classification for a single ticket.

    Attributes:
        persona: One of the 7 BOLDR buyer personas.
        confidence: Confidence score (0–1) for the persona assignment.
        method: 'llm' or 'rule_based' — which classifier produced this result.
        all_scores: Scores for all personas (useful for debugging / top-2).
        raw_llm_response: The raw JSON string from the LLM (for debugging), if any.
    """

    persona: str
    confidence: float
    method: str = "unknown"
    all_scores: Optional[dict[str, float]] = None
    raw_llm_response: Optional[str] = None

    def to_dict(self) -> dict:
        """Serialise to a plain dict."""
        d = asdict(self)
        return d

    def is_confident(self, threshold: float = CONFIDENCE_THRESHOLD) -> bool:
        """Return True if confidence meets the threshold."""
        return self.confidence >= threshold


# ---------------------------------------------------------------------------
# Rule-Based Fallback Classifier
# ---------------------------------------------------------------------------

_PERSONA_KEYWORDS: dict[str, list[tuple[str, float]]] = {
    "health_conscious": [
        (r"\btoxic\b", 3.5),
        (r"\bnon-toxic\b", 4.0),
        (r"\bdye\b", 3.0),
        (r"\bsafety\b", 3.0),
        (r"\bsafe\b", 2.0),
        (r"\ballerg", 3.5),
        (r"\bhypoallerg", 4.0),
        (r"\bskin\b", 2.5),
        (r"\breact\b", 3.0),
        (r"\bsensitive\s*skin\b", 4.0),
        (r"\bsweat\b", 3.0),
        (r"\bbleed\b", 3.0),
        (r"\bbpa\b", 4.0),
        (r"\bnickel\b", 3.5),
        (r"\bchemical\b", 2.5),
        (r"\b316l\b", 3.0),
        (r"\btitanium\s*grade\b", 3.0),
        (r"\bgrade\s*[25]\b", 2.5),
        (r"\bmaterial.*safe", 3.0),
        (r"\bstainless\s*steel\b", 1.5),
        (r"\bhealth\b", 2.0),
        (r"\birritat", 3.0),
        (r"\brash\b", 3.0),
        (r"\bfood.?grade\b", 4.0),
        (r"\bmedical.?grade\b", 4.0),
        (r"\bsilicone.*\bskin\b", 4.0),
        (r"\bsilicone.*\bsensit", 4.0),
        (r"\bskin.*\bsensit", 4.0),
        (r"\bsensit.*\bskin\b", 4.0),
        (r"\bvegan.?friend", 3.5),
        (r"\bvegan\b", 2.5),
        (r"\bwater\s*resist.*\bmaterial", 3.5),
        (r"\bmaterial.*\bstrap\b", 3.0),
        (r"\btitanium.*\bv\?\s*stainless", 3.5),
        (r"\btitanium.*\bstainless", 3.0),
    ],
    "gifter": [
        (r"\bgift\b", 4.0),
        (r"\bbirthday\b", 3.5),
        (r"\bchristmas\b", 3.5),
        (r"\bfather'?s?\s*day\b", 3.5),
        (r"\bmother'?s?\s*day\b", 3.5),
        (r"\banniversary\b", 3.0),
        (r"\bwedding\b", 2.5),
        (r"\bengrav", 3.0),
        (r"\bpersonaliz", 3.0),
        (r"\binscrip", 3.0),
        (r"\bmonogram", 3.0),
        (r"\bdedication\b", 3.0),
        (r"\bpresent\b", 3.0),
        (r"\bsurprise\b", 2.0),
        (r"\bfor\s*my\s*(dad|mom|husband|wife|son|daughter|partner)\b", 3.5),
        (r"\bgift\s*wrap", 4.0),
        (r"\bgift\s*box", 4.0),
        (r"\bpackag", 1.5),
        (r"\bfor\s*my\s*father\b", 3.5),
        (r"\bcharacter\s*message", 3.0),
        (r"\bper.?character\b", 3.0),
    ],
    "enthusiast": [
        (r"\bstrap\b", 1.5),
        (r"\brubber\s*strap\b", 2.5),
        (r"\bsilicone\b", 2.0),
        (r"\bnato\b", 3.0),
        (r"\bbracelet\b", 2.0),
        (r"\bm(?:esh|ilanese)\b", 2.5),
        (r"\blug\s*width\b", 3.0),
        (r"\b20mm\b", 2.0),
        (r"\b22mm\b", 2.0),
        (r"\binterchangeab", 3.0),
        (r"\bfit.*wrist\b", 2.5),
        (r"\bservic(e|ing)\b", 2.5),
        (r"\brepair\b", 2.0),
        (r"\bwater\s*resist", 2.5),
        (r"\bretest\b", 3.0),
        (r"\bdiving\b", 2.0),
        (r"\bbattery\b", 2.0),
        (r"\bcrown\b", 1.5),
        (r"\bcrystal\b", 1.5),
        (r"\bmaintenance\b", 2.5),
        (r"\bmodel\b.*\bolder?\b", 2.5),
        (r"\bfrom\s*20(19|20|21)\b", 2.5),
    ],
    "niche_buyer": [
        (r"\bmagnetic\b", 3.5),
        (r"\bmagnet\b", 2.0),
        (r"\bluminov?a\b", 3.5),
        (r"\bsuper-luminov?a\b", 3.5),
        (r"\bsuperluminov?a\b", 3.5),
        (r"\bluminous\b", 3.5),
        (r"\bcollector\b", 3.5),
        (r"\bcollab(oration)?\b", 3.0),
        (r"\bindependent\s*watchmak", 3.5),
        (r"\bvintage\b", 2.5),
        (r"\bheritage\b", 2.5),
        (r"\bcos?c\b", 3.5),
        (r"\bchronomet", 3.5),
        (r"\biso\b", 3.0),
        (r"\bcertifi", 2.5),
        (r"\bresale\s*value\b", 3.0),
        (r"\bhold.*value\b", 2.5),
        (r"\bmicro.?brand\b", 2.5),
        (r"\baltitude\b", 3.0),
        (r"\bextreme\s*sport", 3.0),
        (r"\bshock\s*resist", 3.0),
        (r"\barabic\b", 3.0),
        (r"\brecycl.*programme\b", 3.5),
        (r"\btake.?back\b", 3.5),
        (r"\bcarbon\s*footprint\b", 3.5),
        (r"\bcarbon.?neutral\b", 3.5),
        (r"\bdispose.*responsibl", 3.0),
        (r"\bvegan.?friend", 3.0),
        (r"\bvegan\b", 2.0),
        (r"\bsustainab", 2.5),
        (r"\benvironment", 2.0),
    ],
    "owner_aftercare": [
        (r"\bservic(e|ing)\b", 3.0),
        (r"\brepair\b", 2.5),
        (r"\bwarranty\b", 3.0),
        (r"\bwarrenty\b", 3.0),  # common misspelling
        (r"\bre-?test\b", 3.0),
        (r"\bwater\s*resist", 2.0),
        (r"\bpolicy\b", 1.5),
        (r"\bcover\b", 1.5),
        (r"\bmovement\b", 2.0),
        (r"\bbattery\s*replac", 3.0),
        (r"\bpolish\b", 2.0),
        (r"\boverhaul\b", 2.5),
        (r"\bcrown\b", 1.5),
        (r"\bcrystal\b", 1.5),
        (r"\bolder?\s*model", 3.0),
        (r"\bfrom\s*20(19|20|21)\b", 2.5),
        (r"\bstill\s*servic", 3.0),
        (r"\bown\b", 2.0),
        (r"\bmy\s*(watch|boldr|expedition)\b", 2.5),
        (r"\bdive\b", 2.0),
        (r"\bturnaround\b", 1.5),
        (r"\bhow\s*long.*\bservic", 3.5),
        (r"\bservic.*\btake\b", 3.5),
    ],
    "prospect": [
        (r"\bprice\b", 2.5),
        (r"\bpric(e|ing)\b", 2.5),
        (r"\bprice\s*match\b", 3.5),
        (r"\bdiscount\b", 2.0),
        (r"\bavailable\b", 2.5),
        (r"\bsold\s*out\b", 2.5),
        (r"\blimited\s*edition\b", 2.5),
        (r"\bcollab\b", 2.0),
        (r"\bcompare\b", 2.5),
        (r"\bdiffer(ence|ent)?\b", 1.5),
        (r"\bvs\b", 2.0),
        (r"\bversus\b", 2.0),
        (r"\brecommend\b", 2.5),
        (r"\bwhich\s*model\b", 3.0),
        (r"\bthinking\s*about\s*(buy|get)", 3.0),
        (r"\bbefore\s*i\s*buy\b", 3.0),
        (r"\bconsider(ing)?\b", 2.0),
        (r"\bwarranty\b", 2.0),
        (r"\breturn\s*policy\b", 2.5),
        (r"\bbulk\b", 2.5),
        (r"\bwholesale\b", 2.5),
        (r"\bcorporate\b", 2.0),
        (r"\bdimension\b", 1.5),
        (r"\bweight\b", 1.5),
        (r"\btitanium.*\bstainless", 2.5),
        (r"\blighter\b", 2.0),
        (r"\bpractical\b", 1.5),
        (r"\bgift\s*wrap", 1.5),
        (r"\bgift\s*box", 1.5),
        (r"\bwedding\s*gift", 3.5),
    ],
    "transactional": [
        (r"\border\b", 3.0),
        (r"\bshipping\b", 3.0),
        (r"\bship\b", 2.0),
        (r"\bdeliver\b", 2.5),
        (r"\btrack(ing)?\b", 3.0),
        (r"\bcustoms\b", 3.0),
        (r"\bdut(y|ies)\b", 3.0),
        (r"\bexpress\b", 2.5),
        (r"\bdispatch\b", 2.0),
        (r"\btransit\b", 2.0),
        (r"\barriv", 2.0),
        (r"\bwhere\s*is\s*my\b", 3.0),
        (r"\bhow\s*long\b", 2.0),
        (r"\btime\b", 1.0),
        (r"\bturnaround\b", 2.0),
        (r"\bby\s*next\b", 2.5),
        (r"\burgent(ly)?\b", 3.0),
        (r"\bfast\b", 1.0),
        (r"\bwrong\s*item\b", 3.5),
        (r"\breceived.*order\b", 3.0),
        (r"\bwrong\s*colour\b", 3.0),
        (r"\bwrong\s*color\b", 3.0),
        (r"\brefund\b", 2.0),
        (r"\breturn\b", 1.5),
        (r"\bcancel\b", 2.5),
        (r"\bchange.*engrav", 3.0),
        (r"\bwrong\s*text\b", 3.0),
        (r"\bcheckout\b", 2.5),
        (r"\bdiscount\s*code\b", 3.0),
        (r"\bneed\s*it\s*by\b", 3.0),
    ],
}


def _score_text(text: str, keyword_map: dict[str, list[tuple[str, float]]]) -> dict[str, float]:
    """Score *text* against every persona in *keyword_map* and return a
    ``{persona: total_weight}`` mapping.
    """
    text_lower = text.lower()
    scores: dict[str, float] = {}
    for persona, patterns in keyword_map.items():
        total = 0.0
        for pattern, weight in patterns:
            if re.search(pattern, text_lower):
                total += weight
        scores[persona] = total
    return scores


def _softmax_to_confidence(scores: dict[str, float], winning_persona: str) -> float:
    """Derive a pseudo-confidence from keyword scores using simple normalisation.

    If the winning score is S_w and the sum of all positive scores is S_total,
    confidence ≈ S_w / S_total, scaled into [0.4, 0.95] for rule-based.
    """
    total = sum(max(v, 0) for v in scores.values())
    if total == 0:
        return 0.5
    raw = scores.get(winning_persona, 0) / total
    return round(0.4 + 0.55 * raw, 3)


def classify_persona_rule_based(
    subject: str,
    message_body: str,
) -> PersonaResult:
    """Classify ticket persona using deterministic keyword matching.

    This is the fallback classifier used when the LLM API is unavailable.
    It uses weighted regex patterns per persona to score the combined
    ``subject + message_body`` text.

    Args:
        subject: The ticket subject line.
        message_body: The full message body.

    Returns:
        A :class:`PersonaResult` with ``method='rule_based'``.
    """
    combined = f"{subject} {message_body}"

    scores = _score_text(combined, _PERSONA_KEYWORDS)

    # If nothing matched, default to 'prospect' with low confidence
    if all(v == 0 for v in scores.values()):
        return PersonaResult(
            persona="prospect",
            confidence=0.3,
            method="rule_based",
            all_scores={k: 0.0 for k in BUYER_PERSONAS},
        )

    best_persona = max(scores, key=lambda k: scores[k])
    confidence = _softmax_to_confidence(scores, best_persona)

    all_scores = {k: round(v, 3) for k, v in scores.items()}

    return PersonaResult(
        persona=best_persona,
        confidence=confidence,
        method="rule_based",
        all_scores=all_scores,
    )


# ---------------------------------------------------------------------------
# LLM-Based Classifier
# ---------------------------------------------------------------------------

_PERSONA_SYSTEM_PROMPT = """\
You are a buyer-persona classifier for BOLDR Supply Co., a Singapore-based watch \
micro-brand. You receive a ticket subject and message body and must output a \
JSON object with exactly these keys:

- "persona": one of {personas}
- "confidence": float 0.0–1.0

Persona definitions:
- "health_conscious": Customer is concerned about material safety, allergens, \
skin reactions, toxicity, chemical composition, or certification standards. \
They ask "Is this safe for my skin?" type questions.
- "gifter": Customer is buying as a gift for someone else. They ask about \
engraving, packaging, delivery timing for a birthday/anniversary, or use \
gift-related language.
- "enthusiast": Knowledgeable watch enthusiast asking technical questions about \
straps, servicing, water resistance, movement specs, or compatibility. They \
often own the watch already.
- "niche_buyer": Collector or specialist asking niche/spec questions that are \
outside the normal KB — magnetic resistance, luminous materials, COSC \
certification, vintage/heritage, or collaboration availability.
- "owner_aftercare": Existing owner asking about after-purchase care — servicing, \
warranty, repairs, water-resistance testing, battery replacement. They mention \
owning or having a BOLDR watch.
- "prospect": Pre-purchase prospect asking about pricing, availability, \
comparisons, return policies, wholesale/bulk orders, or model recommendations.
- "transactional": Customer focused on logistics — order status, shipping, \
tracking, customs duties, delivery timing, cancellations, or fixing order \
issues. Their concern is "where is my thing" or "how do I get it fast".

Guidelines:
- Prioritise the PRIMARY intent. If someone asks about engraving timing because \
they need it for a gift, the persona is "gifter" not "transactional".
- If someone asks about strap material safety, they are "health_conscious" \
not "enthusiast".
- If someone asks about servicing their existing watch, they are \
"owner_aftercare" not "enthusiast".
- Return ONLY the JSON object, no additional text.
""".format(
    personas=json.dumps(BUYER_PERSONAS),
)


def classify_persona_llm(
    subject: str,
    message_body: str,
    *,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
) -> PersonaResult:
    """Classify ticket persona using GLM-5.1 via an OpenAI-compatible API.

    The LLM is prompted to return structured JSON with persona and confidence.
    If the LLM call fails or returns unparseable output, the function falls
    back to the rule-based classifier and logs a warning.

    Args:
        subject: The ticket subject line.
        message_body: The full message body.
        api_key: OpenAI-compatible API key. Falls back to ``GLM_API_KEY`` or
            ``OPENAI_API_KEY`` environment variable.
        base_url: API base URL. Falls back to ``GLM_BASE_URL`` env var or
            ``https://open.bigmodel.cn/api/paas/v4``.
        model: Model name. Falls back to ``GLM_MODEL`` env var or ``glm-5.1``.

    Returns:
        A :class:`PersonaResult` with ``method='llm'`` on success, or
        ``method='rule_based'`` on fallback.
    """
    api_key = api_key or os.getenv("GLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = base_url or os.getenv("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
    model = model or os.getenv("GLM_MODEL", "glm-5.1")

    if not api_key:
        logger.warning("No API key available; falling back to rule-based classifier.")
        return classify_persona_rule_based(subject, message_body)

    user_content = f"Subject: {subject}\n\nMessage:\n{message_body}"

    try:
        client = OpenAI(api_key=api_key, base_url=base_url, timeout=30.0)
        # Ollama doesn't support response_format=json_object, so we omit it
        # and instruct the model to return JSON via the system prompt instead.
        extra_kwargs = {}
        if "bigmodel" in (base_url or ""):
            # Only use response_format for the official GLM API
            extra_kwargs["response_format"] = {"type": "json_object"}
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _PERSONA_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.0,
            **extra_kwargs,
        )
        raw = response.choices[0].message.content.strip()
        # Handle GLM-5.1:cloud reasoning mode
        if not raw:
            reasoning = getattr(response.choices[0].message, 'reasoning_content', None) or getattr(response.choices[0].message, 'reasoning', None)
            if reasoning:
                import re
                json_match = re.search(r'\{[^}]+\}', reasoning)
                if json_match:
                    raw = json_match.group(0)
                else:
                    logger.warning("LLM returned empty content with reasoning but no JSON; falling back to rule-based.")
                    return classify_persona_rule_based(subject, message_body)
            else:
                logger.warning("LLM returned empty content; falling back to rule-based.")
                return classify_persona_rule_based(subject, message_body)
        # Strip <think>...</think> blocks if present
        import re
        raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
        json_match = re.search(r'```json\s*(.*?)\s*```', raw, re.DOTALL)
        if json_match:
            raw = json_match.group(1)
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            raw = json_match.group(0)
        parsed = json.loads(raw)

        persona = parsed.get("persona", "")
        if persona not in BUYER_PERSONAS:
            logger.warning("LLM returned unknown persona '%s'; falling back to rule-based.", persona)
            return classify_persona_rule_based(subject, message_body)

        confidence = float(parsed.get("confidence", 0.5))
        confidence = max(0.0, min(1.0, confidence))

        return PersonaResult(
            persona=persona,
            confidence=confidence,
            method="llm",
            all_scores=None,
            raw_llm_response=raw,
        )

    except json.JSONDecodeError as exc:
        logger.warning("LLM returned invalid JSON (%s); falling back to rule-based.", exc)
        return classify_persona_rule_based(subject, message_body)
    except Exception as exc:
        logger.warning("LLM call failed (%s: %s); falling back to rule-based.", type(exc).__name__, exc)
        return classify_persona_rule_based(subject, message_body)


# ---------------------------------------------------------------------------
# Unified Classifier
# ---------------------------------------------------------------------------


def classify_persona(
    subject: str,
    message_body: str,
    *,
    prefer_llm: bool = True,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
) -> PersonaResult:
    """Classify a BOLDR ticket's buyer persona.

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
        A :class:`PersonaResult` with the best available classification.
    """
    if prefer_llm:
        result = classify_persona_llm(
            subject,
            message_body,
            api_key=api_key,
            base_url=base_url,
            model=model,
        )
        if result.method == "llm" and result.is_confident():
            return result
        logger.info("LLM result not confident (persona=%s, conf=%.2f); using rule-based fallback.",
                     result.persona, result.confidence)

    return classify_persona_rule_based(subject, message_body)


# ---------------------------------------------------------------------------
# Test / Validation
# ---------------------------------------------------------------------------


def _run_tests(dataset_path: str | None = None) -> None:
    """Validate the persona classifier against the 70-ticket dataset.

    Runs the rule-based classifier over all tickets and prints per-persona
    accuracy and overall accuracy.  This function is invoked when the
    module is run directly::

        python -m app.classifier.persona

    Args:
        dataset_path: Path to the CSV dataset. Defaults to the project's
            ``01_customer_tickets.csv``.
    """
    import csv
    from pathlib import Path

    if dataset_path is None:
        dataset_path = str(
            Path(__file__).resolve().parents[3] / "dataset" / "01_customer_tickets.csv"
        )

    if not Path(dataset_path).exists():
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

    correct = 0
    total = len(rows)
    per_persona_correct: dict[str, int] = {p: 0 for p in BUYER_PERSONAS}
    per_persona_total: dict[str, int] = {p: 0 for p in BUYER_PERSONAS}

    misclassified = []

    for row in rows:
        subject = row.get("subject", "")
        message = row.get("message_body", "")
        expected = row.get("buyer_persona", "")

        result = classify_persona_rule_based(subject, message)

        per_persona_total[expected] = per_persona_total.get(expected, 0) + 1

        if result.persona == expected:
            correct += 1
            per_persona_correct[expected] = per_persona_correct.get(expected, 0) + 1
        else:
            misclassified.append({
                "ticket_id": row.get("ticket_id", "?"),
                "expected": expected,
                "predicted": result.persona,
                "subject": subject[:60],
            })

    print(f"\n{'BUYER PERSONA CLASSIFICATION':^70}")
    print("-" * 70)
    for persona in BUYER_PERSONAS:
        total_p = per_persona_total.get(persona, 0)
        correct_p = per_persona_correct.get(persona, 0)
        pct = (correct_p / total_p * 100) if total_p > 0 else 0
        print(f"  {persona:<25} {correct_p:>3}/{total_p:>3}  ({pct:5.1f}%)")

    print("-" * 70)
    print(f"  {'OVERALL':<25} {correct:>3}/{total:>3}  ({correct/total*100:5.1f}%)")

    if misclassified:
        print(f"\n{'MISCLASSIFIED TICKETS':^70}")
        print("-" * 70)
        for m in misclassified:
            print(f"  {m['ticket_id']:>10}  expected={m['expected']:<20} predicted={m['predicted']:<20}  \"{m['subject']}\"")

    print("\n" + "=" * 70)
    print("Persona classifier validation complete (rule-based).")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _run_tests()