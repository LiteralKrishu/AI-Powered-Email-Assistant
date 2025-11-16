"""
Streamlit analytics page — displays email statistics and distributions.
"""

import streamlit as st
from streamlit_utils import api_get, safe_api_call, get_api_base_url


st.set_page_config(page_title="Analytics", layout="wide")

st.title("📊 Analytics")

st.markdown(
    f"**API Base URL:** {get_api_base_url()} (from env or sidebar config)"
)
st.markdown("---")


def fetch_analytics():
    """Fetch analytics from FastAPI backend."""
    return api_get("/analytics/")


def display_analytics():
    """Display analytics dashboard."""
    analytics = safe_api_call(
        fetch_analytics,
        error_message="Failed to fetch analytics",
        return_default=None
    )
    
    if not analytics:
        st.warning("⚠️ No analytics data available. Try fetching emails first.")
        return
    
    # Summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Emails",
            value=analytics.get("total_emails", 0)
        )
    
    with col2:
        st.metric(
            label="Processed",
            value=analytics.get("processed_emails", 0)
        )
    
    with col3:
        st.metric(
            label="Pending",
            value=analytics.get("pending_emails", 0)
        )
    
    with col4:
        st.metric(
            label="Last 24h",
            value=analytics.get("emails_last_24h", 0)
        )
    
    st.markdown("---")
    
    # Charts
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📈 Sentiment Distribution")
        sentiment_data = analytics.get("sentiment_distribution", {})
        if sentiment_data:
            st.bar_chart(sentiment_data)
        else:
            st.info("No sentiment data available")
    
    with col_right:
        st.subheader("⏰ Urgency Distribution")
        urgency_data = analytics.get("urgency_distribution", {})
        if urgency_data:
            st.bar_chart(urgency_data)
        else:
            st.info("No urgency data available")
    
    st.markdown("---")
    
    st.subheader("🏷️ Category Distribution")
    category_data = analytics.get("category_distribution", {})
    if category_data:
        st.bar_chart(category_data)
    else:
        st.info("No category data available")
    
    st.markdown("---")
    
    # Raw data (expandable)
    with st.expander("📋 View raw analytics JSON"):
        st.json(analytics)


# UI
st.sidebar.markdown("### Navigation")
st.sidebar.markdown("[← Back to Emails](./)", use_column_width=True)

if st.button("🔄 Refresh Analytics", use_container_width=True):
    st.rerun()

st.markdown("")
display_analytics()

st.markdown("---")
st.caption(
    "💡 **Tip:** Analytics are cached from the last fetch. Click 'Fetch & process new emails' "
    "on the main page to update email processing and refresh analytics."
)
