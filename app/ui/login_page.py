"""
Login page — Google OAuth + guest mode.
"""
import streamlit as st
import streamlit.components.v1 as components
from app.services.auth_service import google_auth_url, google_configured, is_logged_in, current_user, logout
from app.services.db_service import get_user_comps


def render_login_banner():
    """Slim banner shown at top of every page when not logged in."""
    if is_logged_in():
        user = current_user()
        pic  = user.get("picture","")
        name = user.get("name","User")
        col_pic, col_name, col_out = st.columns([0.3, 3, 1])
        with col_pic:
            if pic:
                components.html(f'<img src="{pic}" style="width:32px;height:32px;border-radius:50%;border:2px solid #10b981;display:block;">',height=36)
        with col_name:
            st.markdown(f'<div style="font-size:0.8rem;color:#10b981;font-weight:600;padding-top:6px;">✅ {name}</div>', unsafe_allow_html=True)
        with col_out:
            if st.button("Sign out", key="signout_banner", use_container_width=True):
                logout()
    else:
        col_msg, col_btn = st.columns([3,1])
        with col_msg:
            st.markdown('<div style="font-size:0.78rem;color:#475569;padding-top:6px;">🔒 Sign in with Google to save comps to the cloud</div>', unsafe_allow_html=True)
        with col_btn:
            if google_configured():
                url = google_auth_url()
                st.markdown(f'''<a href="{url}" target="_self" style="display:block;text-align:center;
                    background:linear-gradient(135deg,#4285F4,#34A853);color:#fff;padding:6px 12px;
                    border-radius:8px;font-size:0.75rem;font-weight:700;text-decoration:none;">
                    🔑 Sign in with Google</a>''', unsafe_allow_html=True)
            else:
                st.markdown('<div style="font-size:0.7rem;color:#334155;">Configure Google OAuth in secrets.toml</div>', unsafe_allow_html=True)


