"""
Meta Tracker V3 — simple tier list per map.

Each agent appears in exactly one tier (S/A/B/C) based on the composite
score from meta_service V3 (win rate + pick rate + map profile).
Cards show just Win Rate % and Pick Rate % — no volatile "Meta/Off" labels.
"""
import streamlit as st
from app.services.meta_service import (
    is_meta_loaded, get_all_maps, get_tier_groups, load_meta_data
)

TIER_STYLE = {
    "S": {"color": "#ff4655", "label": "S TIER", "desc": "Pro-meta essential"},
    "A": {"color": "#ff8c42", "label": "A TIER", "desc": "Strong meta pick"},
    "B": {"color": "#ffd700", "label": "B TIER", "desc": "Viable choice"},
    "C": {"color": "#64748b", "label": "C TIER", "desc": "Niche pick"},
}

AGENTS_PER_ROW = 5


def _wr_color(wr: float) -> str:
    if wr >= 52: return "#10b981"
    if wr >= 48: return "#ffd700"
    return "#ff6b6b"


def _pr_color(pr: float) -> str:
    if pr >= 50: return "#10b981"
    if pr >= 25: return "#ff8c42"
    return "#64748b"


def render():
    st.markdown("## 📊 Meta Tracker")

    if not is_meta_loaded():
        st.warning("Meta data not found — make sure `data/vct_meta.json` exists.")
        return

    meta = load_meta_data()
    updated = meta.get("last_updated", "")
    series = meta.get("series", "")
    if updated or series:
        st.caption(f"{series} · Last updated: {updated}")

    maps = get_all_maps()
    selected_map = st.selectbox("Select map", maps, key="meta_tracker_map")

    st.markdown(
        "<p style='color:#94a3b8;font-size:0.85rem;'>"
        "Tiers blend <b>win rate</b>, <b>pick rate</b>, and each agent's "
        "<b>map profile</b> — a stable measure of meta strength."
        "</p>", unsafe_allow_html=True)

    groups = get_tier_groups(selected_map)

    for tier in ["S", "A", "B", "C"]:
        agents = groups.get(tier, [])
        if not agents:
            continue
        style = TIER_STYLE[tier]

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin:22px 0 10px 0;">
            <div style="background:{style['color']};color:#0b0f1a;font-weight:800;
                        font-size:1.1rem;padding:4px 16px;border-radius:6px;">
                {style['label']}
            </div>
            <span style="color:#64748b;font-size:0.8rem;">{style['desc']} · {len(agents)} agents</span>
        </div>
        """, unsafe_allow_html=True)

        for row_start in range(0, len(agents), AGENTS_PER_ROW):
            row = agents[row_start:row_start + AGENTS_PER_ROW]
            cols = st.columns(AGENTS_PER_ROW)
            for col, (name, stats) in zip(cols, row):
                wr = stats.get("win_rate", 0)
                pr = stats.get("pick_rate", 0)
                with col:
                    st.markdown(f"""
                    <div style="border:1px solid {style['color']}33;border-left:3px solid {style['color']};
                                border-radius:8px;padding:10px 12px;margin-bottom:8px;
                                background:rgba(255,255,255,0.02);">
                        <div style="font-weight:700;font-size:0.95rem;margin-bottom:6px;">{name}</div>
                        <div style="font-size:0.78rem;color:#94a3b8;">
                            WR <span style="color:{_wr_color(wr)};font-weight:700;">{wr}%</span>
                            &nbsp;·&nbsp;
                            PR <span style="color:{_pr_color(pr)};font-weight:700;">{pr}%</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
