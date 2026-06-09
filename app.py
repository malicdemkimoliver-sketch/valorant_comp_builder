"""
Gyd's Comp Helper — Main Streamlit App
A premium Valorant team composition builder and analyzer.
"""
import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Gyd's Comp Helper",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Import UI pages ───────────────────────────────────────────────────────────
from app.ui.orbital_hub import render as render_hub
from app.ui.login_page import render as render_account, render_login_banner
from app.services.auth_service import handle_oauth_callback, is_logged_in, current_user
from app.services.db_service import save_comp_db
from app.ui.builder_page import render as render_builder
from app.ui.agent_database_page import render as render_database
from app.ui.saved_comps_page import render as render_saved
from app.ui.rules_editor_page import render as render_rules

# ── Handle Google OAuth callback ────────────────────────────────────────────
handle_oauth_callback()

# ── Global CSS — Premium Dark Gaming Dashboard ────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ─────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Exo+2:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root Variables ───────────────────────────────────────────────────────── */
:root {
    --bg-primary: #020817;
    --bg-secondary: #0a1628;
    --bg-card: #0f1e35;
    --bg-card-hover: #132240;
    --bg-input: #0d1b2e;
    --border: #1a2f4a;
    --border-hover: #2a4a70;
    --text-primary: #e2e8f0;
    --text-secondary: #94a3b8;
    --text-muted: #475569;
    --accent-cyan: #00d4ff;
    --accent-purple: #7c3aed;
    --accent-green: #10b981;
    --accent-red: #ff4d6d;
    --accent-gold: #fbbf24;
    --glow-cyan: 0 0 20px rgba(0,212,255,0.2);
    --glow-purple: 0 0 20px rgba(124,58,237,0.2);
    --glow-green: 0 0 20px rgba(16,185,129,0.2);
    --shadow-card: 0 4px 24px rgba(0,0,0,0.4);
    --radius: 12px;
    --radius-sm: 8px;
}

/* ── Base Layout ──────────────────────────────────────────────────────────── */
.stApp {
    background: var(--bg-primary) !important;
    font-family: 'Exo 2', sans-serif !important;
}

/* Remove default Streamlit padding */
.main .block-container {
    padding: 1.5rem 2rem !important;
    max-width: 1400px !important;
}

/* ── Sidebar ──────────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
    min-width: 240px !important;
}

section[data-testid="stSidebar"] .stMarkdown {
    color: var(--text-primary) !important;
}

/* ── Logo / Brand ─────────────────────────────────────────────────────────── */
.brand-header {
    text-align: center;
    padding: 24px 16px 20px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 16px;
}

.brand-logo-text {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 2px;
    line-height: 1;
}

.brand-subtitle {
    font-size: 0.7rem;
    color: var(--text-muted);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 4px;
}

.brand-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent-cyan), var(--accent-purple), transparent);
    margin: 12px 0;
    border-radius: 2px;
}

/* ── Nav Buttons ──────────────────────────────────────────────────────────── */
.nav-btn {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 12px 16px;
    margin: 3px 0;
    background: transparent;
    border: 1px solid transparent;
    border-radius: var(--radius-sm);
    color: var(--text-secondary);
    font-family: 'Exo 2', sans-serif;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
}

.nav-btn:hover {
    background: rgba(0,212,255,0.06);
    border-color: var(--border-hover);
    color: var(--text-primary);
}

.nav-btn.active {
    background: rgba(0,212,255,0.1);
    border-color: var(--accent-cyan);
    color: var(--accent-cyan);
    box-shadow: var(--glow-cyan);
}

/* ── Streamlit radio styling for nav ─────────────────────────────────────── */
[data-testid="stSidebar"] .stRadio > div {
    gap: 4px !important;
}

[data-testid="stSidebar"] .stRadio label {
    background: transparent;
    border: 1px solid transparent;
    border-radius: var(--radius-sm);
    padding: 12px 16px !important;
    color: var(--text-secondary) !important;
    font-family: 'Exo 2', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    cursor: pointer;
    transition: all 0.2s ease;
    width: 100% !important;
    display: flex;
    align-items: center;
}

[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(0,212,255,0.06);
    border-color: var(--border-hover);
    color: var(--text-primary) !important;
}

[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] {
    display: none !important;
}

/* ── Page Header ──────────────────────────────────────────────────────────── */
.page-header {
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border);
}

.page-title {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    margin: 0 !important;
    letter-spacing: 1px;
}

