"""Account Page - User authentication and settings with database"""
import streamlit as st
from app.services.database import add_or_update_user, get_user_comps

def render():
    st.markdown('<h1 class="page-title">👤 Account</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Manage your profile and preferences</p>', unsafe_allow_html=True)
    
    if st.session_state.get("user_logged_in"):
        # ─── LOGGED IN ──────────────────────────────────────────────
        st.markdown("""
        <div style="background:#0f1e35;border:1px solid #10b98144;border-radius:12px;padding:20px;margin-bottom:20px;">
            <div style="color:#10b981;font-weight:700;margin-bottom:8px;">✅ Logged In</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Your Profile")
            st.markdown(f"**Email:** {st.session_state.user_email}")
            st.markdown(f"**Name:** {st.session_state.get('user_name', 'User')}")
            
            comps = get_user_comps(st.session_state.user_email)
            st.markdown(f"**Saved Comps:** {len(comps)}")
        
        with col2:
            st.markdown("### Settings")
            theme = st.selectbox("Theme:", ["Dark (Default)", "Light"], key="theme_select")
            language = st.selectbox("Language:", ["English", "Español", "中文"], key="lang_select")
            notifications = st.checkbox("Email notifications", value=True, key="notif_check")
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 View Comps", use_container_width=True):
                st.session_state.current_page = "saved"
                st.rerun()
        
        with col2:
            if st.button("⚙️ Preferences", use_container_width=True):
                st.info("Preferences updated!")
        
        with col3:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.user_logged_in = False
                st.session_state.user_email = None
                st.session_state.current_page = "builder"
                st.success("Logged out!")
                st.rerun()
    
    else:
        # ─── NOT LOGGED IN ──────────────────────────────────────────
        st.markdown("### 🔐 Login to Your Account")
        
        st.markdown("""
        Login to save your compositions and access them across devices.
        """)
        
        # Simulated Google Login (in production, use OAuth2)
        st.markdown("---")
        
        col1, col2 = st.columns([1.5, 1])
        
        with col1:
            email = st.text_input("Email:", placeholder="your.email@gmail.com", key="login_email")
        
        with col2:
            if st.button("🔐 Login with Email", use_container_width=True, type="primary", key="btn_email_login"):
                if email and "@" in email:
                    add_or_update_user(email, email.split("@")[0])
                    st.session_state.user_logged_in = True
                    st.session_state.user_email = email
                    st.success(f"✅ Logged in as {email}!")
                    st.rerun()
                else:
                    st.error("Enter a valid email")
        
        st.markdown("---")
        
        st.markdown("### 📌 Demo Users (For Testing)")
        demo_emails = ["kimma@example.com", "user2@example.com", "user3@example.com"]
        
        for demo_email in demo_emails:
            if st.button(f"Login as {demo_email}", key=f"demo_{demo_email}", use_container_width=True):
                add_or_update_user(demo_email, demo_email.split("@")[0])
                st.session_state.user_logged_in = True
                st.session_state.user_email = demo_email
                st.success(f"✅ Logged in as {demo_email}!")
                st.rerun()
        
        st.markdown("---")
        st.info("💡 **Note:** In production, use Google OAuth2 for secure login. This is a simplified demo.")
