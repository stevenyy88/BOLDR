"""
BOLDR Self-Improving Customer Intelligence Engine
Streamlit Dashboard — Approval Queue, Theme Visualisation, KB Management

Author: Steve Ng, Founder and CEO - Digital Futures Consultancy LLP
"""

import streamlit as st
import json
from datetime import datetime

st.set_page_config(
    page_title="BOLDR Customer Intelligence Engine",
    page_icon="🏛️",
    layout="wide",
)

st.title("🏛️ BOLDR — Self-Improving Customer Intelligence Engine")
st.caption("ECHELON 2026 AI Workflow Competition | REVENUE ROCKET Track")
st.caption("Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP")

# Sidebar navigation
tab = st.sidebar.radio(
    "Dashboard",
    ["📋 Approval Queue", "📊 Theme Analysis", "📚 KB Management", "🔍 Gap Log", "📈 Marketing Brief"],
)

if tab == "📋 Approval Queue":
    st.header("Reply Approval Queue")
    st.markdown("Drafted replies queued for human approval before sending.")

    # Placeholder for live data
    st.info("🔄 Connect to n8n workflow to see live queued replies.")

    with st.expander("Sample Queued Reply", expanded=True):
        st.markdown("**Ticket:** TKT-1016 | **Type:** materials_safety | **Persona:** health_conscious")
        st.markdown("**Subject:** Strap dye safety")
        st.markdown("---")
        st.markdown("""**Draft Reply:**

Hi Caleb,

Thanks for reaching out! Happy to help with that.

All BOLDR FKM rubber and Nylon NATO straps are BPA-free and use non-toxic dyes. The coloured straps (including Red, Navy, and Olive) are designed for active wear and are safe for skin contact even with heavy sweating.

If you have sensitive skin, we'd recommend our FKM rubber straps, which are both BPA-free and nickel-free.

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

elif tab == "📊 Theme Analysis":
    st.header("Weekly Theme Clustering")
    st.markdown("Visualisation of customer enquiry themes and persona distributions.")

    # Theme distribution chart
    st.subheader("Theme Distribution")
    theme_data = {
        "materials_safety": 10,
        "strap_compatibility": 10,
        "servicing": 10,
        "product_general": 10,
        "order_status": 10,
        "engraving": 10,
        "knowledge_gap": 10,
    }
    st.bar_chart(theme_data)

    # Persona breakdown
    st.subheader("Buyer Persona Distribution")
    persona_data = {
        "health_conscious": 10,
        "gifter": 10,
        "enthusiast": 10,
        "niche_buyer": 10,
        "owner_aftercare": 10,
        "prospect": 10,
        "transactional": 10,
    }
    st.bar_chart(persona_data)

    # KB answerability
    st.subheader("KB Answerability")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Answerable by KB", "50", "71%")
    with col2:
        st.metric("Knowledge Gaps", "20", "29%")
    with col3:
        st.metric("Requires Shopify", "~10", "14%")

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
    st.info("🔄 New KB entries will appear here when knowledge gaps are resolved.")
    st.markdown("*Example:* If a customer asks about MRI resistance and the team resolves it, a KB entry will be auto-drafted here for 1-click approval.")

elif tab == "🔍 Gap Log":
    st.header("Knowledge Gap Log")
    st.markdown("Detected knowledge gaps from customer enquiries that the KB cannot answer.")

    # Gap log table
    gaps = [
        {"Theme": "Product specs", "Question": "Magnetic field resistance (MRI)", "Persona": "niche_buyer", "Frequency": 1, "Marketing Signal": "❌", "Status": "Pending"},
        {"Theme": "Sustainability", "Question": "Vegan-friendly materials", "Persona": "health_conscious", "Frequency": 1, "Marketing Signal": "✅", "Status": "Answered"},
        {"Theme": "Sustainability", "Question": "Carbon-neutral shipping", "Persona": "health_conscious", "Frequency": 1, "Marketing Signal": "✅", "Status": "Pending"},
        {"Theme": "Product specs", "Question": "Shock rating for trail running", "Persona": "niche_buyer", "Frequency": 1, "Marketing Signal": "❌", "Status": "Answered"},
        {"Theme": "Sales", "Question": "Corporate bulk pricing", "Persona": "prospect", "Frequency": 1, "Marketing Signal": "✅", "Status": "Redirected"},
        {"Theme": "Sustainability", "Question": "Strap recycling programme", "persona": "niche_buyer", "Frequency": 1, "Marketing Signal": "✅", "Status": "Pending"},
    ]
    st.dataframe(gaps, use_container_width=True)

    # Key insight
    st.warning("⚠️ **Key Insight:** 10 of 20 unanswerable tickets are actually order operations requiring Shopify lookup — not true KB gaps. The workflow distinguishes these automatically.")

elif tab == "📈 Marketing Brief":
    st.header("Monthly Marketing Intelligence Brief")
    st.markdown("**What customers are asking that is NOT on your product pages.**")

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

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.markdown("Built by Digital Futures Consultancy LLP")
st.sidebar.markdown("ECHELON 2026 — REVENUE ROCKET Track")
st.sidebar.markdown(f"Dashboard loaded: {datetime.now().strftime('%Y-%m-%d %H:%M')}")