.page-subtitle {
    font-size: 0.875rem;
    color: var(--text-muted);
    margin-top: 4px;
}

/* ── Cards ────────────────────────────────────────────────────────────────── */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: var(--shadow-card);
    transition: border-color 0.2s ease;
}

.card:hover {
    border-color: var(--border-hover);
}

.card-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 14px;
    letter-spacing: 0.5px;
}

/* ── Stat Cards ───────────────────────────────────────────────────────────── */
.stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px;
    text-align: center;
    transition: all 0.2s ease;
}

.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
}

.stat-icon { font-size: 1.6rem; }
.stat-value { font-size: 1.8rem; font-weight: 700; margin-top: 4px; }
.stat-label { font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; }

/* ── Agent Cards ──────────────────────────────────────────────────────────── */
.agent-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 12px;
    text-align: center;
    transition: all 0.25s ease;
    cursor: default;
    height: 140px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.agent-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(0,0,0,0.4);
    border-color: var(--border-hover);
}

.agent-icon { font-size: 2.2rem; }
.agent-name { font-family: 'Rajdhani', sans-serif; font-size: 1rem; font-weight: 700; color: var(--text-primary); margin-top: 4px; }
.agent-role { font-size: 0.72rem; font-weight: 600; margin-top: 2px; }
.agent-map-fit { font-size: 0.7rem; color: var(--text-muted); margin-top: 4px; }

/* ── Score Display ────────────────────────────────────────────────────────── */
.score-card { text-align: center; }

.score-circle {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    border: 4px solid;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin: 16px auto;
    box-shadow: 0 0 30px rgba(0,212,255,0.15);
}

.score-number {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    line-height: 1;
}

.score-grade {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
}

.score-label {
    font-size: 0.85rem;
    color: var(--text-secondary);
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* ── Score Bars ───────────────────────────────────────────────────────────── */
.score-bar-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
}

.score-bar-label {
    font-size: 0.78rem;
    color: var(--text-secondary);
    width: 130px;
    flex-shrink: 0;
}

.score-bar-track {
    flex: 1;
    height: 6px;
    background: var(--border);
    border-radius: 3px;
    overflow: hidden;
}

.score-bar-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.5s ease;
}

.score-bar-val {
    font-size: 0.72rem;
    color: var(--text-muted);
    width: 35px;
    text-align: right;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Strength / Weakness / Warning Items ──────────────────────────────────── */
.strength-item {
    font-size: 0.82rem;
    color: #10b981;
    padding: 5px 0;
    border-bottom: 1px solid rgba(16,185,129,0.1);
}

.weakness-item {
    font-size: 0.82rem;
    color: #ff4d6d;
    padding: 5px 0;
    border-bottom: 1px solid rgba(255,77,109,0.1);
}

.warning-item {
    font-size: 0.82rem;
    color: #fbbf24;
    padding: 5px 0;
    border-bottom: 1px solid rgba(251,191,36,0.1);
    line-height: 1.4;
}

/* ── Recommendation Cards ─────────────────────────────────────────────────── */
.rec-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 14px;
    margin-bottom: 8px;
    transition: all 0.2s ease;
}

.rec-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
}

/* ── Tags ─────────────────────────────────────────────────────────────────── */
.tag {
    display: inline-block;
    font-size: 0.65rem;
    padding: 2px 7px;
    border-radius: 20px;
    background: rgba(0,212,255,0.08);
    border: 1px solid rgba(0,212,255,0.2);
    color: var(--accent-cyan);
    margin: 2px;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Badges ───────────────────────────────────────────────────────────────── */
.badge {
    display: inline-block;
    font-size: 0.65rem;
    padding: 3px 8px;
    border-radius: 20px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.badge-info {
    background: rgba(0,212,255,0.12);
    border: 1px solid rgba(0,212,255,0.3);
    color: var(--accent-cyan);
}

.badge-danger {
    background: rgba(255,77,109,0.12);
    border: 1px solid rgba(255,77,109,0.3);
    color: var(--accent-red);
}

.badge-success {
    background: rgba(16,185,129,0.12);
    border: 1px solid rgba(16,185,129,0.3);
    color: var(--accent-green);
}

/* ── Agent Database Cards ─────────────────────────────────────────────────── */
.db-agent-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px;
    margin-bottom: 12px;
    transition: all 0.25s ease;
    min-height: 280px;
}

.db-agent-card:hover {
    border-color: var(--border-hover);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
}

.db-agent-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
}

