import streamlit as st
from datetime import datetime
from streamlit_utils import (
    api_get, api_post, api_put,
    safe_api_call, get_api_base_url,
    set_api_base_url
)


st.set_page_config(page_title="AI Email Assistant Dashboard", layout="wide")

st.title("📧 AI-Powered Email Assistant — Streamlit Dashboard")

# Sidebar: Configuration
st.sidebar.header("⚙️ Settings")
default_url = get_api_base_url()
api_base = st.sidebar.text_input(
    "FastAPI Base URL",
    value=default_url,
    help="Set via FASTAPI_BASE_URL env var or configure here. "
         "e.g., http://localhost:8000 or http://192.168.1.100:8000"
)
set_api_base_url(api_base)

st.sidebar.markdown("---")
st.sidebar.subheader("🔄 Actions")
col_fetch, col_manual = st.sidebar.columns(2)
with col_fetch:
    if st.sidebar.button("📬 Fetch & Process", use_container_width=True):
        with st.spinner("Fetching emails from server..."):
            result = safe_api_call(
                lambda: api_post("/fetch-emails/"),
                error_message="Failed to fetch emails",
                return_default=None
            )
            if result:
                st.sidebar.success(f"✅ {result.get('message', 'Fetch started')}")
                st.session_state["emails"] = None  # Force refresh

with col_manual:
    if st.sidebar.button("🔃 Refresh List", use_container_width=True):
        st.session_state["emails"] = None  # Force refresh
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("**Pages:**")
st.sidebar.markdown("- 📊 [Analytics](./pages/1_analytics)")
st.sidebar.markdown("- 📚 [Knowledge Base](./pages/2_knowledge_base)")

st.sidebar.markdown("---")
st.sidebar.caption(
    "💡 Ensure FastAPI backend is running before using this dashboard. "
    "Start with: `uvicorn app.main:app --reload`"
)


def fetch_emails(limit=50):
    """Fetch emails using new retry logic."""
    return api_get("/emails/", params={"skip": 0, "limit": limit})


def fetch_email_detail(email_id):
    """Fetch single email detail."""
    return api_get(f"/emails/{email_id}")


def send_response(email_id):
    """Send email response."""
    return api_post(f"/emails/{email_id}/send-response")


def update_ai_response(email_id, ai_text):
    """Update AI response for an email."""
    return api_put(f"/emails/{email_id}", data={"ai_response": ai_text})


# Main content
st.markdown("")

col1, col2 = st.columns([1, 2])

# Left column: Email list
with col1:
    st.subheader("📬 Emails")
    limit = st.number_input(
        "Load limit",
        min_value=10,
        max_value=500,
        value=50,
        step=10,
        help="Number of emails to load from the server"
    )
    
    if st.button("🔄 Reload List", use_container_width=True):
        st.session_state["emails"] = None
        st.rerun()
    
    st.markdown("")
    
    # Load emails with caching
    if "emails" not in st.session_state or st.session_state["emails"] is None:
        with st.spinner("Loading emails..."):
            emails = safe_api_call(
                lambda: fetch_emails(limit=limit),
                error_message="Failed to load emails",
                return_default=[]
            )
            st.session_state["emails"] = emails
    else:
        emails = st.session_state.get("emails", [])
    
    if emails:
        # Build selection list with metadata
        options = []
        for e in emails:
            status = "✅" if e.get('is_processed') else "⏳"
            sentiment_icon = {
                "positive": "😊",
                "negative": "😞",
                "neutral": "😐"
            }.get(e.get('sentiment'), "❓")
            
            label = (
                f"{status} {e['id']:3d} | "
                f"{sentiment_icon} {e.get('sentiment', 'N/A')[:3].upper():3s} | "
                f"{e.get('subject', 'No subject')[:40]}"
            )
            options.append((label, e['id']))
        
        selected_label = st.selectbox(
            "Select email:",
            options=options,
            format_func=lambda x: x[0]
        )
        selected_id = selected_label[1]
    else:
        st.info(
            "📭 No emails found. Click '📬 Fetch & Process' in the sidebar to pull new emails."
        )
        selected_id = None
    
    st.markdown("---")
    st.metric("Emails Loaded", len(emails))

# Right column: Email detail
with col2:
    st.subheader("📖 Email Detail")
    
    if selected_id:
        with st.spinner("Loading email details..."):
            detail = safe_api_call(
                lambda: fetch_email_detail(selected_id),
                error_message="Failed to load email details",
                return_default=None
            )
        
        if detail:
            # Header info
            st.markdown(f"**📌 Subject:** {detail.get('subject', 'N/A')}")
            st.markdown(f"**👤 From:** {detail.get('sender', 'N/A')}")
            st.markdown(f"**📮 To:** {detail.get('recipient', 'N/A')}")
            
            # Parse date
            date_val = detail.get('date')
            try:
                parsed_date = datetime.fromisoformat(date_val)
                st.markdown(f"**📅 Date:** {parsed_date.strftime('%Y-%m-%d %H:%M:%S')}")
            except Exception:
                st.markdown(f"**📅 Date:** {date_val}")
            
            # Metadata badges
            col_meta1, col_meta2, col_meta3 = st.columns(3)
            with col_meta1:
                st.metric("Category", detail.get('category', 'N/A'))
            with col_meta2:
                st.metric("Urgency", detail.get('urgency', 'N/A'))
            with col_meta3:
                sentiment_score = detail.get('sentiment_score', 0)
                st.metric("Sentiment", detail.get('sentiment', 'N/A'), f"{sentiment_score:.2f}")
            
            st.markdown("---")
            
            # Email body
            st.markdown("**📄 Message Body:**")
            st.text_area(
                "",
                value=detail.get('body', ''),
                height=150,
                disabled=True,
                key=f"body_{selected_id}"
            )
            
            st.markdown("**🤖 AI Response (editable):**")
            ai_text = st.text_area(
                "",
                value=detail.get('ai_response') or "",
                height=150,
                key=f"ai_{selected_id}",
                placeholder="AI response will be generated automatically or edit here..."
            )
            
            # Action buttons
            col_send, col_save = st.columns(2)
            
            with col_send:
                if st.button("📤 Send Response", key=f"send_{selected_id}", use_container_width=True):
                    if not detail.get('ai_response'):
                        st.error("❌ No AI response to send. Generate or edit a response first.")
                    else:
                        with st.spinner("Sending response..."):
                            result = safe_api_call(
                                lambda: send_response(selected_id),
                                error_message="Failed to send response",
                                return_default=None
                            )
                            if result:
                                st.success("✅ Response sent successfully!")
                                st.session_state["emails"] = None  # Force refresh
                                st.rerun()
            
            with col_save:
                if st.button("💾 Save AI Response", key=f"save_{selected_id}", use_container_width=True):
                    if not ai_text:
                        st.error("❌ AI response is empty. Type a response to save.")
                    else:
                        with st.spinner("Saving response..."):
                            result = safe_api_call(
                                lambda: update_ai_response(selected_id, ai_text),
                                error_message="Failed to save AI response",
                                return_default=None
                            )
                            if result:
                                st.success("✅ AI response updated!")
                                st.session_state["emails"] = None  # Force refresh
                                st.rerun()
        else:
            st.warning("⚠️ Failed to load email details. Try selecting another email.")
    
    else:
        st.info(
            "👈 Select an email from the list on the left to view details, "
            "edit the AI response, or send it."
        )

st.markdown("---")
st.caption(
    "🚀 **Quick Start:** Ensure FastAPI is running with `uvicorn app.main:app --reload` "
    "and have the FASTAPI_BASE_URL environment variable set (or configure in sidebar)."
)
