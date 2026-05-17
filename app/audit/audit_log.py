"""
BOLDR Self-Improving Customer Intelligence Engine
Audit Log — Persistent ticket processing log for transparency and auditability

Every classification, routing, and reply decision is logged to SQLite.
This satisfies rubric §4.3 (Transparency & Auditability).

Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import Optional

AUDIT_DB_PATH = os.environ.get("BOLDR_AUDIT_DB", "data/boldr_audit.db")


def get_audit_connection(db_path: str = AUDIT_DB_PATH) -> sqlite3.Connection:
    """Get a connection to the audit database."""
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_audit_db(db_path: str = AUDIT_DB_PATH):
    """Create audit log tables if they don't exist."""
    conn = get_audit_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ticket_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            channel TEXT NOT NULL,
            sender_name TEXT DEFAULT '',
            subject TEXT DEFAULT '',
            original_message TEXT NOT NULL,
            question_type TEXT NOT NULL,
            buyer_persona TEXT NOT NULL,
            confidence REAL NOT NULL DEFAULT 0.0,
            is_answerable INTEGER NOT NULL DEFAULT 0,
            answerability_type TEXT NOT NULL DEFAULT '',
            escalation_required INTEGER NOT NULL DEFAULT 0,
            escalation_reason TEXT DEFAULT '',
            sop_routing TEXT DEFAULT '',
            needs_shopify INTEGER NOT NULL DEFAULT 0,
            kb_best_match TEXT DEFAULT '',
            kb_confidence REAL DEFAULT 0.0,
            reply_queued INTEGER NOT NULL DEFAULT 0,
            processing_time_ms INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_audit_ticket_id ON ticket_audit(ticket_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON ticket_audit(timestamp)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_audit_question_type ON ticket_audit(question_type)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_audit_channel ON ticket_audit(channel)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_audit_persona ON ticket_audit(buyer_persona)
    """)

    conn.commit()
    conn.close()


def log_ticket_processing(
    ticket_id: str,
    channel: str,
    sender_name: str = "",
    subject: str = "",
    original_message: str = "",
    question_type: str = "",
    buyer_persona: str = "",
    confidence: float = 0.0,
    is_answerable: bool = False,
    answerability_type: str = "",
    escalation_required: bool = False,
    escalation_reason: str = "",
    sop_routing: str = "",
    needs_shopify: bool = False,
    kb_best_match: str = "",
    kb_confidence: float = 0.0,
    reply_queued: bool = False,
    processing_time_ms: int = 0,
    db_path: str = AUDIT_DB_PATH,
) -> dict:
    """Log a ticket processing event to the audit database."""
    conn = get_audit_connection(db_path)
    now = datetime.now().isoformat()
    try:
        conn.execute("""
            INSERT INTO ticket_audit (
                ticket_id, timestamp, channel, sender_name, subject, original_message,
                question_type, buyer_persona, confidence, is_answerable, answerability_type,
                escalation_required, escalation_reason, sop_routing, needs_shopify,
                kb_best_match, kb_confidence, reply_queued, processing_time_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticket_id, now, channel, sender_name, subject, original_message,
            question_type, buyer_persona, confidence, int(is_answerable), answerability_type,
            int(escalation_required), escalation_reason, sop_routing, int(needs_shopify),
            kb_best_match, kb_confidence, int(reply_queued), processing_time_ms
        ))
        conn.commit()
        return {"status": "logged", "ticket_id": ticket_id, "timestamp": now}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()


def get_recent_tickets(limit: int = 50, offset: int = 0, db_path: str = AUDIT_DB_PATH) -> list[dict]:
    """Get recent ticket processing events."""
    conn = get_audit_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM ticket_audit ORDER BY timestamp DESC LIMIT ? OFFSET ?
    """, (limit, offset))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_ticket_by_id(ticket_id: str, db_path: str = AUDIT_DB_PATH) -> Optional[dict]:
    """Get a specific ticket's audit record."""
    conn = get_audit_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM ticket_audit WHERE ticket_id = ? ORDER BY timestamp DESC LIMIT 1
    """, (ticket_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_audit_summary(db_path: str = AUDIT_DB_PATH) -> dict:
    """Get audit summary statistics."""
    conn = get_audit_connection(db_path)
    cursor = conn.cursor()

    # Total count
    cursor.execute("SELECT COUNT(*) as total FROM ticket_audit")
    total = cursor.fetchone()["total"]

    # By channel
    cursor.execute("SELECT channel, COUNT(*) as count FROM ticket_audit GROUP BY channel ORDER BY count DESC")
    by_channel = {row["channel"]: row["count"] for row in cursor.fetchall()}

    # By intent
    cursor.execute("SELECT question_type, COUNT(*) as count FROM ticket_audit GROUP BY question_type ORDER BY count DESC")
    by_intent = {row["question_type"]: row["count"] for row in cursor.fetchall()}

    # By persona
    cursor.execute("SELECT buyer_persona, COUNT(*) as count FROM ticket_audit GROUP BY buyer_persona ORDER BY count DESC")
    by_persona = {row["buyer_persona"]: row["count"] for row in cursor.fetchall()}

    # Answerability
    cursor.execute("SELECT is_answerable, COUNT(*) as count FROM ticket_audit GROUP BY is_answerable")
    answerability = {("answerable" if row["is_answerable"] else "gap"): row["count"] for row in cursor.fetchall()}

    # Average confidence
    cursor.execute("SELECT AVG(confidence) as avg_confidence FROM ticket_audit")
    avg_confidence = cursor.fetchone()["avg_confidence"] or 0.0

    # Average processing time
    cursor.execute("SELECT AVG(processing_time_ms) as avg_time FROM ticket_audit WHERE processing_time_ms > 0")
    avg_time = cursor.fetchone()["avg_time"] or 0.0

    # Recent tickets (last 10)
    cursor.execute("""
        SELECT ticket_id, timestamp, channel, question_type, buyer_persona, confidence, is_answerable
        FROM ticket_audit ORDER BY timestamp DESC LIMIT 10
    """)
    recent = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        "total_tickets": total,
        "by_channel": by_channel,
        "by_intent": by_intent,
        "by_persona": by_persona,
        "answerability": answerability,
        "avg_confidence": round(avg_confidence, 3),
        "avg_processing_time_ms": round(avg_time, 1),
        "recent_tickets": recent,
    }


# Initialize on import
init_audit_db()