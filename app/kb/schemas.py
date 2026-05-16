"""
BOLDR Self-Improving Customer Intelligence Engine
KB Data Schemas — Structured data models for all BOLDR knowledge sources

Author: Steve Ng, Founder and CEO - Digital Futures Consultancy LLP
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class QuestionType(Enum):
    """BOLDR ticket question types (from dataset)."""
    STRAP_COMPATIBILITY = "strap_compatibility"
    SERVICING = "servicing"
    PRODUCT_GENERAL = "product_general"
    ORDER_STATUS = "order_status"
    MATERIALS_SAFETY = "materials_safety"
    KNOWLEDGE_GAP = "knowledge_gap"
    ENGRAVING = "engraving"


class BuyerPersona(Enum):
    """BOLDR buyer personas (from dataset — 7 personas)."""
    HEALTH_CONSCIOUS = "health_conscious"
    GIFTER = "gifter"
    ENTHUSIAST = "enthusiast"
    NICHE_BUYER = "niche_buyer"
    OWNER_AFTERCARE = "owner_aftercare"
    PROSPECT = "prospect"
    TRANSACTIONAL = "transactional"


class TicketChannel(Enum):
    """BOLDR ticket channels."""
    EMAIL = "email"
    CHAT = "chat"
    INSTAGRAM_DM = "instagram_dm"
    WHATSAPP = "whatsapp"


class KBSource(Enum):
    """Knowledge base source documents."""
    PRODUCT_REFERENCE = "product_reference"
    RATE_CARD_ENGRAVING = "rate_card_engraving"
    RATE_CARD_SERVICING = "rate_card_servicing"
    FAQ_DOCUMENT = "faq_document"
    CS_SOP = "cs_sop"


class AnswerabilityResult(Enum):
    """Whether the KB can answer the ticket."""
    ANSWERABLE = "yes"
    NOT_ANSWERABLE = "no"
    NEEDS_SHOPIFY = "needs_shopify"  # Order operations requiring Shopify lookup


class EscalationReason(Enum):
    """SOP-defined escalation triggers."""
    ANGRY_CUSTOMER = "angry_customer"
    CHARGEBACK_THREAT = "chargeback_threat"
    WARRANTY_SIGNIFICANT_DAMAGE = "warranty_significant_damage"
    REFUND_OUTSTANDING_10_DAYS = "refund_outstanding_10_days"
    CORPORATE_BULK_ORDER = "corporate_bulk_order"
    MEDIA_PRESS = "media_press"
    UNCERTAIN_ANSWER = "uncertain_answer"


@dataclass
class CustomerTicket:
    """Structured model for a customer ticket."""
    ticket_id: str
    date_received: str
    customer_name: str
    customer_email: str
    order_id: Optional[str]
    channel: str
    question_type: str
    subject: str
    message_body: str
    status: str
    answered_by_kb: str
    requires_escalation: str
    buyer_persona: str
    agent_notes: Optional[str] = None


@dataclass
class KBDocument:
    """A document in the knowledge base."""
    id: str
    content: str
    metadata: dict = field(default_factory=dict)
    source_file: str = ""
    section: str = ""
    category: str = ""


@dataclass
class ClassificationResult:
    """Result of classifying a ticket."""
    ticket_id: str
    question_type: str
    buyer_persona: str
    confidence: float
    is_answerable: bool
    answerability_type: str  # 'kb_answer', 'shopify_lookup', 'knowledge_gap'
    escalation_required: bool
    escalation_reason: Optional[str] = None
    suggested_kb_sources: list = field(default_factory=list)


@dataclass
class KnowledgeGap:
    """A detected knowledge gap."""
    ticket_id: str
    question: str
    theme: str
    frequency: int = 1
    buyer_persona: str = ""
    marketing_signal: bool = False
    kb_draft_status: str = "pending"  # pending, drafted, approved, rejected
    suggested_answer: Optional[str] = None
    source_document: Optional[str] = None


@dataclass
class ModelSpec:
    """Product specification for a BOLDR watch model."""
    model_name: str
    sku: str
    price_sgd: float
    case_spec: str
    crystal: str
    movement: str
    water_resistance: str
    lume: str
    weight_grams: int
    dial_colours: list = field(default_factory=list)
    included_strap: str = ""
    strap_options: list = field(default_factory=list)
    lug_width_mm: int = 20
    safety: dict = field(default_factory=dict)
    warranty: str = ""
    availability: str = ""


@dataclass
class StrapEntry:
    """A strap catalogue entry."""
    sku: str
    strap_type: str
    colour: str
    bpa_free: bool
    price_sgd: float
    compatible_with: str


@dataclass
class EngravingService:
    """An engraving rate card entry."""
    service: str
    price_sgd: float
    notes: str


@dataclass
class ServicingTier:
    """A servicing rate card entry."""
    service_tier: str
    price_sgd: float
    turnaround_days: str
    includes: str
    notes: str


@dataclass
class FAQEntry:
    """A FAQ entry from the PDF."""
    category: str
    question: str
    answer: str


@dataclass
class SOPEscalationRule:
    """An escalation rule from the CS SOP."""
    trigger: str
    action: str
    contact: str = ""


@dataclass
class NewQuestionLogEntry:
    """An entry from the SOP's new questions log."""
    date: str
    question: str
    theme: str
    status: str


# Brief-defined buyer personas (5 from the challenge brief)
BRIEF_PERSONAS = {
    "Health-Conscious Buyer": {
        "triggers": ["BPA-free", "nickel-free", "hypoallergenic", "EU REACH", "safe for kids"],
        "marketing_action": "Product badge: BPA-Free Straps",
    },
    "Gifter": {
        "triggers": ["engraving", "gift wrap", "birthday", "anniversary", "turnaround time"],
        "marketing_action": "Seasonal campaign: Valentine's, Father's Day",
    },
    "Enthusiast / Collector": {
        "triggers": ["Grade 5 titanium", "Miyota movement", "limited editions"],
        "marketing_action": "Collector content: specs and craftsmanship",
    },
    "Active / Outdoor Buyer": {
        "triggers": ["water resistance", "shock", "trail running", "FKM rubber strap"],
        "marketing_action": "Segment: adventure lifestyle content",
    },
    "Sustainability Advocate": {
        "triggers": ["vegan straps", "carbon offset shipping", "eco packaging"],
        "marketing_action": "New: vegan strap angle to develop",
    },
}

# Dataset-derived buyer personas (7 from the ticket data)
DATASET_PERSONAS = {
    "health_conscious": {"label": "Health-Conscious Buyer", "count": 10},
    "gifter": {"label": "Gifter", "count": 10},
    "enthusiast": {"label": "Enthusiast / Collector", "count": 10},
    "niche_buyer": {"label": "Niche Buyer / Collector", "count": 10},
    "owner_aftercare": {"label": "Owner / Aftercare", "count": 10},
    "prospect": {"label": "Prospect", "count": 10},
    "transactional": {"label": "Transactional / Order Ops", "count": 10},
}