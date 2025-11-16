"""
Streamlit knowledge base page — view and create KB items.
"""

import streamlit as st
from streamlit_utils import api_get, api_post, safe_api_call, get_api_base_url


st.set_page_config(page_title="Knowledge Base", layout="wide")

st.title("📚 Knowledge Base")

st.markdown(
    f"**API Base URL:** {get_api_base_url()} (from env or sidebar config)"
)
st.markdown("---")


def fetch_kb_items(limit: int = 100):
    """Fetch knowledge base items from FastAPI backend."""
    return api_get("/knowledge-base/", params={"skip": 0, "limit": limit})


def create_kb_item(title: str, content: str, category: str, tags: list):
    """Create a new knowledge base item."""
    payload = {
        "title": title,
        "content": content,
        "category": category,
        "tags": tags
    }
    return api_post("/knowledge-base/", data=payload)


def display_kb_items():
    """Display list of knowledge base items."""
    items = safe_api_call(
        fetch_kb_items,
        error_message="Failed to fetch knowledge base items",
        return_default=[]
    )
    
    if not items:
        st.info("📭 No knowledge base items found. Create your first item below!")
        return
    
    st.subheader(f"📖 Knowledge Base Items ({len(items)})")
    
    for item in items:
        with st.expander(
            f"**{item.get('title', 'Untitled')}** — {item.get('category', 'N/A')}"
        ):
            col_left, col_right = st.columns([1, 1])
            
            with col_left:
                st.markdown(f"**Category:** `{item.get('category', 'N/A')}`")
                created = item.get("created_at", "N/A")
                st.markdown(f"**Created:** {created}")
            
            with col_right:
                if item.get("tags"):
                    st.markdown("**Tags:**")
                    for tag in item.get("tags", []):
                        st.markdown(f"🏷️ `{tag}`", unsafe_allow_html=True)
            
            st.markdown("**Content:**")
            st.text(item.get("content", ""))


def display_create_form():
    """Display form to create a new KB item."""
    st.subheader("➕ Create New Knowledge Base Item")
    
    with st.form(key="kb_form"):
        title = st.text_input(
            "Title",
            placeholder="e.g., How to reset password",
            help="Brief title for the KB article"
        )
        
        category = st.selectbox(
            "Category",
            options=["billing", "technical", "account", "feature", "general"],
            help="Choose or type a category"
        )
        
        content = st.text_area(
            "Content",
            placeholder="Detailed content for this KB article...",
            height=150,
            help="Full text of the knowledge base article"
        )
        
        tags_input = st.text_input(
            "Tags (comma-separated)",
            placeholder="e.g., password, reset, account",
            help="Comma-separated list of tags for searching"
        )
        
        # Parse tags
        tags = [t.strip() for t in tags_input.split(",") if t.strip()]
        
        submit_button = st.form_submit_button(
            "✅ Create Item",
            use_container_width=True
        )
        
        if submit_button:
            if not title or not content or not category:
                st.error("❌ Please fill in Title, Category, and Content")
            else:
                with st.spinner("Creating knowledge base item..."):
                    result = safe_api_call(
                        lambda: create_kb_item(title, content, category, tags),
                        error_message="Failed to create knowledge base item",
                        return_default=None
                    )
                
                if result:
                    st.success(f"✅ Knowledge base item created successfully!")
                    st.rerun()


# UI
st.sidebar.markdown("### Navigation")
st.sidebar.markdown("[← Back to Emails](./)", use_container_width=True)

col_refresh, col_new = st.columns(2)
with col_refresh:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

with col_new:
    if st.button("➕ New Item", use_container_width=True):
        st.session_state["show_form"] = not st.session_state.get("show_form", False)
        st.rerun()

st.markdown("")

# Toggle form display
if st.session_state.get("show_form", False):
    display_create_form()
    st.markdown("---")

display_kb_items()

st.markdown("---")
st.caption(
    "💡 **Tip:** Knowledge base items are used by the AI to generate better responses. "
    "Add common questions, FAQs, and company policies here."
)
