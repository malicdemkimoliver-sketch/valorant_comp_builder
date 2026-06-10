"""
GYDRENZIN Valorant Comp Builder v2.0
Professional comp building + analytics platform
"""
import streamlit as st
from datetime import datetime

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GYDRENZIN Comp Builder",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Exo+2:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg-primary: #020817;
    --bg-secondary: #0a1628;
    --bg-card: #0f1e35;
    --bg-card-hover: #132240;
    --border: #1a2f4a;
    --border-hover: #2a4a70;
    --text-primary: #e2e8f0;
    --text-secondary: #94a3b8;
    --accent-cyan: #00d4ff;
    --accent-purple: #7c3aed;
    --accent-green: #10b981;
    --accent-red: #ff4d6d;
    --accent-gold: #fbbf24;
}

.stApp {
    background: var(--bg-primary) !important;
    font-family: 'Exo 2', sans-serif !important;
}

.main .block-container {
    padding: 2rem;
    max-width: 1400px !important;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--bg-secondary), var(--bg-primary)) !important;
    border-right: 1px solid var(--border) !important;
}

/* Navigation Buttons */
.nav-button {
    width: 100%;
    padding: 12px 16px;
    margin: 6px 0;
    border-radius: 8px;
    border: 1px solid var(--border);
    background: var(--bg-card);
    color: var(--text-secondary);
    cursor: pointer;
    font-size: 0.95rem;
    font-weight: 500;
    transition: all 0.3s ease;
    text-align: left;
    font-family: 'Exo 2', sans-serif;
}

.nav-button:hover {
    background: var(--bg-card-hover);
    color: var(--text-primary);
    border-color: var(--border-hover);
    transform: translateX(4px);
}

.nav-button.active {
    background: var(--accent-cyan);
    color: #000;
    border-color: var(--accent-cyan);
    font-weight: 600;
    box-shadow: 0 0 20px rgba(0,212,255,0.2);
}

.brand-header {
    text-align: center;
    padding: 20px 0;
    margin-bottom: 20px;
    border-bottom: 1px solid var(--border);
}

.brand-logo {
    font-size: 2.5rem;
    margin-bottom: 8px;
}

.brand-text {
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--accent-cyan);
    font-family: 'Rajdhani', monospace;
    letter-spacing: 2px;
}

.brand-subtitle {
    font-size: 0.75rem;
    color: var(--text-secondary);
    margin-top: 4px;
}

.page-title {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}

.page-subtitle {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-bottom: 2rem;
}

.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin: 16px 0;
    transition: all 0.3s ease;
}

.card:hover {
    border-color: var(--border-hover);
    background: var(--bg-card-hover);
}

/* Responsive */
@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem;
    }
    
    .page-title {
        font-size: 1.5rem;
    }
}
</style>
""", unsafe_allow_html=True)

# ── Import pages ────────────────────────────────────────────────────────────
try:
    from app.ui.builder_page import render as render_builder
    from app.ui.saved_comps_page import render as render_saved
    from app.ui.meta_tracker_page import render as render_meta
    from app.ui.agents_used_page import render as render_agents_used
    from app.ui.login_page_google_oauth import render as render_login
    from app.ui.account_page import render as render_account
except ImportError as e:
    st.error(f"Error importing pages: {e}")
    st.info("Make sure all page files exist in app/ui/")

# ── Initialize Session State ────────────────────────────────────────────────
if "current_page" not in st.session_state:
    st.session_state.current_page = "builder"

if "user_logged_in" not in st.session_state:
    st.session_state.user_logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = None

# ── Sidebar Navigation ──────────────────────────────────────────────────────
with st.sidebar:
    # Brand Header
    st.markdown("""
    <div class="brand-header">
        <div class="brand-logo">⚔️</div>
        <div class="brand-text">GYDRENZIN</div>
        <div class="brand-subtitle">Comp Builder v2.0</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Main Navigation
    st.markdown("<div style='margin: 20px 0;'><p style='font-size:0.85rem; color:#475569; font-weight:600; text-transform:uppercase; letter-spacing:1px;'>FEATURES</p></div>", unsafe_allow_html=True)
    
    # Build Composition Button
    if st.button(
        "🎯 Build Composition",
        key="nav_builder",
        use_container_width=True,
        help="Build and analyze team compositions"
    ):
        st.session_state.current_page = "builder"
        st.rerun()
    
    # Meta Tracker Button
    if st.button(
        "📊 Meta Tracker",
        key="nav_meta",
        use_container_width=True,
        help="VCT statistics and meta analysis"
    ):
        st.session_state.current_page = "meta"
        st.rerun()
    
    # Your Agent Stats Button
    if st.button(
        "📈 Your Agent Stats",
        key="nav_agents_used",
        use_container_width=True,
        help="Your personal agent statistics from tracker.gg"
    ):
        st.session_state.current_page = "agents_used"
        st.rerun()
    
    st.markdown("---")
    
    # Account Section
    st.markdown("<div style='margin: 20px 0;'><p style='font-size:0.85rem; color:#475569; font-weight:600; text-transform:uppercase; letter-spacing:1px;'>ACCOUNT</p></div>", unsafe_allow_html=True)
    
    if st.session_state.user_logged_in:
        # Saved Comps Button (MOVED TO ACCOUNT)
        if st.button(
            "💾 Saved Comps",
            key="nav_saved",
            use_container_width=True,
            help="View and load your saved compositions"
        ):
            st.session_state.current_page = "saved"
            st.rerun()
        
        # Show account settings for logged-in users
        st.markdown(f"""
        <div class="card" style="padding:12px;">
            <p style='margin:0; font-size:0.85rem; color:var(--text-secondary);'>Logged in as:</p>
            <p style='margin:4px 0 0 0; font-size:0.9rem; color:var(--accent-cyan); font-weight:600;'>{st.session_state.user_email}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("👤 Account Settings", key="nav_account", use_container_width=True):
            st.session_state.current_page = "account"
            st.rerun()
        
        if st.button("🚪 Logout", key="btn_logout", use_container_width=True):
            st.session_state.user_logged_in = False
            st.session_state.user_email = None
            st.session_state.current_page = "builder"
            st.success("Logged out successfully!")
            st.rerun()
    else:
        # Show login button for non-logged-in users
        if st.button("🔐 Login with Google", key="btn_login", use_container_width=True):
            st.session_state.current_page = "account"
            st.rerun()
    
    st.markdown("---")
    
    # Quick Tips
    st.markdown("""
    <div class="card" style="padding:12px; margin-top:20px;">
        <p style='font-size:0.8rem; color:var(--text-secondary); margin:0; line-height:1.6;'>
        💡 <strong style='color:var(--text-primary);'>Quick Tips:</strong><br>
        • Start with map selection<br>
        • Check meta pick rates<br>
        • Share codes via Discord<br>
        • Save your best comps
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='position:relative; margin-top:30px; padding-top:20px; border-top:1px solid var(--border); text-align:center; font-size:0.7rem; color:var(--text-secondary);'>
        Made with 🎮 by GYDRENZIN
    </div>
    """, unsafe_allow_html=True)

# ── Main Content Area ──────────────────────────────────────────────────────
# Check if user is logged in - redirect to login if not
if not st.session_state.get("user_logged_in", False):
    render_login()
elif st.session_state.current_page == "builder":
    render_builder()
elif st.session_state.current_page == "saved":
    render_saved()
elif st.session_state.current_page == "meta":
    render_meta()
elif st.session_state.current_page == "agents_used":
    render_agents_used()
elif st.session_state.current_page == "account":
    render_account()
else:
    render_builder()
