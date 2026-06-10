"""
Proper Google OAuth 2.0 Implementation for Streamlit
Uses redirect flow with secure token exchange
"""
import streamlit as st
import requests
import json
from urllib.parse import urlencode, parse_qs
from datetime import datetime
import os

# Google OAuth Configuration
GOOGLE_CLIENT_ID = "479281130427-ntgbl24stb04n08t7d1i7dcoibgvbsuc.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "YOUR_CLIENT_SECRET")  # Set via environment
REDIRECT_URI = "http://localhost:8501"  # Will be updated in production

# Google OAuth URLs
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

def init_oauth_session():
    """Initialize OAuth session state"""
    if "oauth_state" not in st.session_state:
        st.session_state.oauth_state = None
    if "oauth_code" not in st.session_state:
        st.session_state.oauth_code = None
    if "oauth_token" not in st.session_state:
        st.session_state.oauth_token = None

def get_google_auth_url(state: str) -> str:
    """Generate Google OAuth authorization URL"""
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "consent"
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

def exchange_code_for_token(code: str) -> dict:
    """Exchange authorization code for access token"""
    data = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }
    
    try:
        response = requests.post(GOOGLE_TOKEN_URL, data=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Token exchange failed: {e}")
        return None

def get_user_info(access_token: str) -> dict:
    """Get user info from Google using access token"""
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(GOOGLE_USERINFO_URL, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to get user info: {e}")
        return None

def handle_oauth_callback():
    """Handle OAuth callback from Google"""
    init_oauth_session()
    
    # Get authorization code from URL parameters
    query_params = st.query_params
    code = query_params.get("code")
    state = query_params.get("state")
    error = query_params.get("error")
    
    if error:
        st.error(f"OAuth Error: {error}")
        return False
    
    if code:
        # Exchange code for token
        token_response = exchange_code_for_token(code)
        
        if token_response and "access_token" in token_response:
            st.session_state.oauth_token = token_response["access_token"]
            
            # Get user info
            user_info = get_user_info(token_response["access_token"])
            
            if user_info:
                # Set user session
                set_authenticated_user(user_info, token_response.get("id_token"))
                
                # Clear query params
                st.query_params.clear()
                st.success(f"✅ Logged in as {user_info.get('email')}")
                st.rerun()
                return True
    
    return False

def set_authenticated_user(user_info: dict, id_token: str):
    """Set authenticated user in session"""
    st.session_state.user_logged_in = True
    st.session_state.user_email = user_info.get("email")
    st.session_state.user_name = user_info.get("name")
    st.session_state.user_picture = user_info.get("picture")
    st.session_state.oauth_id_token = id_token
    st.session_state.login_time = datetime.now().isoformat()
    
    # Save to localStorage for persistence
    st.markdown(f"""
    <script>
    localStorage.setItem('user_email', '{user_info.get("email")}');
    localStorage.setItem('user_name', '{user_info.get("name")}');
    localStorage.setItem('user_picture', '{user_info.get("picture", "")}');
    localStorage.setItem('login_time', '{datetime.now().isoformat()}');
    </script>
    """, unsafe_allow_html=True)

def is_user_logged_in() -> bool:
    """Check if user is logged in"""
    return st.session_state.get("user_logged_in", False)

def get_logged_in_user() -> dict:
    """Get current logged in user"""
    if is_user_logged_in():
        return {
            "email": st.session_state.get("user_email"),
            "name": st.session_state.get("user_name"),
            "picture": st.session_state.get("user_picture")
        }
    return None

def logout_user():
    """Logout user"""
    st.session_state.user_logged_in = False
    st.session_state.user_email = None
    st.session_state.user_name = None
    st.session_state.user_picture = None
    st.session_state.oauth_token = None
    st.session_state.oauth_id_token = None
    
    # Clear localStorage
    st.markdown("""
    <script>
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_name');
    localStorage.removeItem('user_picture');
    localStorage.removeItem('login_time');
    </script>
    """, unsafe_allow_html=True)

def render_google_login_button() -> str:
    """Generate Google login button HTML"""
    auth_url = get_google_auth_url("state_parameter")
    
    return f"""
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
    """

