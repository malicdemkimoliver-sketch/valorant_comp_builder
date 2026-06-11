"""
Valorant Comp Builder - Main App with Sidebar Navigation
Landing page entry point, no login required initially
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

# Page imports
from app.ui import landing_page
from app.ui import builder_page
from app.ui import meta_tracker_page
from app.ui import saved_comps_page
from app.ui import account_page
from app.ui import agents_used_page
from app.ui import login_page_google_oauth

# Set page config
st.set_page_config(
    page_title="Valorant Comp Builder",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="auto"
)

# Initialize session state
if "current_page" not in st.session_state:
    st.session_state.current_page = "landing"
    st.session_state.has_seen_landing = False

# If Google redirected back with ?code=, route to login so the callback runs
try:
    _has_code = "code" in st.query_params
except Exception:
    _has_code = "code" in st.experimental_get_query_params()
if _has_code and not st.session_state.get("user_logged_in", False):
    st.session_state.current_page = "login"

if "user_logged_in" not in st.session_state:
    st.session_state.user_logged_in = False

# Main app flow
def main():
    """Main application flow"""
    
    # Landing page - no login required, no sidebar
    if st.session_state.current_page == "landing":
        landing_page.render()
        return
    
    # For all other pages, show sidebar navigation
    render_sidebar()
    render_main_content()

def render_sidebar():
    """Render sidebar navigation"""
    
    with st.sidebar:
        st.markdown("""<div style="text-align:center;padding:14px 8px;"><svg width="42" height="42" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" style="filter:drop-shadow(0 2px 8px rgba(255,70,85,0.4));"><path d="M8 14 L40 14 L50 40 L60 14 L92 14 L58 86 L42 86 Z" fill="#ff4655"/><path d="M8 14 L40 14 L50 40 L42 50 Z" fill="#ff6b78" opacity="0.55"/></svg><div style="font-weight:800;font-size:0.72rem;letter-spacing:1.5px;color:#ff4655;margin-top:8px;">GYDRENZIN'S</div><div style="font-weight:700;font-size:0.92rem;color:#ece8e1;margin-top:1px;">Valorant Comp Builder</div><div style="display:inline-block;margin-top:6px;padding:1px 9px;border-radius:10px;background:rgba(255,70,85,0.12);border:1px solid rgba(255,70,85,0.35);font-size:0.6rem;letter-spacing:1px;color:#ff8c42;font-weight:700;">V1</div></div>""", unsafe_allow_html=True)
        st.markdown("---")
        
        # Features section
        st.markdown("## 🎮 Features")
        
        if st.button("🎯 Build Composition", use_container_width=True, 
                    key="nav_builder"):
            st.session_state.current_page = "builder"
            st.rerun()
        
        if st.button("📊 Meta Tracker", use_container_width=True,
                    key="nav_meta"):
            st.session_state.current_page = "meta"
            st.rerun()
        
        if st.button("📈 Agent Stats", use_container_width=True,
                    key="nav_agents"):
            st.session_state.current_page = "agents_used"
            st.rerun()
        
        if st.button("💾 Saved Comps", use_container_width=True,
                    key="nav_saved"):
            st.session_state.current_page = "saved"
            st.rerun()
        
        st.markdown("---")
        
        # Account section
        st.markdown("## 👤 Account")
        
        if st.session_state.user_logged_in:
            user_email = st.session_state.get("user_email", "User")
            st.markdown(f"**Logged in as:**  \n{user_email}")
            
            if st.button("⚙️ Account Settings", use_container_width=True,
                        key="nav_account"):
                st.session_state.current_page = "account"
                st.rerun()
            
            if st.button("🚪 Logout", use_container_width=True,
                        key="logout_btn"):
                st.session_state.user_logged_in = False
                st.session_state.user_email = None
                st.session_state.current_page = "builder"
                st.success("Logged out successfully!")
                st.rerun()
        else:
            if st.button("🔐 Login with Google", use_container_width=True,
                        key="nav_login"):
                st.session_state.current_page = "login"
                st.rerun()
        
        st.markdown("---")
        
        # Back to landing
def render_main_content():
    """Render main content based on current page"""
    
    # Handle login page
    if st.session_state.current_page == "login":
        login_page_google_oauth.render()
        return
    
    # Handle saved comps (login required)
    if st.session_state.current_page == "saved":
        if not st.session_state.user_logged_in:
            st.warning("⚠️ Please login to view saved compositions")
            st.info("Click 'Login with Google' in the sidebar to get started!")
            return
    
    # Handle account (login required)
    if st.session_state.current_page == "account":
        if not st.session_state.user_logged_in:
            st.warning("⚠️ Please login to access account settings")
            st.info("Click 'Login with Google' in the sidebar to get started!")
            return
    
    # Render current page
    if st.session_state.current_page == "builder":
        builder_page.render()
    elif st.session_state.current_page == "meta":
        meta_tracker_page.render()
    elif st.session_state.current_page == "agents_used":
        agents_used_page.render()
    elif st.session_state.current_page == "saved":
        saved_comps_page.render()
    elif st.session_state.current_page == "account":
        account_page.render()
    else:
        builder_page.render()

if __name__ == "__main__":
    main()