"""
Login Page with Google OAuth - Simplified Version
Works with existing database structure
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.services.google_oauth_proper import handle_oauth_callback, is_user_logged_in

def render():
    """Render login page"""
    
    st.set_page_config(page_title="Valorant Comp Builder - Login", layout="centered")
    
    # Handle OAuth callback
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
                from app.services.google_oauth_proper import logout_user
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
        <h2>🔐 Secure Login</h2>
        <p>Login with your Google account to get started.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Google OAuth Button
    from app.services.google_oauth_proper import get_google_auth_url
    auth_url = get_google_auth_url("state_parameter")
    
    st.markdown(f"""
    <div style="text-align: center; padding: 20px;">
        <a href="{auth_url}" style="
            display: inline-block;
            padding: 12px 24px;
            background: #4285F4;
            color: white;
            border-radius: 4px;
            text-decoration: none;
            font-weight: 500;
            font-size: 1rem;
            border: 1px solid #4285F4;
            cursor: pointer;
            transition: all 0.3s ease;
        " onmouseover="this.style.backgroundColor='#3367D6'" onmouseout="this.style.backgroundColor='#4285F4'">
            🔐 Login with Google
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    <div style="padding: 20px; margin-top: 40px; background: #1a2f4a; border-radius: 8px; text-align: center; color: #aaa;">
        <p><strong>🔒 Your Data is Secure</strong></p>
        <p>• Google manages your authentication securely</p>
        <p>• We only store your email and team compositions</p>
        <p>• No password stored - OAuth 2.0 only</p>
    </div>
    """, unsafe_allow_html=True)

