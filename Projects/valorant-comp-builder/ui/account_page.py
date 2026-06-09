"""
Account Page - User authentication and settings
"""
import streamlit as st

def render():
    """Render the account page"""
    st.markdown("""
    <div class="page-title">👤 Account Settings</div>
    <div class="page-subtitle">Manage your profile and preferences</div>
    """, unsafe_allow_html=True)
    
    if st.session_state.user_logged_in:
        # Show account info for logged-in users
        st.markdown("### Your Account")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="card">
                <p style='margin:0 0 8px 0; color:var(--text-secondary); font-size:0.9rem;'>Email</p>
                <p style='margin:0; font-weight:600; color:var(--text-primary);'>""" + st.session_state.user_email + """</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="card">
                <p style='margin:0 0 8px 0; color:var(--text-secondary); font-size:0.9rem;'>Status</p>
                <p style='margin:0; font-weight:600; color:var(--accent-green);'>✅ Verified</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            theme = st.selectbox(
                "Theme Preference:",
                options=["Dark (Default)", "Light (Coming Soon)"],
                disabled=True
            )
        
        with col2:
            notifications = st.checkbox("Enable Notifications", value=True)
        
        st.markdown("---")
        
        st.markdown("### Saved Data")
        
        if "saved_comps" in st.session_state:
            num_comps = len(st.session_state.saved_comps)
            st.info(f"📊 You have {num_comps} saved composition(s)")
        
        if st.button("🗑️ Clear All Data", key="btn_clear_data"):
            if st.session_state.get("confirm_clear"):
                st.session_state.saved_comps = []
                st.success("✅ All data cleared")
            else:
                st.session_state.confirm_clear = True
                st.warning("⚠️ Click again to confirm clearing all data")
        
        st.markdown("---")
        
        st.markdown("### Account Actions")
        
        if st.button("🚪 Logout", key="btn_logout_account", use_container_width=True):
            st.session_state.user_logged_in = False
            st.session_state.user_email = None
            st.session_state.current_page = "builder"
            st.success("✅ Logged out successfully!")
            st.rerun()
    
    else:
        # Show login screen for non-logged-in users
        st.markdown("### Sign In to Your Account")
        
        st.info("🔐 Login with Google to save your compositions and access advanced features")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🔐 Sign in with Google", use_container_width=True, key="btn_google_login"):
                # Simulate Google login
                st.session_state.user_logged_in = True
                st.session_state.user_email = "user@example.com"  # Replace with actual OAuth
                st.success("✅ Successfully logged in!")
                st.rerun()
        
        st.markdown("---")
        
        st.markdown("### Benefits of Signing In")
        
        benefits = [
            "💾 Save compositions to cloud",
            "📊 Track your meta preferences",
            "🎯 Sync across devices",
            "🏆 View your comp history",
            "📱 Share comps with teammates"
        ]
        
        for benefit in benefits:
            st.markdown(f"✅ {benefit}")
        
        st.markdown("---")
        
        st.markdown("### Privacy")
        
        st.info("""
        We respect your privacy:
        - Your compositions are encrypted
        - We never share your email
        - Data is stored securely
        - You can delete anytime
        """)
