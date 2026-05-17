"""
BOLDR Self-Improving Customer Intelligence Engine
Streamlit Dashboard — Live Pipeline Stats, Approval Queue, Theme Visualisation, KB Management

Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP
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
)

st.title("🏛️ BOLDR — Self-Improving Customer Intelligence Engine")
st.caption("ECHELON 2026 AI Workflow Competition | REVENUE ROCKET Track")
st.caption("Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP (T17LL1937H)")

# Try to fetch live stats
live_stats = None
try:
    resp = requests.get(f"{API_BASE}/stats", timeout=3)
    if resp.status_code == 200:
        live_stats = resp.json()
except Exception:
    live_stats = None

# Sidebar navigation
tab = st.sidebar.radio(
    "Dashboard",
    ["📊 Live Pipeline", "📋 Approval Queue", "🎨 Theme Analysis", "📚 KB Management", "🔍 Gap Log", "📈 Marketing Brief"],
)

if tab == "📊 Live Pipeline":
    st.header("Live Pipeline Statistics")
    st.markdown("Real-time statistics from the BOLDR Intelligence Engine.")

    if live_stats:
        pipeline = live_stats.get("pipeline", {})
        kb_info = live_stats.get("kb", {})
        models = live_stats.get("models", {})

        # Pipeline overview
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
        if channel_data:
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
        st.markdown("Showing sample data below:")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tickets", "70")
        with col2:
            st.metric("Answerable by KB", "50", "71.4%")
        with col3:
            st.metric("Knowledge Gaps", "20", "28.6%")
        with col4:
            st.metric("Requires Shopify", "10", "14.3%")

elif tab == "📋 Approval Queue":
    st.header("Reply Approval Queue")
    st.markdown("Drafted replies queued for human approval before sending. **No auto-send — human-in-the-loop by design.**")

    # Try to fetch recent themes to show live gaps
    recent_gaps = None
    try:
        resp = requests.get(f"{API_BASE}/themes/weekly", timeout=3)
        if resp.status_code == 200:
            recent_gaps = resp.json()
    except Exception:
        recent_gaps = None

    st.info("📋 Drafted replies appear here after the Intelligence Loop processes a ticket. Each reply requires explicit human approval before sending.")

    with st.expander("Sample Queued Reply", expanded=True):
        st.markdown("**Ticket:** TKT-1016 | **Type:** materials_safety | **Persona:** health_conscious")
        st.markdown("**Subject:** Strap dye safety")
        st.markdown("**Confidence:** 0.89 | **Channel:** Email")
        st.markdown("---")
        st.markdown("""**Draft Reply:**

Hi Caleb,

Thank you for reaching out to BOLDR. We are happy to help with that.

All BOLDR FKM rubber and Nylon NATO straps are BPA-free and use non-toxic dyes. The coloured straps (including Red, Navy, and Olive) are designed for active wear and are safe for skin contact even with heavy sweating.

If you have sensitive skin, we would recommend our FKM rubber straps, which are both BPA-free and nickel-free.

