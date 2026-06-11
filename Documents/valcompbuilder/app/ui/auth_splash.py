"""
Auth Splash — shows a branded "Signing you in..." screen while the Google
OAuth code is exchanged, instead of flashing the logged-out UI and then
suddenly refreshing into a logged-in state.

INTEGRATION (app.py) — make this the FIRST thing inside main():

    from app.ui.auth_splash import handle_oauth_splash
    def main():
        if handle_oauth_splash():
            return          # splash handled this run; next rerun is logged in
        ...rest of main()...

Then find your existing code that exchanges the OAuth ?code= for a user
profile, and MOVE that call into _exchange_code() below (one marked line).
"""
import time
import streamlit as st


def _splash(message: str):
    st.markdown(f"""
    <style>
      [data-testid="stSidebar"], header {{ display: none !important; }}
    </style>
    <div style="position:fixed;inset:0;z-index:9999;
                background:linear-gradient(135deg,#0f1923 0%,#1a2332 50%,#2d1b3d 100%);
                display:flex;flex-direction:column;align-items:center;justify-content:center;gap:22px;">
        <div style="font-family:sans-serif;font-weight:900;font-size:2rem;letter-spacing:2px;">
            <span style="color:#ff4655;">VALORANT</span>
            <span style="color:#ff8c42;"> COMP BUILDER</span>
        </div>
        <div style="width:46px;height:46px;border:4px solid rgba(255,70,85,0.2);
                    border-top-color:#ff4655;border-radius:50%;
                    animation:vspin 0.9s linear infinite;"></div>
        <div style="color:#cbd5e1;font-size:1rem;font-family:sans-serif;">{message}</div>
        <style>@keyframes vspin {{ to {{ transform: rotate(360deg); }} }}</style>
    </div>
    """, unsafe_allow_html=True)


def _exchange_code(code: str) -> bool:
    """
    Exchange the OAuth authorization code for a user profile and store it
    in session state. Returns True on success.

    >>> REPLACE the body below with YOUR existing exchange call — it's the
    >>> same code that currently runs when the app detects ?code= in the URL
    >>> (look in google_oauth_proper.py / login_page_google_oauth.py).
    """
    try:
        from app.services.google_oauth_proper import handle_oauth_callback  # adjust name if different
        return bool(handle_oauth_callback(code))
    except Exception as e:
        st.session_state["auth_error"] = str(e)
        return False


def handle_oauth_splash() -> bool:
    """
    Returns True if this run was consumed by the auth splash (caller should
    return immediately). Returns False when there's nothing auth-related
    to do — normal app flow continues.
    """
    # Already logged in → nothing to do
    if st.session_state.get("user") or st.session_state.get("user_email"):
        return False

    qp = st.query_params
    code = qp.get("code")
    if not code:
        return False

    # Show the splash, do the exchange, then land in the app logged in
    _splash("Signing you in with Google…")
    ok = _exchange_code(code)

    # Clean the ?code= from the URL so reruns don't re-trigger
    try:
        st.query_params.clear()
    except Exception:
        pass

    if ok:
        _splash("Welcome back! Loading your profile…")
        time.sleep(0.8)   # brief beat so the transition reads as intentional
    st.rerun()
    return True
