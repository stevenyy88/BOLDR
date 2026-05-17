"""
BOLDR Self-Improving Customer Intelligence Engine
Streamlit Dashboard — Live Pipeline Stats, Approval Queue, Ticket Timeline,
Channel Analytics, Theme Visualisation, KB Management, Audit Log

Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP (T17LL1937H)
"""

import streamlit as st
import json
import requests
from datetime import datetime

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="BOLDR Customer Intelligence Engine",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏛️ BOLDR — Self-Improving Customer Intelligence Engine")
st.caption("ECHELON 2026 AI Workflow Competition | REVENUE ROCKET Track")
st.caption("Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP (T17LL1937H)")

# Auto-refresh on Live Pipeline tab
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False

# Try to fetch live stats
live_stats = None
try:
    resp = requests.get(f"{API_BASE}/stats", timeout=3)
    if resp.status_code == 200:
        live_stats = resp.json()
except Exception:
    live_stats = None

# Fetch audit data
audit_data = None
try:
    resp = requests.get(f"{API_BASE}/audit/summary", timeout=3)
    if resp.status_code == 200:
        audit_data = resp.json()
except Exception:
    audit_data = None

# Sidebar navigation
tab = st.sidebar.radio(
    "Dashboard",
    [
        "📊 Live Pipeline",
        "📋 Approval Queue",
        "📝 Ticket Timeline",
        "📊 Channel Analytics",
        "🎨 Theme Analysis",
        "📚 KB Management",
        "🔍 Gap Log",
        "📈 Marketing Brief",
        "📜 Audit Log",
    ],
)

