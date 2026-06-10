"""
Session Manager - Handle persistent login with localStorage
"""
import streamlit as st
from datetime import datetime, timedelta
import hashlib

def init_session():
    """Initialize session state"""
    if "user" not in st.session_state:
        st.session_state.user = None
    if "auth_token" not in st.session_state:
        st.session_state.auth_token = None
    if "login_time" not in st.session_state:
        st.session_state.login_time = None
    if "session_mobile" not in st.session_state:
        st.session_state.session_mobile = False

def set_user(user_data: dict, token: str):
    """Set user session"""
    st.session_state.user = user_data
    st.session_state.auth_token = token
    st.session_state.login_time = datetime.now().isoformat()
    
    # Save to browser localStorage via JavaScript
    st.markdown(f"""
    <script>
    localStorage.setItem('auth_token', '{token}');
    localStorage.setItem('user_email', '{user_data.get("email", "")}');
    localStorage.setItem('login_time', '{st.session_state.login_time}');
    </script>
    """, unsafe_allow_html=True)

def get_user():
    """Get current user"""
    return st.session_state.user

def is_logged_in() -> bool:
    """Check if user is logged in"""
    return st.session_state.user is not None and st.session_state.auth_token is not None

def logout():
    """Logout user"""
    st.session_state.user = None
    st.session_state.auth_token = None
    st.session_state.login_time = None
    
    # Clear localStorage
    st.markdown("""
    <script>
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_email');
    localStorage.removeItem('login_time');
    </script>
    """, unsafe_allow_html=True)

def restore_session_from_storage():
    """Restore session from localStorage"""
    st.markdown("""
    <script>
    // Get stored session
    const token = localStorage.getItem('auth_token');
    const email = localStorage.getItem('user_email');
    const loginTime = localStorage.getItem('login_time');
    
    // Send to Streamlit via hidden form
    if (token && email) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = window.location.href;
        
        const tokenInput = document.createElement('input');
        tokenInput.type = 'hidden';
        tokenInput.name = 'restore_token';
        tokenInput.value = token;
        form.appendChild(tokenInput);
        
        const emailInput = document.createElement('input');
        emailInput.type = 'hidden';
        emailInput.name = 'restore_email';
        emailInput.value = email;
        form.appendChild(emailInput);
        
        // Store in sessionStorage for Streamlit to read
        sessionStorage.setItem('streamlit_restore_token', token);
        sessionStorage.setItem('streamlit_restore_email', email);
    }
    </script>
    """, unsafe_allow_html=True)

def get_mobile_mode() -> bool:
    """Check if running in mobile mode"""
    return st.session_state.session_mobile

def set_mobile_mode(is_mobile: bool):
    """Set mobile mode"""
    st.session_state.session_mobile = is_mobile

def generate_token(email: str) -> str:
    """Generate auth token"""
    timestamp = datetime.now().isoformat()
    data = f"{email}:{timestamp}"
    return hashlib.sha256(data.encode()).hexdigest()
