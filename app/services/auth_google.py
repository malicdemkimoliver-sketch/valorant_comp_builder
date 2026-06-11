"""
Google OAuth Authentication Service
Handles Google login and user session management
"""
import streamlit as st
import requests
from datetime import datetime
import hashlib

# Google OAuth Configuration
GOOGLE_CLIENT_ID = "YOUR_CLIENT_ID.apps.googleusercontent.com"
GOOGLE_REDIRECT_URI = "http://localhost:8501"  # Streamlit default

def init_auth_state():
    """Initialize authentication state"""
    if "user_info" not in st.session_state:
        st.session_state.user_info = None
    if "auth_token" not in st.session_state:
        st.session_state.auth_token = None
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False

def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return st.session_state.get("is_authenticated", False)

def get_user_info():
    """Get current user info"""
    return st.session_state.get("user_info")

def set_user(user_info: dict):
    """Set user session after successful login"""
    st.session_state.user_info = user_info
    st.session_state.is_authenticated = True
    st.session_state.auth_token = generate_token(user_info.get("email"))
    
    # Save to localStorage for persistence
    st.markdown(f"""
    <script>
    localStorage.setItem('user_email', '{user_info.get("email")}');
    localStorage.setItem('user_name', '{user_info.get("name")}');
    localStorage.setItem('user_picture', '{user_info.get("picture", "")}');
    localStorage.setItem('auth_token', '{st.session_state.auth_token}');
    localStorage.setItem('login_time', '{datetime.now().isoformat()}');
    </script>
    """, unsafe_allow_html=True)

def logout():
    """Logout user and clear session"""
    st.session_state.user_info = None
    st.session_state.is_authenticated = False
    st.session_state.auth_token = None
    
    # Clear localStorage
    st.markdown("""
    <script>
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_name');
    localStorage.removeItem('user_picture');
    localStorage.removeItem('auth_token');
    localStorage.removeItem('login_time');
    </script>
    """, unsafe_allow_html=True)

def generate_token(email: str) -> str:
    """Generate authentication token"""
    timestamp = datetime.now().isoformat()
    data = f"{email}:{timestamp}"
    return hashlib.sha256(data.encode()).hexdigest()

def render_google_login_button():
    """
    Render Google Login button
    Note: For production, use proper OAuth library like google-auth-oauthlib
    """
    st.markdown("""
    <script src="https://accounts.google.com/gsi/client" async defer></script>
    <div id="g_id_onload"
         data-client_id="YOUR_CLIENT_ID.apps.googleusercontent.com"
         data-callback="handleCredentialResponse">
    </div>
    <div class="g_id_signin" data-type="standard"></div>
    
    <script>
    function handleCredentialResponse(response) {
        // Parse JWT token
        const base64Url = response.credential.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(
            atob(base64).split('').map((c) => {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join('')
        );
        const userData = JSON.parse(jsonPayload);
        
        // Send to Streamlit
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: {
                email: userData.email,
                name: userData.name,
                picture: userData.picture
            }
        }, '*');
    }
    </script>
    """, unsafe_allow_html=True)

def check_stored_login():
    """Check if user was previously logged in (from localStorage)"""
    st.markdown("""
    <script>
    const email = localStorage.getItem('user_email');
    const name = localStorage.getItem('user_name');
    const picture = localStorage.getItem('user_picture');
    
    if (email && name) {
        // User was previously logged in
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: {
                restore: true,
                email: email,
                name: name,
                picture: picture
            }
        }, '*');
    }
    </script>
    """, unsafe_allow_html=True)