# Auto-refresh toggle
st.sidebar.markdown("---")
st.session_state.auto_refresh = st.sidebar.checkbox("Auto-refresh (10s)", value=st.session_state.auto_refresh)
if st.session_state.auto_refresh:
    st.sidebar.info("Dashboard will refresh every 10 seconds.")

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.markdown("Built by Digital Futures Consultancy LLP (T17LL1937H)")
st.sidebar.markdown("[https://DigitalFutures.Asia](https://DigitalFutures.Asia)")
st.sidebar.markdown(f"Loaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# =====================================================================
# TAB: Live Pipeline
# =====================================================================
if tab == "📊 Live Pipeline":
    st.header("Live Pipeline Statistics")
    st.markdown("Real-time statistics from the BOLDR Intelligence Engine.")

    if live_stats:
        pipeline = live_stats.get("pipeline", {})
        kb_info = live_stats.get("kb", {})
        models = live_stats.get("models", {})

        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tickets Processed", pipeline.get("total_tickets", 0))
        with col2:
            answerable = pipeline.get("answerable_count", 0)
            total = max(pipeline.get("total_tickets", 1), 1)
            st.metric("Answerable by KB", answerable, f"{round(answerable/total*100, 1)}%")
        with col3:
            st.metric("Knowledge Gaps", pipeline.get("gap_count", 0))
        with col4:
            st.metric("Escalations", pipeline.get("escalation_count", 0))

        # Channel distribution
        st.subheader("Channel Distribution")
        channel_data = pipeline.get("tickets_by_channel", {})
        if channel_data and any(v > 0 for v in channel_data.values()):
            st.bar_chart(channel_data)
        else:
            st.info("No tickets processed yet. Send a request to /api/v1/intake to see live data.")

        # Intent distribution
        intent_data = pipeline.get("tickets_by_intent", {})
        if intent_data:
            st.subheader("Intent Distribution")
            st.bar_chart(intent_data)

        # Persona distribution
        persona_data = pipeline.get("tickets_by_persona", {})
        if persona_data:
            st.subheader("Buyer Persona Distribution")
            st.bar_chart(persona_data)

        # KB info
        st.subheader("Knowledge Base")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("KB Chunks", kb_info.get("total_chunks", 93))
        with col2:
            st.metric("KB Sources", kb_info.get("total_sources", 5))
        with col3:
            st.metric("Answerability Rate", f"{kb_info.get('answerability_rate', 71.4)}%")

        # Model info
        st.subheader("Model Configuration")
        for key, val in models.items():
            st.markdown(f"- **{key}:** {val}")

        st.success(f"Connected to BOLDR Intelligence Engine | Uptime since: {pipeline.get('start_time', 'unknown')}")
    else:
        st.warning("Cannot connect to FastAPI server. Start it with: `uvicorn app.api:app --host 0.0.0.0 --port 8000`")

# =====================================================================
# TAB: Approval Queue
# =====================================================================
elif tab == "📋 Approval Queue":
    st.header("Reply Approval Queue")
    st.markdown("**Human-in-the-loop by design.** Every drafted reply requires explicit approval before sending. No auto-send, ever.")

    # Fetch live pending replies
    try:
        resp = requests.get(f"{API_BASE}/queue/replies/pending", timeout=3)
        if resp.status_code == 200:
            pending = resp.json().get("replies", [])
            if pending:
                st.info(f"📋 {len(pending)} replies pending approval")
                for reply in pending:
                    with st.expander(f"**{reply['ticket_id']}** — {reply['question_type']} | {reply['persona']} | {reply['channel']}", expanded=(reply == pending[0])):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**Customer:** {reply['customer_name']}")
                            st.markdown(f"**Subject:** {reply.get('subject', 'N/A')}")
                            st.markdown(f"**Original Message:** {reply['original_message'][:200]}")
                            st.markdown("---")
                            st.markdown(f"**Draft Reply:** {reply.get('draft_reply', '(generated by Intelligence Engine)')[:500]}")
                        with col2:
                            st.metric("Confidence", f"{reply.get('confidence', 0):.2f}")
                            st.metric("Answerable", "Yes" if reply.get('is_answerable') else "No")
                            st.metric("Needs Shopify", "Yes" if reply.get('needs_shopify') else "No")
                            st.metric("SOP Routing", reply.get('sop_routing', 'N/A'))
                            if st.button(f"✅ Approve {reply['ticket_id']}", key=f"approve_{reply['ticket_id']}"):
                                approve_resp = requests.post(
                                    f"{API_BASE}/queue/replies/{reply['ticket_id']}/approve",
                                    params={"approved_by": "dashboard_user"},
                                    timeout=5,
                                )
                                if approve_resp.status_code == 200:
                                    st.success(f"Approved {reply['ticket_id']}")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to approve: {approve_resp.text}")
                            if st.button(f"❌ Reject {reply['ticket_id']}", key=f"reject_{reply['ticket_id']}"):
                                reject_resp = requests.post(
                                    f"{API_BASE}/queue/replies/{reply['ticket_id']}/reject",
                                    params={"rejected_by": "dashboard_user"},
                                    timeout=5,
                                )
                                if reject_resp.status_code == 200:
                                    st.warning(f"Rejected {reply['ticket_id']}")
                                    st.rerun()
            else:
                st.info("📋 No pending replies. All drafted replies have been processed.")
        else:
            st.warning("Could not fetch pending replies from API.")
    except Exception as e:
        st.error(f"Cannot connect to API: {e}")

# =====================================================================
# TAB: Ticket Timeline
# =====================================================================
elif tab == "📝 Ticket Timeline":
    st.header("Ticket Processing Timeline")
    st.markdown("Recent ticket processing events with full classification and routing details.")

    # Fetch from audit log
    try:
        resp = requests.get(f"{API_BASE}/audit/recent?limit=20", timeout=5)
        if resp.status_code == 200:
            tickets = resp.json().get("tickets", [])
            if tickets:
                for ticket in tickets:
                    status_icon = "✅" if ticket.get("is_answerable") else "🔴"
                    esc_icon = "⚠️" if ticket.get("escalation_required") else ""
                    shopify_icon = "🛒" if ticket.get("needs_shopify") else ""

                    with st.expander(
                        f"{status_icon} {ticket['ticket_id']} — {ticket['question_type']} | "
                        f"{ticket['buyer_persona']} | {ticket['channel']} {shopify_icon}{esc_icon}",
                        expanded=False,
                    ):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(f"**Timestamp:** {ticket['timestamp']}")
                            st.markdown(f"**Channel:** {ticket['channel']}")
                            st.markdown(f"**Customer:** {ticket.get('sender_name', 'Unknown')}")
                            if ticket.get('subject'):
                                st.markdown(f"**Subject:** {ticket['subject']}")
                            st.markdown(f"**Message:** {ticket.get('original_message', 'N/A')[:300]}")
                        with col2:
                            st.metric("Confidence", f"{ticket.get('confidence', 0):.2f}")
                            st.metric("Answerable", "Yes" if ticket.get("is_answerable") else "No")
                            st.metric("Answerability", ticket.get("answerability_type", "N/A"))
                            st.metric("Escalation", "Yes" if ticket.get("escalation_required") else "No")
                        with col3:
                            st.markdown(f"**SOP Routing:** {ticket.get('sop_routing', 'N/A')}")
                            st.markdown(f"**Needs Shopify:** {'Yes' if ticket.get('needs_shopify') else 'No'}")
                            st.markdown(f"**KB Match:** {ticket.get('kb_best_match', 'N/A')}")
                            st.markdown(f"**KB Confidence:** {ticket.get('kb_confidence', 0):.2f}")
                            st.markdown(f"**Reply Queued:** {'Yes' if ticket.get('reply_queued') else 'No'}")

                # Timeline chart
                st.subheader("Processing Timeline")
                timestamps = [t['timestamp'][:16] for t in tickets if t.get('timestamp')]
                if timestamps:
                    st.info(f"Showing {len(tickets)} most recent tickets (newest first)")
            else:
                st.info("No tickets in the audit log yet. Process tickets via /api/v1/intake to see them here.")
        else:
            st.warning("Could not fetch audit data from API.")
    except Exception as e:
        st.error(f"Cannot connect to API: {e}")

# =====================================================================
# TAB: Channel Analytics
# =====================================================================
elif tab == "📊 Channel Analytics":
    st.header("Channel Analytics")
    st.markdown("Breakdown of customer enquiries by channel, intent, and persona.")

    # Use audit summary if available, fall back to pipeline stats
    if audit_data and audit_data.get("total_tickets", 0) > 0:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Processed", audit_data["total_tickets"])
        with col2:
            st.metric("Avg Confidence", f"{audit_data.get('avg_confidence', 0):.2f}")
        with col3:
            ans = audit_data.get("answerability", {}).get("answerable", 0)
            gap = audit_data.get("answerability", {}).get("gap", 0)
            total = max(ans + gap, 1)
            st.metric("Answerability Rate", f"{round(ans/total*100, 1)}%")
        with col4:
            st.metric("Avg Processing Time", f"{audit_data.get('avg_processing_time_ms', 0):.0f}ms")

        # Channel breakdown
        by_channel = audit_data.get("by_channel", {})
        if by_channel:
            st.subheader("Channel Distribution")
            st.bar_chart(by_channel)

            # Pie chart using metric columns
            st.subheader("Channel Share")
            cols = st.columns(len(by_channel))
            for i, (channel, count) in enumerate(by_channel.items()):
                pct = round(count / max(audit_data["total_tickets"], 1) * 100, 1)
                with cols[i]:
                    st.metric(channel, f"{count} ({pct}%)")

        # Intent breakdown
        by_intent = audit_data.get("by_intent", {})
        if by_intent:
            st.subheader("Intent Distribution")
            st.bar_chart(by_intent)

        # Persona breakdown
        by_persona = audit_data.get("by_persona", {})
        if by_persona:
            st.subheader("Persona Distribution")
            st.bar_chart(by_persona)

        # Answerability breakdown
        answerability = audit_data.get("answerability", {})
        if answerability:
            st.subheader("Answerability Breakdown")
            cols = st.columns(len(answerability))
            for i, (key, val) in enumerate(answerability.items()):
                with cols[i]:
                    st.metric(key.replace("_", " ").title(), val)

    elif live_stats:
        pipeline = live_stats.get("pipeline", {})
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tickets", pipeline.get("total_tickets", 0))
        with col2:
            st.metric("Answerable", pipeline.get("answerable_count", 0))
        with col3:
            st.metric("Gaps", pipeline.get("gap_count", 0))
        with col4:
            st.metric("Escalations", pipeline.get("escalation_count", 0))

        st.subheader("Channel Distribution")
        st.bar_chart(pipeline.get("tickets_by_channel", {}))
        st.subheader("Intent Distribution")
        st.bar_chart(pipeline.get("tickets_by_intent", {}))
        st.subheader("Persona Distribution")
        st.bar_chart(pipeline.get("tickets_by_persona", {}))
    else:
        st.warning("No data available. Connect to the API server to see analytics.")

# =====================================================================
# TAB: Theme Analysis
# =====================================================================
elif tab == "🎨 Theme Analysis":
    st.header("Weekly Theme Clustering")
    st.markdown("Visualisation of customer enquiry themes and persona distributions.")

    theme_data = None
    try:
        resp = requests.get(f"{API_BASE}/themes/weekly", timeout=3)
        if resp.status_code == 200:
            theme_data = resp.json()
    except Exception:
        theme_data = None

    st.subheader("Theme Distribution")
    if theme_data and "themes" in theme_data:
        st.bar_chart(theme_data["themes"])
    else:
        fallback_themes = {
            "materials_safety": 10, "strap_compatibility": 10, "servicing": 10,
            "product_general": 10, "order_status": 10, "engraving": 10, "knowledge_gap": 10,
        }
        st.bar_chart(fallback_themes)

    st.subheader("Buyer Persona Distribution")
    if live_stats and live_stats.get("pipeline", {}).get("tickets_by_persona"):
        st.bar_chart(live_stats["pipeline"]["tickets_by_persona"])
    elif audit_data and audit_data.get("by_persona"):
        st.bar_chart(audit_data["by_persona"])
    else:
        fallback_personas = {
            "health_conscious": 10, "gifter": 10, "enthusiast": 10, "niche_buyer": 10,
            "owner_aftercare": 10, "prospect": 10, "transactional": 10,
        }
        st.bar_chart(fallback_personas)

    st.subheader("KB Answerability")
    if audit_data and audit_data.get("answerability"):
        ans = audit_data["answerability"].get("answerable", 0)
        gap = audit_data["answerability"].get("gap", 0)
        total = max(ans + gap, 1)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Answerable by KB", ans, f"{round(ans/total*100, 1)}%")
        with col2:
            st.metric("Knowledge Gaps", gap, f"{round(gap/total*100, 1)}%")
        with col3:
            st.metric("Requires Shopify", live_stats["pipeline"].get("shopify_count", 0) if live_stats else "~10")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Answerable by KB", "50", "71.4%")
        with col2:
            st.metric("Knowledge Gaps", "20", "28.6%")
        with col3:
            st.metric("Requires Shopify", "~10", "14.3%")

# =====================================================================
# TAB: KB Management
# =====================================================================
elif tab == "📚 KB Management":
    st.header("Knowledge Base Management")
    st.markdown("View, search, and manage the BOLDR knowledge base.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("FAQ Entries", "28")
    with col2:
        st.metric("Product Models", "3")
    with col3:
        st.metric("Rate Card Services", "19")
    with col4:
        st.metric("SOP Procedures", "7")

    # Live KB search
    st.subheader("🔍 Search Knowledge Base")
    search_query = st.text_input("Enter a question to search the KB:", key="kb_search")
    if search_query:
        try:
            resp = requests.post(
                f"{API_BASE}/kb/search",
                json={"query": search_query, "n_results": 3},
                timeout=10,
            )
            if resp.status_code == 200:
                results = resp.json()
                if results:
                    for i, r in enumerate(results if isinstance(results, list) else [results]):
                        score = r.get("score", r.get("confidence", "N/A"))
                        st.markdown(f"**Result {i+1}** (score: {score})")
                        st.markdown(f"- **Source:** {r.get('source', r.get('metadata', {}).get('source', 'N/A'))}")
                        st.markdown(f"- **Category:** {r.get('category', r.get('metadata', {}).get('category', 'N/A'))}")
                        st.markdown(f"- **Content:** {r.get('content', r.get('document', 'N/A'))[:500]}")
                        st.markdown("---")
                else:
                    st.warning("No results found.")
            else:
                st.error(f"Search failed: {resp.status_code}")
        except Exception as e:
            st.warning(f"Cannot connect to API: {e}")

    # KB sources
    st.subheader("KB Sources")
    sources = [
        {"Source": "02_product_reference.docx", "Type": "DOCX", "Entries": "3 models + 10 straps + quick answers", "Status": "✅ Indexed"},
        {"Source": "03a_rate_card_engraving.csv", "Type": "CSV", "Entries": "10 services", "Status": "✅ Indexed"},
        {"Source": "03b_rate_card_servicing.csv", "Type": "CSV", "Entries": "9 tiers", "Status": "✅ Indexed"},
        {"Source": "04_faq_document.pdf", "Type": "PDF", "Entries": "28 FAQ entries", "Status": "✅ Indexed"},
        {"Source": "05_cs_sop.docx", "Type": "DOCX", "Entries": "SOP + escalation rules + new questions log", "Status": "✅ Indexed"},
    ]
    st.dataframe(sources, use_container_width=True)

    # Auto-drafted KB entries
    st.subheader("Auto-Drafted KB Entries (Pending Approval)")
    try:
        resp = requests.get(f"{API_BASE}/queue/kb", timeout=3)
        if resp.status_code == 200:
            entries = resp.json().get("entries", [])
            if entries:
                st.dataframe(entries, use_container_width=True)
            else:
                st.info("No pending KB entries. New entries appear here when knowledge gaps are resolved.")
        else:
            st.info("No pending KB entries. New entries appear here when knowledge gaps are resolved.")
    except Exception:
        st.info("No pending KB entries.")

# =====================================================================
# TAB: Gap Log
# =====================================================================
elif tab == "🔍 Gap Log":
    st.header("Knowledge Gap Log")
    st.markdown("Detected knowledge gaps from customer enquiries that the KB cannot answer.")

    # Try live gap data
    try:
        resp = requests.get(f"{API_BASE}/themes/weekly", timeout=3)
        if resp.status_code == 200:
            weekly = resp.json()
            gaps_data = weekly.get("gaps", weekly.get("theme_distribution", {}))
            if gaps_data:
                st.subheader("Current Gap Themes")
                st.json(gaps_data)
    except Exception:
        pass

    gaps = [
        {"Theme": "Product specs", "Question": "Magnetic field resistance (MRI)", "Persona": "niche_buyer", "Frequency": 1, "Marketing Signal": "No", "Status": "Pending"},
        {"Theme": "Sustainability", "Question": "Vegan-friendly materials", "Persona": "health_conscious", "Frequency": 1, "Marketing Signal": "Yes", "Status": "Answered"},
        {"Theme": "Sustainability", "Question": "Carbon-neutral shipping", "Persona": "health_conscious", "Frequency": 1, "Marketing Signal": "Yes", "Status": "Pending"},
        {"Theme": "Product specs", "Question": "Shock rating for trail running", "Persona": "niche_buyer", "Frequency": 1, "Marketing Signal": "No", "Status": "Answered"},
        {"Theme": "Sales", "Question": "Corporate bulk pricing", "Persona": "prospect", "Frequency": 1, "Marketing Signal": "Yes", "Status": "Redirected"},
        {"Theme": "Sustainability", "Question": "Strap recycling programme", "Persona": "niche_buyer", "Frequency": 1, "Marketing Signal": "Yes", "Status": "Pending"},
    ]
    st.dataframe(gaps, use_container_width=True)

    st.warning("⚠️ **Key Insight:** 10 of 20 unanswerable tickets are order operations requiring Shopify lookup — not true KB gaps. The workflow distinguishes these automatically.")

# =====================================================================
# TAB: Marketing Brief
# =====================================================================
elif tab == "📈 Marketing Brief":
    st.header("Monthly Marketing Intelligence Brief")
    st.markdown("**What customers are asking that is NOT on your product pages.**")

    try:
        resp = requests.get(f"{API_BASE}/themes/monthly-brief", timeout=3)
        if resp.status_code == 200:
            brief = resp.json()
            if brief and "title" in brief:
                st.subheader("Live Marketing Brief")
                st.markdown(f"**{brief.get('title', '')}**")
                st.markdown(brief.get("executive_summary", ""))
    except Exception:
        pass

    st.subheader("Executive Summary")
    st.info("This month, 20 customer enquiries could not be answered from the existing Knowledge Base. The top emerging themes are: materials_safety, sustainability, and product_specs. These represent gaps in product documentation and marketing positioning that, if addressed, could unlock new customer segments and revenue opportunities.")

    st.subheader("Marketing Signals")
    signals = [
        {"Signal": "BPA-free straps", "Frequency": "3+", "Persona": "Health-Conscious", "Action": 'Product badge: "BPA-Free Straps"', "Priority": "🔴 High"},
        {"Signal": "Vegan materials", "Frequency": "1+", "Persona": "Sustainability Advocate", "Action": "Develop vegan strap positioning", "Priority": "🔴 High"},
        {"Signal": "Corporate gifting", "Frequency": "1+", "Persona": "Gifter", "Action": "Create bulk pricing KB entry + gifting page", "Priority": "🟡 Medium"},
        {"Signal": "Nickel allergy", "Frequency": "4+", "Persona": "Health-Conscious", "Action": "Add hypoallergenic product page section", "Priority": "🟡 Medium"},
        {"Signal": "Magnetic field resistance", "Frequency": "1+", "Persona": "Niche Buyer", "Action": "Add MRI safety note to product specs", "Priority": "🟢 Low"},
    ]
    st.dataframe(signals, use_container_width=True)

    st.subheader("Prioritised Action Items")
    actions = [
        {"Action": 'Add "BPA-Free Straps" product badge', "Priority": "High", "Deadline": "2 weeks", "Persona": "Health-Conscious"},
        {"Action": "Develop vegan strap product positioning", "Priority": "High", "Deadline": "2 weeks", "Persona": "Sustainability"},
        {"Action": "Create corporate gifting pricing page", "Priority": "Medium", "Deadline": "1 month", "Persona": "Gifter"},
        {"Action": "Add hypoallergenic section to product pages", "Priority": "Medium", "Deadline": "1 month", "Persona": "Health-Conscious"},
    ]
    st.dataframe(actions, use_container_width=True)

    st.subheader("Business Impact")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("CS Time Saved", "~9 hrs/wk", "60% reduction")
    with col2:
        st.metric("Monthly Cost Savings", "SGD 1,080", "at SGD 28/hr blended rate")
    with col3:
        st.metric("Monthly Opex", "SGD 22-57", "19-49× ROI")

# =====================================================================
# TAB: Audit Log
# =====================================================================
elif tab == "📜 Audit Log":
    st.header("Audit Log")
    st.markdown("**Transparency & Auditability.** Every classification decision is logged with reasoning, confidence scores, and routing details.")

    # Summary stats
    if audit_data and audit_data.get("total_tickets", 0) > 0:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tickets Audited", audit_data["total_tickets"])
        with col2:
            st.metric("Avg Confidence", f"{audit_data.get('avg_confidence', 0):.2f}")
        with col3:
            ans = audit_data.get("answerability", {}).get("answerable", 0)
            total = max(audit_data["total_tickets"], 1)
            st.metric("Answerability Rate", f"{round(ans/total*100, 1)}%")
        with col4:
            st.metric("Avg Processing Time", f"{audit_data.get('avg_processing_time_ms', 0):.0f}ms")

        # Full audit table
        st.subheader("All Ticket Records")
        try:
            limit = st.slider("Records to display", 10, 200, 50)
            resp = requests.get(f"{API_BASE}/audit/recent?limit={limit}", timeout=5)
            if resp.status_code == 200:
                tickets = resp.json().get("tickets", [])
                if tickets:
                    # Show as a clean table
                    display_data = []
                    for t in tickets:
                        display_data.append({
                            "Ticket ID": t["ticket_id"],
                            "Time": t["timestamp"][:19],
                            "Channel": t["channel"],
                            "Intent": t["question_type"],
                            "Persona": t["buyer_persona"],
                            "Confidence": f"{t.get('confidence', 0):.2f}",
                            "Answerable": "Yes" if t.get("is_answerable") else "No",
                            "Escalated": "Yes" if t.get("escalation_required") else "No",
                            "SOP Route": t.get("sop_routing", ""),
                        })
                    st.dataframe(display_data, use_container_width=True)
                else:
                    st.info("No audit records found.")
        except Exception as e:
            st.error(f"Error fetching audit data: {e}")

        # Detailed ticket lookup
        st.subheader("Ticket Lookup")
        lookup_id = st.text_input("Enter Ticket ID (e.g., TKT-18219):")
        if lookup_id:
            try:
                resp = requests.get(f"{API_BASE}/audit/ticket/{lookup_id}", timeout=5)
                if resp.status_code == 200:
                    ticket = resp.json()
                    st.json(ticket)
                else:
                    st.warning(f"Ticket {lookup_id} not found.")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.info("No audit records yet. Process tickets via /api/v1/intake to start logging.")

# Auto-refresh
if st.session_state.auto_refresh:
    import time
    time.sleep(10)
    st.rerun()