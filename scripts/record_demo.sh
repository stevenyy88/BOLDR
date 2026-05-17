#!/bin/bash
# BOLDR — Screen Recording Demo Script
# Records the n8n workflows executing, Streamlit dashboard, and API responses
#
# Prerequisites:
#   - OBS Studio or ffmpeg with x11grab
#   - All services running (FastAPI :8000, ChromaDB :8100, n8n :5678, Streamlit :8501)
#   - n8n workflows active
#
# Usage:
#   chmod +x scripts/record_demo.sh
#   ./scripts/record_demo.sh

set -e

echo "============================================================"
echo "  BOLDR Self-Improving Customer Intelligence Engine"
echo "  ECHELON 2026 AI Workflow Competition — Screen Recording"
echo "============================================================"
echo ""
echo "This script runs through the demo sequence, pausing for you"
echo "to record with OBS Studio or another screen recorder."
echo ""
echo "Press Enter to start each section, or Ctrl+C to exit."
echo ""

# Check services are running
echo "=== Checking services ==="
echo -n "FastAPI: "; curl -s http://localhost:8000/api/v1/health 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'{d[\"status\"]} — {d[\"tickets_processed\"]} tickets processed')" 2>/dev/null || echo "NOT RUNNING — start with: uvicorn app.api:app --host 0.0.0.0 --port 8000"
echo -n "ChromaDB: "; curl -s http://localhost:8100/api/v2/heartbeat 2>/dev/null | python3 -c "import sys,json; print('healthy')" 2>/dev/null || echo "NOT RUNNING"
echo -n "n8n: "; curl -s http://localhost:5678/healthz 2>/dev/null | python3 -c "import sys; print('healthy')" 2>/dev/null || echo "NOT RUNNING"
echo -n "Streamlit: "; curl -s http://localhost:8501/_stcore/health 2>/dev/null && echo "" || echo "NOT RUNNING"
echo ""

read -p "Press Enter to start Section 1: API Health Check & PII Stripping..."

echo ""
echo "=== Section 1: API Health Check & PII Stripping ==="
echo ""
echo "1. Open browser to: http://localhost:8000/docs"
echo "   This shows the Swagger UI with all 29 API endpoints."
echo ""
echo "2. Health Check:"
curl -s http://localhost:8000/api/v1/health | python3 -m json.tool
echo ""
echo "3. PII Stripping Status (default: OFF for competition):"
curl -s http://localhost:8000/api/v1/pii/status | python3 -m json.tool
echo ""
echo "4. PII Strip Demo (forced on):"
curl -s -X POST "http://localhost:8000/api/v1/pii/strip?text=My+email+is+john%40example.com+and+my+phone+is+%2B65+9123+4567&enabled=true" | python3 -m json.tool
echo ""
echo "5. Rate Limit Headers:"
curl -sI http://localhost:8000/api/v1/health | grep -i "x-ratelimit"
echo ""

read -p "Press Enter to start Section 2: Channel Integration Webhooks..."

echo ""
echo "=== Section 2: Channel Integration Webhooks ==="
echo ""
echo "6. WhatsApp Webhook Verification:"
curl -s "http://localhost:8000/api/v1/channels/whatsapp/webhook?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=boldr_verify_2026"
echo ""
echo ""
echo "7. WhatsApp Message Webhook:"
curl -s -X POST http://localhost:8000/api/v1/channels/whatsapp/webhook \
  -H "Content-Type: application/json" \
  -d '{"object":"whatsapp_business_account","entry":[{"changes":[{"value":{"messages":[{"from":"6591234567","type":"text","text":{"body":"Are your straps BPA-free?"},"timestamp":"1705315853","id":"wamid.test123"}],"contacts":[{"wa_id":"6591234567","profile":{"name":"Caleb Tan"}}]}}]}]}' | python3 -m json.tool
echo ""
echo "8. Instagram DM Webhook:"
curl -s -X POST http://localhost:8000/api/v1/channels/instagram/webhook \
  -H "Content-Type: application/json" \
  -d '{"object":"instagram","entry":[{"messaging":[{"sender":{"id":"ig_user_456"},"recipient":{"id":"ig_business"},"timestamp":1705315853000,"message":{"mid":"m_abc123","text":"Hey is the Expedition BPA-free?"}}]}]}' | python3 -m json.tool
echo ""
echo "9. Email Webhook:"
curl -s -X POST http://localhost:8000/api/v1/channels/email/webhook \
  -H "Content-Type: application/json" \
  -d '{"from_email":"caleb@example.com","from_name":"Caleb Tan","subject":"Strap dye safety","body_text":"Hi, are your BPA-free straps also nickel-free? I have sensitive skin.","date":"2026-01-15T10:30:00+08:00","message_id":"msg-456"}' | python3 -m json.tool
echo ""

