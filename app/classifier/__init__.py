"""
BOLDR Classifier Package

Provides intent classification (question type + routing) and buyer persona
tagging for inbound customer support tickets.

Quick Start::

    from app.classifier import classify_intent, classify_persona

    result = classify_intent("Strap compatibility", "Do you sell rubber straps?")
    print(result.question_type)       # 'strap_compatibility'
    print(result.routing_intent)      # 'kb_answerable'

    persona = classify_persona("Strap compatibility", "Do you sell rubber straps?")
    print(persona.persona)            # 'enthusiast'

Modules:
    - intent:  Question type + routing classification
    - persona: Buyer persona tagging
"""

from app.classifier.intent import (
    IntentResult,
    classify_intent,
    classify_intent_llm,
    classify_intent_rule_based,
    QUESTION_TYPES,
    ROUTING_INTENTS,
)

from app.classifier.persona import (
    PersonaResult,
    classify_persona,
    classify_persona_llm,
    classify_persona_rule_based,
    BUYER_PERSONAS,
)

__all__ = [
    # Intent classification
    "IntentResult",
    "classify_intent",
    "classify_intent_llm",
    "classify_intent_rule_based",
    "QUESTION_TYPES",
    "ROUTING_INTENTS",
    # Persona classification
    "PersonaResult",
    "classify_persona",
    "classify_persona_llm",
    "classify_persona_rule_based",
    "BUYER_PERSONAS",
]