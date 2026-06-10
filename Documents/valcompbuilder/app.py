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
        st.markdown("# ⚙️ Valorant Comp Builder")
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
        if st.button("🏠 Back to Landing", use_container_width=True,
                    key="nav_home"):
            st.session_state.current_page = "landing"
            st.rerun()

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