.db-agent-icon { font-size: 1.8rem; }
.db-agent-name { font-family: 'Rajdhani', sans-serif; font-size: 1rem; font-weight: 700; color: var(--text-primary); }
.db-agent-role { font-size: 0.72rem; font-weight: 600; }

.db-section-title {
    font-size: 0.68rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 8px 0 4px;
}

.db-list {
    font-size: 0.75rem;
    color: var(--text-secondary);
    margin: 0 0 4px 14px;
    padding: 0;
    line-height: 1.6;
}

.db-list li { margin-bottom: 2px; }
.strength-list { color: #10b981 !important; }
.weakness-list { color: #ff6b6b !important; }

/* ── Saved Comp Cards ─────────────────────────────────────────────────────── */
.saved-comp-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
    margin-bottom: 8px;
    transition: all 0.2s ease;
}

.saved-comp-card:hover {
    border-color: var(--border-hover);
}

.saved-comp-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 12px;
}

.saved-comp-name {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--text-primary);
}

.saved-score-badge {
    display: flex;
    flex-direction: column;
    align-items: center;
    border: 2px solid;
    border-radius: 8px;
    padding: 6px 12px;
    min-width: 60px;
}

.agent-pills-row {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 8px;
}

.agent-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.75rem;
    padding: 3px 10px;
    border-radius: 20px;
    border: 1px solid;
    font-weight: 600;
    background: rgba(0,0,0,0.2);
}

.saved-notes {
    margin-top: 10px;
    font-size: 0.8rem;
    color: var(--text-muted);
    font-style: italic;
    padding-top: 8px;
    border-top: 1px solid var(--border);
}

/* ── Streamlit native element overrides ───────────────────────────────────── */
/* Buttons */
.stButton > button {
    background: rgba(0,212,255,0.08) !important;
    border: 1px solid rgba(0,212,255,0.3) !important;
    color: var(--accent-cyan) !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Exo 2', sans-serif !important;
    font-size: 0.875rem !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.3px;
}

.stButton > button:hover {
    background: rgba(0,212,255,0.16) !important;
    border-color: var(--accent-cyan) !important;
    box-shadow: 0 0 16px rgba(0,212,255,0.2) !important;
    transform: translateY(-1px);
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent-purple), var(--accent-cyan)) !important;
    border: none !important;
    color: white !important;
}

.stButton > button[kind="primary"]:hover {
    box-shadow: 0 0 24px rgba(124,58,237,0.4) !important;
    transform: translateY(-1px);
}

/* Selectbox */
.stSelectbox > div > div {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: 'Exo 2', sans-serif !important;
}

.stSelectbox > div > div:hover {
    border-color: var(--border-hover) !important;
}

/* Text inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: 'Exo 2', sans-serif !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent-cyan) !important;
    box-shadow: 0 0 0 2px rgba(0,212,255,0.15) !important;
}

/* Multiselect */
.stMultiSelect > div > div {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
}

/* Number input */
.stNumberInput > div > div > input {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* Labels */
.stSelectbox label, .stMultiSelect label, .stTextInput label,
.stTextArea label, .stNumberInput label, .stRadio label {
    color: var(--text-secondary) !important;
    font-family: 'Exo 2', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}

/* Download button */
.stDownloadButton > button {
    background: rgba(16,185,129,0.08) !important;
    border: 1px solid rgba(16,185,129,0.3) !important;
    color: var(--accent-green) !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Exo 2', sans-serif !important;
    font-weight: 600 !important;
}

.stDownloadButton > button:hover {
    background: rgba(16,185,129,0.16) !important;
    box-shadow: 0 0 16px rgba(16,185,129,0.2) !important;
}

/* Success/Warning/Error messages */
.stSuccess {
    background: rgba(16,185,129,0.1) !important;
    border: 1px solid rgba(16,185,129,0.3) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--accent-green) !important;
}

.stWarning {
    background: rgba(251,191,36,0.1) !important;
    border: 1px solid rgba(251,191,36,0.3) !important;
    border-radius: var(--radius-sm) !important;
}

.stError {
    background: rgba(255,77,109,0.1) !important;
    border: 1px solid rgba(255,77,109,0.3) !important;
    border-radius: var(--radius-sm) !important;
}

/* Dividers */
hr {
    border-color: var(--border) !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--border-hover); }

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden !important; }

/* Columns gap */
[data-testid="column"] { padding: 0 8px !important; }