def render():
    """Full login/profile page."""
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">👤 Account</h1>
        <p class="page-subtitle">Sign in with Google to save comps to the cloud and access them anywhere</p>
    </div>""", unsafe_allow_html=True)

    if is_logged_in():
        _render_profile()
    else:
        _render_login()


def _render_login():
    col, _ = st.columns([1, 1])
    with col:
        st.markdown("""
        <div style="background:#0f1e35;border:1px solid #1a2f4a;border-radius:14px;padding:32px 28px;text-align:center;">
            <div style="font-size:3rem;margin-bottom:12px;">🎯</div>
            <div style="font-family:Rajdhani,sans-serif;font-size:1.4rem;font-weight:700;color:#e2e8f0;margin-bottom:6px;">Gyd's Comp Helper</div>
            <div style="font-size:0.82rem;color:#475569;margin-bottom:24px;">Sign in to sync your comps across devices</div>
        </div>""", unsafe_allow_html=True)

        if google_configured():
            url = google_auth_url()
            st.markdown(f"""
            <div style="margin-top:16px;text-align:center;">
                <a href="{url}" target="_self" style="display:inline-flex;align-items:center;gap:10px;
                    background:#fff;color:#333;padding:12px 24px;border-radius:10px;
                    font-size:0.9rem;font-weight:600;text-decoration:none;
                    box-shadow:0 2px 12px rgba(0,0,0,0.3);">
                    <svg width="20" height="20" viewBox="0 0 48 48">
                      <path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9 3.2l6.7-6.7C35.7 2.5 30.2 0 24 0 14.7 0 6.7 5.4 2.7 13.3l7.8 6.1C12.4 13 17.7 9.5 24 9.5z"/>
                      <path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v8.5h12.7c-.6 3-2.3 5.5-4.8 7.2l7.6 5.9c4.4-4.1 7-10.1 7-17.1z"/>
                      <path fill="#FBBC05" d="M10.5 28.6A14.5 14.5 0 0 1 9.5 24c0-1.6.3-3.2.8-4.6l-7.8-6.1A24 24 0 0 0 0 24c0 3.9.9 7.5 2.7 10.7l7.8-6.1z"/>
                      <path fill="#34A853" d="M24 48c6.2 0 11.4-2 15.2-5.5l-7.6-5.9c-2 1.4-4.6 2.2-7.6 2.2-6.3 0-11.6-4.2-13.5-10l-7.8 6.1C6.7 42.6 14.7 48 24 48z"/>
                    </svg>
                    Continue with Google
                </a>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#0a1628;border:1px solid #f59e0b44;border-radius:10px;padding:16px;margin-top:16px;">
                <div style="color:#f59e0b;font-weight:700;font-size:0.85rem;margin-bottom:8px;">⚙️ Google OAuth not configured</div>
                <div style="font-size:0.78rem;color:#64748b;line-height:1.7;">
                    Add these to <code style="color:#94a3b8;">.streamlit/secrets.toml</code>:<br>
                    <code style="color:#00d4ff;">GOOGLE_CLIENT_ID = "your-client-id"</code><br>
                    <code style="color:#00d4ff;">GOOGLE_CLIENT_SECRET = "your-secret"</code><br>
                    <code style="color:#00d4ff;">REDIRECT_URI = "http://localhost:8501"</code>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center;margin-top:16px;font-size:0.72rem;color:#1e3a5f;">
            Or continue as guest — comps saved locally only
        </div>""", unsafe_allow_html=True)


def _render_profile():
    user = current_user()
    pic  = user.get("picture","")
    name = user.get("name","User")
    email= user.get("email","")
    uid  = user.get("id","")

    # Profile header
    pcol, dcol = st.columns([1,3])
    with pcol:
        if pic:
            components.html(f'''<img src="{pic}" style="width:88px;height:88px;border-radius:50%;
                border:3px solid #10b981;display:block;margin:0 auto;">''', height=100)
    with dcol:
        st.markdown(f"""
        <div style="padding-top:8px;">
            <div style="font-family:Rajdhani,sans-serif;font-size:1.4rem;font-weight:700;color:#e2e8f0;">{name}</div>
            <div style="font-size:0.8rem;color:#64748b;">{email}</div>
            <div style="margin-top:8px;"><span style="background:#10b98122;border:1px solid #10b98155;color:#10b981;
                padding:2px 10px;border-radius:10px;font-size:0.68rem;font-weight:700;">✅ Google Account</span></div>
        </div>""", unsafe_allow_html=True)
        if st.button("Sign Out", key="signout_profile"):
            logout()

    st.markdown("<br>", unsafe_allow_html=True)

    # Cloud-saved comps
    st.markdown('<div style="font-weight:700;color:#e2e8f0;font-size:1rem;margin-bottom:10px;">☁️ Your Cloud Comps</div>', unsafe_allow_html=True)
    comps = get_user_comps(uid)

    if not comps:
        st.markdown("""
        <div style="background:#0a1628;border:1px dashed #1a2f4a;border-radius:10px;padding:32px;text-align:center;color:#334155;">
            No cloud comps yet. Build and save a comp from the Builder!
        </div>""", unsafe_allow_html=True)
    else:
        from app.services.scoring import get_score_grade, get_score_label
        from app.services.auth_service import current_user
        from app.services.db_service import delete_comp_db

        for comp in comps:
            grade, gc = get_score_grade(comp["score"])
            agent_pills = "".join(
                f'<span style="background:#0a1628;border:1px solid #1a2f4a;border-radius:8px;'
                f'padding:2px 8px;font-size:0.68rem;color:#94a3b8;margin:2px;">'
                f'{a.get("icon","?")} {a["name"]}</span>'
                for a in comp["agents"][:5]
            ) if comp["agents"] else ""

            col_info, col_act = st.columns([4,1])
            with col_info:
                st.markdown(f"""
                <div style="background:#0f1e35;border:1px solid #1a2f4a;border-radius:10px;padding:14px 16px;margin:4px 0;">
                    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
                        <span style="font-weight:700;color:#e2e8f0;">{comp["name"]}</span>
                        <span style="font-size:0.7rem;color:{gc};font-weight:700;">{comp["score"]}/100 {grade}</span>
                    </div>
                    <div style="font-size:0.7rem;color:#475569;margin-bottom:6px;">🗺️ {comp["map_name"]} · {comp["created_at"][:10]}</div>
                    <div>{agent_pills}</div>
                </div>""", unsafe_allow_html=True)
            with col_act:
                if st.button("Load", key=f"load_cloud_{comp['id']}", use_container_width=True):
                    st.session_state["selected_agents"] = [a["name"] for a in comp["agents"]]
                    st.session_state["builder_map"]     = comp["map_name"]
                    st.session_state["builder_step"]    = 2
                    st.session_state["active_page"]     = "Builder"
                    st.rerun()
                if st.button("🗑️", key=f"del_cloud_{comp['id']}", use_container_width=True):
                    delete_comp_db(comp["id"], uid)
                    st.rerun()
