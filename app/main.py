"""
BOLDR Self-Improving Customer Intelligence Engine
Main Application Entry Point

Author: Steve Ng, Founder and CEO - Digital Futures Consultancy LLP
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the BOLDR Intelligence Engine."""
    logger.info("BOLDR Self-Improving Customer Intelligence Engine")
    logger.info("Author: Steve Ng, Founder and CEO - Digital Futures Consultancy LLP")
    logger.info("ECHELON 2026 AI Workflow Competition — REVENUE ROCKET Track")

    # Import modules
    from app.kb.indexer import KBIndexer
    from app.kb.retriever import KBRetriever
    from app.kb.schemas import QuestionType, BuyerPersona
    from app.classifier.intent import IntentClassifier
    from app.classifier.persona import PersonaTagger
    from app.intelligence.gap_detector import GapDetector
    from app.intelligence.theme_clusterer import ThemeClusterer
    from app.routing.sop_parser import SOPParser

    logger.info("All modules loaded successfully.")
    logger.info("Ready to process customer enquiries.")
    logger.info("Start the Streamlit dashboard: streamlit run app/dashboard/app.py")
    logger.info("Start n8n: docker compose up n8n")


if __name__ == "__main__":
    main()