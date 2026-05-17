"""
BOLDR Self-Improving Customer Intelligence Engine
Reply Approval Queue — SQLite-backed persistent queue for human approval

Every drafted reply requires explicit human approval before sending.
No auto-send. This is the persistence layer for that approval workflow.

Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field, asdict

DB_PATH = os.environ.get("BOLDR_QUEUE_DB", "data/boldr_queue.db")


@dataclass
class QueuedReply:
    """A reply drafted by the Intelligence Engine, awaiting human approval."""
    ticket_id: str
    question_type: str
    persona: str
    channel: str
    customer_name: str
    subject: str
    original_message: str
    draft_reply: str
    confidence: float
    is_answerable: bool
    sop_routing: str = ""
    needs_shopify: bool = False
    status: str = "pending"  # pending, approved, rejected, edited
    created_at: str = ""
    updated_at: str = ""
    approved_by: str = ""
    edited_reply: str = ""


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Get a connection to the SQLite database, creating it if needed."""
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(db_path: str = DB_PATH):
    """Create the approval queue tables if they don't exist."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reply_queue (
            ticket_id TEXT PRIMARY KEY,
            question_type TEXT NOT NULL,
            persona TEXT NOT NULL,
            channel TEXT NOT NULL,
            customer_name TEXT NOT NULL DEFAULT 'there',
            subject TEXT NOT NULL DEFAULT '',
            original_message TEXT NOT NULL,
            draft_reply TEXT NOT NULL,
            confidence REAL NOT NULL DEFAULT 0.0,
            is_answerable INTEGER NOT NULL DEFAULT 1,
            sop_routing TEXT NOT NULL DEFAULT '',
            needs_shopify INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'edited')),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            approved_by TEXT NOT NULL DEFAULT '',
            edited_reply TEXT NOT NULL DEFAULT ''
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kb_approval_queue (
            entry_id TEXT PRIMARY KEY,
            question TEXT NOT NULL,
            suggested_answer TEXT NOT NULL,
            theme TEXT NOT NULL,
            persona TEXT NOT NULL,
            source_ticket_id TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            approved_by TEXT NOT NULL DEFAULT ''
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reply_status ON reply_queue(status)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_kb_status ON kb_approval_queue(status)
    """)

    conn.commit()
    conn.close()


def enqueue_reply(reply: QueuedReply, db_path: str = DB_PATH) -> dict:
    """Add a drafted reply to the approval queue."""
    conn = get_connection(db_path)
    now = datetime.now().isoformat()
    if not reply.created_at:
        reply.created_at = now
    reply.updated_at = now

    try:
        conn.execute("""
            INSERT OR REPLACE INTO reply_queue
            (ticket_id, question_type, persona, channel, customer_name, subject,
             original_message, draft_reply, confidence, is_answerable, sop_routing,
             needs_shopify, status, created_at, updated_at, approved_by, edited_reply)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            reply.ticket_id, reply.question_type, reply.persona, reply.channel,
            reply.customer_name, reply.subject, reply.original_message,
            reply.draft_reply, reply.confidence, int(reply.is_answerable),
            reply.sop_routing, int(reply.needs_shopify), reply.status,
            reply.created_at, reply.updated_at, reply.approved_by, reply.edited_reply
        ))
        conn.commit()
        return {"status": "queued", "ticket_id": reply.ticket_id, "queued_at": now}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()


def get_pending_replies(db_path: str = DB_PATH) -> list[dict]:
    """Get all pending replies awaiting approval."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM reply_queue WHERE status = 'pending' ORDER BY created_at DESC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_all_replies(status: Optional[str] = None, db_path: str = DB_PATH) -> list[dict]:
    """Get all replies, optionally filtered by status."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    if status:
        cursor.execute("""
            SELECT * FROM reply_queue WHERE status = ? ORDER BY created_at DESC
        """, (status,))
    else:
        cursor.execute("""
            SELECT * FROM reply_queue ORDER BY created_at DESC
        """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def approve_reply(ticket_id: str, approved_by: str = "", edited_reply: str = "", db_path: str = DB_PATH) -> dict:
    """Approve a queued reply. If edited_reply is provided, the reply was edited before approval."""
    conn = get_connection(db_path)
    now = datetime.now().isoformat()
    try:
        if edited_reply:
            conn.execute("""
                UPDATE reply_queue SET status = 'approved', approved_by = ?,
                edited_reply = ?, updated_at = ? WHERE ticket_id = ?
            """, (approved_by, edited_reply, now, ticket_id))
        else:
            conn.execute("""
                UPDATE reply_queue SET status = 'approved', approved_by = ?,
                updated_at = ? WHERE ticket_id = ?
            """, (approved_by, now, ticket_id))
        conn.commit()
        return {"status": "approved", "ticket_id": ticket_id, "approved_at": now, "approved_by": approved_by}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()


def reject_reply(ticket_id: str, rejected_by: str = "", db_path: str = DB_PATH) -> dict:
    """Reject a queued reply."""
    conn = get_connection(db_path)
    now = datetime.now().isoformat()
    try:
        conn.execute("""
            UPDATE reply_queue SET status = 'rejected', approved_by = ?,
            updated_at = ? WHERE ticket_id = ?
        """, (rejected_by, now, ticket_id))
        conn.commit()
        return {"status": "rejected", "ticket_id": ticket_id, "rejected_at": now}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()


def enqueue_kb_entry(entry_id: str, question: str, answer: str, theme: str, persona: str, source_ticket_id: str, db_path: str = DB_PATH) -> dict:
    """Add an auto-drafted KB entry to the approval queue."""
    conn = get_connection(db_path)
    now = datetime.now().isoformat()
    try:
        conn.execute("""
            INSERT OR REPLACE INTO kb_approval_queue
            (entry_id, question, suggested_answer, theme, persona, source_ticket_id,
             status, created_at, updated_at, approved_by)
            VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?, '')
        """, (entry_id, question, answer, theme, persona, source_ticket_id, now, now))
        conn.commit()
        return {"status": "queued", "entry_id": entry_id, "queued_at": now}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()


def get_pending_kb_entries(db_path: str = DB_PATH) -> list[dict]:
    """Get all pending KB entries awaiting approval."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM kb_approval_queue WHERE status = 'pending' ORDER BY created_at DESC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def approve_kb_entry(entry_id: str, approved_by: str = "", db_path: str = DB_PATH) -> dict:
    """Approve an auto-drafted KB entry."""
    conn = get_connection(db_path)
    now = datetime.now().isoformat()
    try:
        conn.execute("""
            UPDATE kb_approval_queue SET status = 'approved', approved_by = ?,
            updated_at = ? WHERE entry_id = ?
        """, (approved_by, now, entry_id))
        conn.commit()
        return {"status": "approved", "entry_id": entry_id, "approved_at": now}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()


# Initialize the database on module import
init_db()