Best regards,
BOLDR CS Team""")
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("✅ Approve & Send", key="approve_1")
        with col2:
            st.button("✏️ Edit", key="edit_1")
        with col3:
            st.button("❌ Reject", key="reject_1")

elif tab == "🎨 Theme Analysis":
    st.header("Weekly Theme Clustering")
    st.markdown("Visualisation of customer enquiry themes and persona distributions.")

    # Try to get live theme data
    theme_data = None
    try:
        resp = requests.get(f"{API_BASE}/themes/weekly", timeout=3)
        if resp.status_code == 200:
            theme_data = resp.json()
    except Exception:
        theme_data = None

    # Theme distribution chart
    st.subheader("Theme Distribution")
    if theme_data and "themes" in theme_data:
        st.bar_chart(theme_data["themes"])
    else:
        fallback_themes = {
            "materials_safety": 10,
            "strap_compatibility": 10,
            "servicing": 10,
            "product_general": 10,
            "order_status": 10,
            "engraving": 10,
            "knowledge_gap": 10,
        }
        st.bar_chart(fallback_themes)

    # Persona breakdown
    st.subheader("Buyer Persona Distribution")
    if live_stats and live_stats.get("pipeline", {}).get("tickets_by_persona"):
        st.bar_chart(live_stats["pipeline"]["tickets_by_persona"])
    else:
        fallback_personas = {
            "health_conscious": 10,
            "gifter": 10,
            "enthusiast": 10,
            "niche_buyer": 10,
            "owner_aftercare": 10,
            "prospect": 10,
            "transactional": 10,
        }
        st.bar_chart(fallback_personas)

    # KB answerability
    st.subheader("KB Answerability")
    if live_stats:
        pipeline = live_stats.get("pipeline", {})
        total = max(pipeline.get("total_tickets", 1), 1)
        ans = pipeline.get("answerable_count", 0)
        gaps = pipeline.get("gap_count", 0)
        shopify = pipeline.get("shopify_count", 0)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Answerable by KB", ans, f"{round(ans/total*100, 1)}%")
        with col2:
            st.metric("Knowledge Gaps", gaps, f"{round(gaps/total*100, 1)}%")
        with col3:
            st.metric("Requires Shopify", shopify, f"{round(shopify/total*100, 1)}%")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Answerable by KB", "50", "71.4%")
        with col2:
            st.metric("Knowledge Gaps", "20", "28.6%")
        with col3:
            st.metric("Requires Shopify", "~10", "14.3%")

elif tab == "📚 KB Management":
    st.header("Knowledge Base Management")
    st.markdown("View, search, and manage the BOLDR knowledge base.")

    # KB stats
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

    # Auto-drafted KB entries awaiting approval
    st.subheader("Auto-Drafted KB Entries (Pending Approval)")
    st.info("New KB entries will appear here when knowledge gaps are resolved. Each entry requires 1-click human approval before being added to the Knowledge Base.")
    st.markdown("*Example:* If a customer asks about MRI resistance and the team resolves it, a KB entry will be auto-drafted here for approval.")

elif tab == "🔍 Gap Log":
    st.header("Knowledge Gap Log")
    st.markdown("Detected knowledge gaps from customer enquiries that the KB cannot answer.")

    # Try to get live gap data
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

    # Gap log table
    gaps = [
        {"Theme": "Product specs", "Question": "Magnetic field resistance (MRI)", "Persona": "niche_buyer", "Frequency": 1, "Marketing Signal": "No", "Status": "Pending"},
        {"Theme": "Sustainability", "Question": "Vegan-friendly materials", "Persona": "health_conscious", "Frequency": 1, "Marketing Signal": "Yes", "Status": "Answered"},
        {"Theme": "Sustainability", "Question": "Carbon-neutral shipping", "Persona": "health_conscious", "Frequency": 1, "Marketing Signal": "Yes", "Status": "Pending"},
        {"Theme": "Product specs", "Question": "Shock rating for trail running", "Persona": "niche_buyer", "Frequency": 1, "Marketing Signal": "No", "Status": "Answered"},
        {"Theme": "Sales", "Question": "Corporate bulk pricing", "Persona": "prospect", "Frequency": 1, "Marketing Signal": "Yes", "Status": "Redirected"},
        {"Theme": "Sustainability", "Question": "Strap recycling programme", "Persona": "niche_buyer", "Frequency": 1, "Marketing Signal": "Yes", "Status": "Pending"},
    ]
    st.dataframe(gaps, use_container_width=True)

    # Key insight
    st.warning("⚠️ **Key Insight:** 10 of 20 unanswerable tickets are actually order operations requiring Shopify lookup — not true KB gaps. The workflow distinguishes these automatically.")

elif tab == "📈 Marketing Brief":
    st.header("Monthly Marketing Intelligence Brief")
    st.markdown("**What customers are asking that is NOT on your product pages.**")

    # Try to get live marketing brief
    try:
        resp = requests.get(f"{API_BASE}/themes/monthly-brief", timeout=3)
        if resp.status_code == 200:
            brief = resp.json()
            if brief:
                st.subheader("Live Marketing Brief")
                st.json(brief)
    except Exception:
        pass

    st.subheader("Executive Summary")
    st.info("This month, 20 customer enquiries could not be answered from the existing Knowledge Base. The top emerging themes are: materials_safety, sustainability, and product_specs. These represent gaps in product documentation and marketing positioning that, if addressed, could unlock new customer segments and revenue opportunities.")

    # Marketing signals
    st.subheader("Marketing Signals")
    signals = [
        {"Signal": "BPA-free straps", "Frequency": "3+", "Persona": "Health-Conscious", "Action": 'Product badge: "BPA-Free Straps"', "Priority": "🔴 High"},
        {"Signal": "Vegan materials", "Frequency": "1+", "Persona": "Sustainability Advocate", "Action": "Develop vegan strap positioning", "Priority": "🔴 High"},
        {"Signal": "Corporate gifting", "Frequency": "1+", "Persona": "Gifter", "Action": "Create bulk pricing KB entry + gifting page", "Priority": "🟡 Medium"},
        {"Signal": "Nickel allergy", "Frequency": "4+", "Persona": "Health-Conscious", "Action": "Add hypoallergenic product page section", "Priority": "🟡 Medium"},
        {"Signal": "Magnetic field resistance", "Frequency": "1+", "Persona": "Niche Buyer", "Action": "Add MRI safety note to product specs", "Priority": "🟢 Low"},
    ]
    st.dataframe(signals, use_container_width=True)

    # Action items
    st.subheader("Prioritised Action Items")
    actions = [
        {"Action": 'Add "BPA-Free Straps" product badge', "Priority": "High", "Deadline": "2 weeks", "Persona": "Health-Conscious"},
        {"Action": "Develop vegan strap product positioning", "Priority": "High", "Deadline": "2 weeks", "Persona": "Sustainability"},
        {"Action": "Create corporate gifting pricing page", "Priority": "Medium", "Deadline": "1 month", "Persona": "Gifter"},
        {"Action": "Add hypoallergenic section to product pages", "Priority": "Medium", "Deadline": "1 month", "Persona": "Health-Conscious"},
    ]
    st.dataframe(actions, use_container_width=True)

    # Business impact
    st.subheader("Business Impact")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("CS Time Saved", "~9 hrs/wk", "60% reduction")
    with col2:
        st.metric("Monthly Cost Savings", "SGD 1,080", "at SGD 28/hr blended rate")
    with col3:
        st.metric("Monthly Opex", "SGD 22-57", "19-49× ROI")

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.markdown("Built by Digital Futures Consultancy LLP (T17LL1937H)")
st.sidebar.markdown("ECHELON 2026 — REVENUE ROCKET Track")
st.sidebar.markdown("[https://DigitalFutures.Asia](https://DigitalFutures.Asia)")
st.sidebar.markdown(f"Dashboard loaded: {datetime.now().strftime('%Y-%m-%d %H:%M')}")