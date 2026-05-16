"""
BOLDR Self-Improving Customer Intelligence Engine
FastAPI Application — Serves the intelligence loop API for n8n integration

Author: Steve Ng, Founder and CEO - Digital Futures Consultancy LLP
"""

import logging
import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.kb.schemas import (
    QuestionType, BuyerPersona, AnswerabilityResult, Channel,
    ClassificationResult, GapResult,
)
from app.kb.retriever import KBRetriever
from app.classifier.intent import IntentClassifier
from app.classifier.persona import PersonaTagger
from app.intelligence.gap_detector import GapDetector
from app.intelligence.theme_clusterer import ThemeClusterer
from app.generator.reply import ReplyGenerator, KBAutoDrafter
from app.routing.sop_parser import SOPParser
from app.routing.channel_router import ChannelRouter

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="BOLDR Self-Improving Customer Intelligence Engine",
    description="API for the BOLDR customer intelligence engine — ECHELON 2026 AI Workflow Competition",
    version="1.0.0",
    author="Steve Ng, Founder and CEO - Digital Futures Consultancy LLP",
)

# CORS middleware for n8n integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
retriever = KBRetriever()
intent_classifier = IntentClassifier()
persona_tagger = PersonaTagger()
gap_detector = GapDetector()
theme_clusterer = ThemeClusterer()
reply_generator = ReplyGenerator()
kb_drafter = KBAutoDrafter()
sop_parser = SOPParser()
channel_router = ChannelRouter()


# --- Request/Response Models ---

class IntakeMessage(BaseModel):
    """Normalised intake message from any channel."""
    message: str = Field(..., description="Customer message text")
    subject: str = Field("", description="Subject line (email only)")
    channel: str = Field(..., description="Channel: email, instagram_dm, whatsapp, chat")
    sender_id: str = Field("", description="Sender identifier")
    sender_name: str = Field("there", description="Sender display name")
    timestamp: str = Field("", description="ISO 8601 timestamp")
    thread_id: str = Field("", description="Conversation thread ID")
    source_id: str = Field("", description="Original message ID from channel")


class IntentRequest(BaseModel):
    """Request for intent classification."""
    message: str = Field(..., description="Customer message")
    subject: str = Field("", description="Email subject line")


class IntentResponse(BaseModel):
    """Response from intent classification."""
    ticket_id: str
    question_type: str
    buyer_persona: str
    confidence: float
    is_answerable: bool
    answerability_type: str
    escalation_required: bool
    escalation_reason: Optional[str] = None
    sop_routing: str
    needs_shopify: bool


class KBSearchRequest(BaseModel):
    """Request for KB search."""
    query: str = Field(..., description="Search query")
    n_results: int = Field(5, description="Number of results to return")


class KBSearchResult(BaseModel):
    """Single KB search result."""
    content: str
    source: str
    category: str
    score: float


class ReplyRequest(BaseModel):
    """Request for reply drafting."""
    ticket_id: str
    customer_name: str = "there"
    subject: str = ""
    question_type: str
    persona: str
    kb_answer: str
    sop_routing: str = ""
    channel: str = "email"
    confidence: float = 1.0


class GapLogRequest(BaseModel):
    """Request to log a knowledge gap."""
    ticket_id: str
    theme: str
    persona: str
    question: str


class KBEntryApproval(BaseModel):
    """Request to approve an auto-drafted KB entry."""
    entry_id: str
    approved: bool = True


# --- API Endpoints ---

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "BOLDR Intelligence Engine",
        "version": "1.0.0",
        "author": "Steve Ng, Founder and CEO - Digital Futures Consultancy LLP",
    }