/* ── Team slots row ───────────────────────────────────────────────────────── */
.team-slots-row {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}

.team-slot {
    flex: 1;
    min-width: 100px;
    max-width: 160px;
    border-radius: 10px;
    padding: 12px 8px;
    text-align: center;
    transition: all 0.2s ease;
}

.team-slot.filled {
    background: rgba(0,0,0,0.25);
    border: 2px solid;
}

.team-slot.empty {
    background: rgba(255,255,255,0.02);
    border: 1px dashed #1e3a5f;
}

.team-slot-icon { font-size: 1.8rem; }
.team-slot-name { font-family: 'Rajdhani', sans-serif; font-size: 0.9rem; font-weight: 700; color: #e2e8f0; margin-top: 4px; }
.team-slot-role { font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px; }
.team-slot-fit  { font-size: 0.7rem; margin-top: 4px; }

/* ── Role picker header ────────────────────────────────────────────────────── */
.role-picker-header {
    padding: 8px 14px;
    margin: 12px 0 8px;
    border-radius: 0 6px 6px 0;
    background: rgba(0,0,0,0.2);
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    color: #94a3b8;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* ── Agent pick buttons — override Streamlit defaults ─────────────────────── */
/* Selected state handled by Streamlit button label prefix */
.stButton > button[data-testid*="pick_"] {
    font-family: 'Exo 2', sans-serif !important;
    font-size: 0.78rem !important;
    padding: 8px 4px !important;
    border-radius: 8px !important;
}

/* ── Remove slot buttons ──────────────────────────────────────────────────── */
[data-testid*="remove_slot_"] > button,
div[data-testid="stButton"]:has(button[kind="secondary"]) button {
    padding: 4px 8px !important;
    font-size: 0.68rem !important;
}

/* Target remove buttons by their label via attribute — fallback: style all small ✕ buttons */
.stButton > button:has-text("✕ Remove") {
    background: rgba(255,77,109,0.08) !important;
    border: 1px solid rgba(255,77,109,0.3) !important;
    color: #ff4d6d !important;
    font-size: 0.68rem !important;
    padding: 4px 0 !important;
    border-radius: 6px !important;
}

.stButton > button:has-text("✕ Remove"):hover {
    background: rgba(255,77,109,0.18) !important;
    box-shadow: 0 0 10px rgba(255,77,109,0.2) !important;
}

/* ── Step indicator bar ───────────────────────────────────────────────────── */
.steps-bar {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0;
    padding: 12px 0 4px;
}

.step {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 18px;
    border-radius: 30px;
    font-family: 'Exo 2', sans-serif;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text-muted);
    background: transparent;
    border: 1px solid var(--border);
    transition: all 0.25s ease;
}

.step.active {
    background: linear-gradient(135deg, rgba(0,212,255,0.12), rgba(124,58,237,0.12));
    border-color: var(--accent-cyan);
    color: var(--accent-cyan);
    box-shadow: 0 0 16px rgba(0,212,255,0.15);
}

.step.done {
    background: rgba(16,185,129,0.08);
    border-color: rgba(16,185,129,0.4);
    color: var(--accent-green);
}

.step-num {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.72rem;
    font-weight: 800;
    background: rgba(255,255,255,0.06);
    flex-shrink: 0;
}

.step.active .step-num { background: var(--accent-cyan); color: #000; }
.step.done  .step-num { background: var(--accent-green); color: #000; }

.step-label { white-space: nowrap; }

.step-line {
    width: 40px;
    height: 2px;
    background: var(--border);
    flex-shrink: 0;
}
.step-line.done { background: var(--accent-green); }

/* ── Map selection cards ──────────────────────────────────────────────────── */
.map-card {
    background: var(--bg-card);
    border-radius: var(--radius);
    padding: 0;
    margin-bottom: 8px;
    overflow: hidden;
    transition: all 0.25s ease;
    cursor: pointer;
}

.map-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 32px rgba(0,0,0,0.5);
}

.map-splash {
    width: 100%;
    height: 100px;
    object-fit: cover;
    display: block;
    opacity: 0.75;
}

.map-icon {
    font-size: 1.4rem;
    text-align: center;
    margin: 10px 0 2px;
}

.map-name {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-primary);
    text-align: center;
}

.map-bias {
    font-size: 0.65rem;
    text-align: center;
    color: var(--accent-cyan);
    margin: 2px 0 4px;
    font-weight: 600;
}

.map-desc {
    font-size: 0.68rem;
    color: var(--text-muted);
    text-align: center;
    padding: 0 8px 10px;
    line-height: 1.4;
}

/* ── Agent avatar cards (picker grid) ────────────────────────────────────── */
.agent-avatar-card {
    border-radius: 10px;
    padding: 8px 4px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
    margin-bottom: 4px;
}

.agent-avatar-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.4);
}

