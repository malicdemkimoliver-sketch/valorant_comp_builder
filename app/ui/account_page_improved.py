"""
Improved Account Page - Persistent Login with localStorage
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.services.session_manager import init_session, set_user, get_user, is_logged_in, logout, generate_token
from app.services.database_enhanced import create_user, get_user as db_get_user, get_user_compositions, update_user_settings

def render():
    """Render account page"""
    init_session()
    
    st.markdown('<h1 class="page-title">👤 Account</h1>', unsafe_allow_html=True)
    
    # Try to restore session from localStorage
    if not is_logged_in():
        st.markdown("""
        <script>
        const token = localStorage.getItem('auth_token');
        const email = localStorage.getItem('user_email');
        if (token && email) {
            window.location.href = window.location.href + '?restore=true';
        }
        </script>
        """, unsafe_allow_html=True)
    
    if is_logged_in():
        render_logged_in()
    else:
        render_login()

def render_login():
    """Render login form"""
    st.markdown("### Login")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        email = st.text_input("Email", placeholder="your@email.com", key="login_email")
    with col2:
        if st.button("Sign In", use_container_width=True):
            if email:
                # Get or create user
                user = db_get_user(email)
                if not user:
                    result = create_user(email, email.split('@')[0])
                    user = result.get("user")
                
                if user:
                    # Generate token and set session
                    token = generate_token(email)
                    set_user(user, token)
                    st.success(f"✅ Logged in as {email}")
                    st.rerun()
            else:
                st.error("❌ Please enter email")
    
    st.markdown("---")
    st.info("💡 **No password needed** - Just enter your email to get started!")

def render_logged_in():
    """Render logged-in view"""
    user = get_user()
    db_user = db_get_user(user.get("email"))
    
    # User info
    st.markdown(f"### Welcome, {user.get('email', 'User')}!")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Compositions", db_user.get("stats", {}).get("total_comps", 0) if db_user else 0)
    with col2:
        st.metric("Account Age", "New" if db_user else "Unknown")
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.success("Logged out!")
            st.rerun()
    
    st.markdown("---")
    
    # Settings
    st.markdown("### Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        mobile_mode = st.checkbox(
            "📱 Enable Mobile Mode",
            value=db_user.get("settings", {}).get("mobile_mode", False) if db_user else False,
            key="mobile_mode_toggle"
        )
    with col2:
        notifications = st.checkbox(
            "🔔 Enable Notifications",
            value=db_user.get("settings", {}).get("notifications", True) if db_user else True,
            key="notifications_toggle"
        )
    
    if st.button("💾 Save Settings", use_container_width=True):
        if db_user:
            update_user_settings(user.get("email"), {
                "mobile_mode": mobile_mode,
                "notifications": notifications
            })
            st.success("✅ Settings saved!")
    
    st.markdown("---")
    
    # Saved compositions
    st.markdown("### Your Compositions")
    
    if db_user:
        comps = get_user_compositions(user.get("email"))
        if comps:
            for comp in comps:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{comp.get('map')}** - {', '.join([a for a in comp.get('agents', [])])}")
                with col2:
                    st.metric("Score", f"{comp.get('score', '?')}", delta=comp.get('grade'))
                with col3:
                    if st.button("🗑️", key=f"delete_{comp.get('id')}"):
                        st.info("Delete composition feature coming soon")
        else:
            st.info("No saved compositions yet. Build one to get started!")
    
    st.markdown("---")
    
    # Debug info
    with st.expander("🔧 Debug Info"):
        st.write(f"**Email:** {user.get('email')}")
        st.write(f"**Token:** {st.session_state.auth_token[:20]}...")
        st.write(f"**Mobile Mode:** {st.session_state.session_mobile}")