@app.post("/api/v1/intake", response_model=IntentResponse)
async def process_intake(message: IntakeMessage):
    """Process an incoming message through the full intelligence loop.

    This is the main endpoint called by n8n workflows.
    """
    # Route the message (check for escalation)
    routing = channel_router.route(message.dict())

    # Classify intent and persona
    classification = intent_classifier.classify(
        message=message.message,
        subject=message.subject,
    )

    # Tag persona
    persona_tag = persona_tagger.tag(
        message=message.message,
        subject=message.subject,
        channel=message.channel,
    )

    # Check KB for answer
    kb_results = retriever.search(message.message, n_results=3)
    best_score = kb_results[0]["score"] if kb_results else 0.0

    # Determine answerability
    answerability = gap_detector.determine_answerability(
        classification, kb_confidence=best_score
    )

    # Get SOP routing
    sop_routing = sop_parser.get_routing(classification.question_type)

    return IntentResponse(
        ticket_id=classification.ticket_id,
        question_type=classification.question_type,
        buyer_persona=persona_tag,
        confidence=classification.confidence,
        is_answerable=answerability in (AnswerabilityResult.ANSWERABLE, AnswerabilityResult.NEEDS_SHOPIFY),
        answerability_type=answerability.value,
        escalation_required=routing["escalation"] or classification.escalation_required,
        escalation_reason=routing.get("escalation_reason") or classification.escalation_reason,
        sop_routing=sop_routing["source"] if sop_routing else "N/A",
        needs_shopify=sop_parser.requires_shopify(classification.question_type),
    )


@app.post("/api/v1/intent", response_model=IntentResponse)
async def classify_intent(request: IntentRequest):
    """Classify intent and persona for a message (standalone endpoint)."""
    classification = intent_classifier.classify(
        message=request.message,
        subject=request.subject,
    )

    persona_tag = persona_tagger.tag(
        message=request.message,
        subject=request.subject,
    )

    sop_routing = sop_parser.get_routing(classification.question_type)

    return IntentResponse(
        ticket_id=classification.ticket_id,
        question_type=classification.question_type,
        buyer_persona=persona_tag,
        confidence=classification.confidence,
        is_answerable=classification.is_answerable,
        answerability_type=classification.answerability_type,
        escalation_required=classification.escalation_required,
        escalation_reason=classification.escalation_reason,
        sop_routing=sop_routing["source"] if sop_routing else "N/A",
        needs_shopify=sop_parser.requires_shopify(classification.question_type),
    )


@app.post("/api/v1/kb/search")
async def search_kb(request: KBSearchRequest):
    """Search the knowledge base."""
    results = retriever.search(request.query, n_results=request.n_results)
    return {"results": results, "count": len(results)}


@app.post("/api/v1/reply/draft")
async def draft_reply(request: ReplyRequest):
    """Draft a reply in BOLDR brand voice."""
    reply = reply_generator.draft_reply(
        ticket_id=request.ticket_id,
        customer_name=request.customer_name,
        subject=request.subject,
        question_type=request.question_type,
        persona=request.persona,
        kb_answer=request.kb_answer,
        sop_routing=request.sop_routing,
        channel=request.channel,
        confidence=request.confidence,
    )
    return reply


@app.post("/api/v1/gap/log")
async def log_gap(request: GapLogRequest):
    """Log a knowledge gap ticket."""
    theme_clusterer.add_ticket(
        ticket_id=request.ticket_id,
        theme=request.theme,
        persona=request.persona,
        question=request.question,
    )
    return {"status": "logged", "ticket_id": request.ticket_id, "theme": request.theme}


@app.get("/api/v1/themes/weekly")
async def get_weekly_themes():
    """Get the weekly theme clustering report."""
    return theme_clusterer.get_weekly_theme_report()


@app.get("/api/v1/themes/monthly-brief")
async def get_monthly_brief():
    """Get the monthly marketing intelligence brief."""
    return theme_clusterer.get_monthly_marketing_brief()


@app.post("/api/v1/kb/auto-draft")
async def auto_draft_kb(question: str, answer: str, theme: str, persona: str):
    """Auto-draft a KB entry from a resolved gap."""
    entry = kb_drafter.draft_entry(
        question=question,
        answer=answer,
        theme=theme,
        persona=persona,
    )
    return entry


@app.get("/api/v1/sop/routing/{question_type}")
async def get_sop_routing(question_type: str):
    """Get SOP routing for a question type."""
    routing = sop_parser.get_routing(question_type)
    if not routing:
        raise HTTPException(status_code=404, detail=f"No routing for question type: {question_type}")
    return routing


@app.get("/api/v1/sop/tone")
async def get_tone_guidelines():
    """Get BOLDR brand voice tone guidelines."""
    return {"tone_guidelines": sop_parser.get_tone_prompt()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)