.av-img {
    width: 64px;
    height: 64px;
    object-fit: cover;
    border-radius: 50%;
    display: block;
    margin: 6px auto 4px;
    border: 2px solid rgba(255,255,255,0.1);
}

.av-name {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 0.78rem;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-top: 2px;
}

.av-role {
    font-size: 0.6rem;
    font-weight: 600;
    margin-top: 1px;
}

.av-check {
    position: absolute;
    top: 4px;
    right: 4px;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    font-size: 0.55rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    color: #000;
}

.av-fitdot {
    position: absolute;
    top: 4px;
    left: 4px;
    width: 8px;
    height: 8px;
    border-radius: 50%;
}

.av-stat {
    font-size: 0.62rem;
    margin-top: 2px;
}

/* ── Tier badge ───────────────────────────────────────────────────────────── */
.tier-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 6px;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    font-weight: 800;
    flex-shrink: 0;
}

/* ── Sidebar footer ───────────────────────────────────────────────────────── */
.sidebar-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 240px;
    padding: 12px 16px;
    border-top: 1px solid var(--border);
    background: var(--bg-secondary);
    font-size: 0.7rem;
    color: var(--text-muted);
    text-align: center;
}

/* ── Small ✕ remove buttons ─────────────────────────────────────────────── */
.stButton > button[kind="secondary"] {
    font-size: 0.7rem !important;
    padding: 3px 6px !important;
    background: rgba(255,77,109,0.07) !important;
    border: 1px solid rgba(255,77,109,0.25) !important;
    color: #ff4d6d !important;
}

.stButton > button[kind="secondary"]:hover {
    background: rgba(255,77,109,0.15) !important;
}
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand header
    st.markdown("""
    <div class="brand-header">
        <div style="font-size: 2.5rem; margin-bottom: 4px;">🎯</div>
        <div class="brand-logo-text">GYDRENZIN</div>
        <div class="brand-divider"></div>
        <div class="brand-subtitle">Comp Helper v1.0</div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    st.markdown('<div style="padding: 0 8px;">', unsafe_allow_html=True)

    pages = {
        "🌐  Orbital Hub":    "Orbital Hub",
        "⚙️  Builder":        "Builder",
        "📚  Agent Database": "Agent Database",
        "💾  Saved Comps":    "Saved Comps",
        "⚖️  Rules Editor":   "Rules Editor",
        "👤  Account":        "Account",
    }

    if "active_page" not in st.session_state:
        st.session_state["active_page"] = "Orbital Hub"

    page_keys = list(pages.keys())
    default_idx = list(pages.values()).index(st.session_state.get("active_page", "Builder"))

    selected_label = st.radio(
        "Navigation",
        options=page_keys,
        index=default_idx,
        key="nav_radio",
        label_visibility="collapsed",
    )
    selected_page = pages[selected_label]
    st.session_state["active_page"] = selected_page

    st.markdown('</div>', unsafe_allow_html=True)

    # Quick tips
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="card" style="padding:14px;">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.72rem; color:#475569; line-height:1.7;">
        💡 <strong style="color:#64748b;">Tips</strong><br>
        • Build on your selected map<br>
        • Always include smokes + recon<br>
        • Score 70+ = tournament ready<br>
        • Save your best comps!
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Login status in sidebar
    st.markdown("<br>", unsafe_allow_html=True)
    render_login_banner()

    st.markdown("""
    <div style="position:absolute; bottom:12px; left:0; right:0; text-align:center; font-size:0.65rem; color:#1e3a5f;">
        Made with 🎮 by GYDRENZIN
    </div>
    """, unsafe_allow_html=True)


# ── Main content ──────────────────────────────────────────────────────────────
if selected_page == "Orbital Hub":
    render_hub()
elif selected_page == "Account":
    render_account()
elif selected_page == "Builder":
    render_builder()
elif selected_page == "Agent Database":
    render_database()
elif selected_page == "Saved Comps":
    render_saved()
elif selected_page == "Rules Editor":
    render_rules()