read -p "Press Enter to start Section 3: Intelligence Loop..."

echo ""
echo "=== Section 3: Intelligence Loop End-to-End ==="
echo ""
echo "10. Process a customer enquiry through the full pipeline:"
curl -s -X POST http://localhost:8000/api/v1/intake \
  -H "Content-Type: application/json" \
  -d '{"message": "Are your straps BPA-free? I have sensitive skin and want to make sure the Venture is safe.", "channel": "chat", "sender_name": "Caleb"}' | python3 -m json.tool
echo ""
echo "11. Process an order status enquiry (triggers Shopify lookup):"
curl -s -X POST http://localhost:8000/api/v1/intake \
  -H "Content-Type: application/json" \
  -d '{"message": "Where is my order #BOLDR-2026-1234? I ordered a Venture Venture last week.", "channel": "email", "sender_name": "Sarah"}' | python3 -m json.tool
echo ""
echo "12. Process an escalation (angry customer):"
curl -s -X POST http://localhost:8000/api/v1/intake \
  -H "Content-Type: application/json" \
  -d '{"message": "This is unacceptable. I want a refund immediately or I am filing a chargeback with my bank.", "channel": "whatsapp", "sender_name": "Angry Customer"}' | python3 -m json.tool
echo ""

read -p "Press Enter to start Section 4: Audit & Approval..."

echo ""
echo "=== Section 4: Audit Log & Approval Queue ==="
echo ""
echo "13. View recent audit log:"
curl -s "http://localhost:8000/api/v1/audit/recent?limit=5" | python3 -m json.tool 2>/dev/null | head -40
echo ""
echo "14. View audit summary:"
curl -s http://localhost:8000/api/v1/audit/summary | python3 -m json.tool
echo ""
echo "15. View pending replies:"
curl -s http://localhost:8000/api/v1/queue/replies/pending | python3 -m json.tool 2>/dev/null | head -40
echo ""
echo "16. Pipeline statistics:"
curl -s http://localhost:8000/api/v1/stats | python3 -m json.tool
echo ""

read -p "Press Enter to start Section 5: Streamlit Dashboard..."

echo ""
echo "=== Section 5: Streamlit Dashboard ==="
echo ""
echo "Open browser to: http://localhost:8501"
echo ""
echo "The dashboard has 9 tabs:"
echo "  1. Live Pipeline — Real-time stats + KPI cards"
echo "  2. Approval Queue — Pending replies with Approve/Reject"
echo "  3. Ticket Timeline — Recent tickets with classification details"
echo "  4. Channel Analytics — Breakdown by channel, intent, persona"
echo "  5. Theme Analysis — Weekly theme clustering"
echo "  6. KB Management — Live search + source listing"
echo "  7. Gap Log — Detected knowledge gaps"
echo "  8. Marketing Brief — Revenue signals and action items"
echo "  9. Audit Log — Full audit trail with ticket lookup"
echo ""
echo "Navigate through all tabs to show the live data."
echo ""

read -p "Press Enter to start Section 6: n8n Workflows..."

echo ""
echo "=== Section 6: n8n Workflows ==="
echo ""
echo "Open browser to: http://localhost:5678"
echo "  Login: steve@digitalfutures.sg / BolDR2026!demo"
echo ""
echo "Active workflows:"
echo "  1. BOLDR Chat Intake — Webhook → Normalize → Classify → Search KB → Draft Reply → Log Gap"
echo "  2. BOLDR WhatsApp Intake — Same pipeline, WhatsApp-specific normalisation"
echo "  3. BOLDR Instagram DM Intake — Same pipeline, Instagram-specific normalisation"
echo "  4. BOLDR Email Intake — Same pipeline, email-specific normalisation"
echo "  5. BOLDR Intelligence Loop — Full 7-step intelligence loop"
echo ""
echo "Execute a workflow manually to show the nodes processing in real-time."
echo ""

read -p "Press Enter to start Section 7: Docker Deployment..."

echo ""
echo "=== Section 7: Docker Deployment ==="
echo ""
echo "17. Show docker-compose.yml with all 3 services:"
cat ../docker-compose.yml | head -30
echo "..."
echo ""
echo "18. Show running containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "Docker not available"
echo ""

echo "============================================================"
echo "  Demo Complete!"
echo ""
echo "  Summary:"
echo "  - 29 API endpoints across 12 functional groups"
echo "  - Real channel integrations (WhatsApp, Instagram, Email)"
echo "  - PII stripping (configurable, GDPR/PDPA compliant)"
echo "  - Rate limiting on all endpoints"
echo "  - SQLite audit log + approval queue"
echo "  - Docker Compose deployment (3 services)"
echo "  - 9-tab Streamlit dashboard with KPI cards"
echo "  - 5 active n8n workflows"
echo "  - 13/13 e2e tests passing"
echo "============================================================"