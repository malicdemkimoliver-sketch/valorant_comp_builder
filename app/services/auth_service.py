"""
Auth service — Google OAuth 2.0 via standard requests.
Uses st.query_params to capture the callback code (works on Streamlit Cloud).
Configure credentials in .streamlit/secrets.toml.
"""
import streamlit as st
import requests
from urllib.parse import urlencode, urlparse

def _cfg(key, default=""):
    try:    return st.secrets.get(key, default)
    except: return default

def google_auth_url() -> str:
    params = {
        "client_id":     _cfg("GOOGLE_CLIENT_ID"),
        "redirect_uri":  _cfg("REDIRECT_URI", "http://localhost:8501"),
        "response_type": "code",
        "scope":         "openid email profile",
        "access_type":   "offline",
        "prompt":        "select_account",
    }
    return "https://accounts.google.com/o/oauth2/auth?" + urlencode(params)

def exchange_code(code: str) -> dict:
    resp = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id":     _cfg("GOOGLE_CLIENT_ID"),
        "client_secret": _cfg("GOOGLE_CLIENT_SECRET"),
        "code":          code,
        "redirect_uri":  _cfg("REDIRECT_URI", "http://localhost:8501"),
        "grant_type":    "authorization_code",
    }, timeout=10)
    return resp.json()

def get_google_user(access_token: str) -> dict:
    resp = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    return resp.json()

def handle_oauth_callback() -> bool:
    """
    Call this at the very top of app.py.
    Returns True if a new login was processed.
    """
    params = st.query_params
    code   = params.get("code")
    if not code or st.session_state.get("user"):
        return False
    try:
        token_data = exchange_code(code)
        if "access_token" not in token_data:
            st.error(f"OAuth error: {token_data.get('error_description','unknown')}")
            return False
        user_info = get_google_user(token_data["access_token"])
        if "email" not in user_info:
            st.error("Could not retrieve Google profile.")
            return False
        # Persist to DB
        from app.services.db_service import upsert_user
        user = upsert_user(
            google_id = user_info["id"],
            email     = user_info["email"],
            name      = user_info.get("name", user_info["email"]),
            picture   = user_info.get("picture", ""),
        )
        st.session_state["user"] = user
        st.query_params.clear()
        return True
    except Exception as e:
        st.error(f"Login failed: {e}")
        return False

def is_logged_in() -> bool:
    return bool(st.session_state.get("user"))

def current_user() -> dict:
    return st.session_state.get("user", {})

def logout():
    st.session_state.pop("user", None)
    st.rerun()

def google_configured() -> bool:
    return bool(_cfg("GOOGLE_CLIENT_ID"))
