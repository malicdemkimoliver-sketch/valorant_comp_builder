"""
Google OAuth Login Page
Required authentication before accessing the app
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.services.auth_google import is_authenticated, get_user_info, set_user, render_google_login_button
from app.services.database_enhanced import create_user, get_user as db_get_user

def render():
    """Render login page"""
    
    # Set page style
    st.set_page_config(page_title="Valorant Comp Builder - Login", layout="centered")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 40px 0;">
            <h1>⚙️ Valorant Comp Builder</h1>
            <p style="color: #999; font-size: 16px;">Build better team compositions</p>
        </div>
        """, unsafe_allow_html=True)
    
    if is_authenticated():
        st.success(f"✅ Logged in as {get_user_info().get('name', 'User')}")
        if st.button("Logout", use_container_width=True):
            from app.services.auth_google import logout
            logout()
            st.rerun()
        return
    
    st.markdown("""
    <div style="padding: 20px; background: #0f1e35; border-radius: 8px; text-align: center;">
        <h2>Welcome!</h2>
        <p>Login with your Google account to get started.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Google login button
    render_google_login_button()
    
    st.markdown("---")
    
    # Manual fallback login (for testing/development)
    with st.expander("🔐 Or login with email (Development Only)"):
        email = st.text_input("Email", placeholder="your@email.com", key="dev_email")
        name = st.text_input("Display Name", placeholder="Your Name", key="dev_name")
        
        if st.button("Sign In with Email", use_container_width=True):
            if email and name:
                # Create/get user
                result = create_user(email, name)
                user_data = result.get("user") or db_get_user(email)
                
                if user_data:
                    set_user(user_data)
                    st.success(f"✅ Welcome, {name}!")
                    st.rerun()
            else:
                st.error("Please enter both email and name")
    
    st.markdown("""
    <div style="padding: 20px; margin-top: 40px; background: #1a2f4a; border-radius: 8px; text-align: center; color: #aaa;">
        <p><strong>Why login?</strong></p>
        <p>• Save your team compositions</p>
        <p>• Track your comp builder history</p>
        <p>• Personalized recommendations</p>
        <p>• Sync across devices</p>
    </div>
    """, unsafe_allow_html=True)

