"""
Login Page with Proper Google OAuth 2.0 Redirect Flow
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.services.google_oauth_proper import (
    handle_oauth_callback, 
    is_user_logged_in, 
    render_google_login_button,
    logout_user
)
from app.services.database_enhanced import create_user, get_user as db_get_user

def render():
    """Render login page with Google OAuth"""
    
    st.set_page_config(page_title="Valorant Comp Builder - Login", layout="centered")
    
    # Handle OAuth callback first
    handle_oauth_callback()
    
    # If already logged in, show success
    if is_user_logged_in():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 40px 0;">
                <h1>⚙️ Valorant Comp Builder</h1>
            </div>
            """, unsafe_allow_html=True)
        
        user_email = st.session_state.get("user_email")
        user_name = st.session_state.get("user_name")
        
        st.success(f"✅ Logged in as {user_name or user_email}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏠 Go to Builder", use_container_width=True):
                st.session_state.current_page = "builder"
                st.rerun()
        with col2:
            if st.button("🚪 Logout", use_container_width=True):
                logout_user()
                st.rerun()
        return
    
    # Show login page
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 40px 0;">
            <h1>⚙️ Valorant Comp Builder</h1>
            <p style="color: #999; font-size: 16px;">Build better team compositions</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="padding: 20px; background: #0f1e35; border-radius: 8px; text-align: center; margin: 20px 0;">
        <h2>🔐 Secure Login with Google</h2>
        <p>Login with your Google account to save compositions and access them across devices.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Google OAuth Button
    st.markdown(render_google_login_button(), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Demo/Testing section
    with st.expander("📝 Demo Login (Testing Only)"):
        st.info("For testing purposes, you can use demo accounts:")
        
        demo_accounts = [
            ("kimma@example.com", "Kimma"),
            ("user2@example.com", "Test User 2"),
            ("user3@example.com", "Test User 3"),
        ]
        
        col1, col2, col3 = st.columns(3)
        for idx, (email, name) in enumerate(demo_accounts):
            with [col1, col2, col3][idx]:
                if st.button(f"Login as {name}", use_container_width=True, key=f"demo_{idx}"):
                    # Create user if not exists
                    create_user(email, name)
                    
                    # Set session
                    st.session_state.user_logged_in = True
                    st.session_state.user_email = email
                    st.session_state.user_name = name
                    st.session_state.current_page = "builder"
                    
                    st.success(f"✅ Logged in as {name}")
                    st.rerun()
    
    st.markdown("""
    <div style="padding: 20px; margin-top: 40px; background: #1a2f4a; border-radius: 8px; text-align: center; color: #aaa;">
        <p><strong>🔒 Your Data is Secure</strong></p>
        <p>• Google manages your account security</p>
        <p>• We only store your email and compositions</p>
        <p>• Your data is never shared</p>
        <p>• Revoke access anytime via Google Account</p>
    </div>
    """, unsafe_allow_html=True)

