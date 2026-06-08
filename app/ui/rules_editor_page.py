"""
Rules Editor page — view and edit scoring weights.
"""
import streamlit as st
from app.services.data_loader import load_rules, save_rules


def render():
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">⚖️ Rules Editor</h1>
        <p class="page-subtitle">Customize scoring weights and penalties to match your meta preference</p>
    </div>
    """, unsafe_allow_html=True)

    rules = load_rules()
    weights = rules.get("scoring_weights", {})
    penalties = rules.get("penalties", {})

    # ── Scoring Weights ─────────────────────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📊 Scoring Category Weights</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.82rem; color:#64748b; margin-bottom:16px;">
        Adjust the maximum points each scoring category can contribute to the total score (0–100).
    </div>
    """, unsafe_allow_html=True)

    updated_weights = {}
    for category, data in weights.items():
        col1, col2 = st.columns([3, 1])
        label = category.replace("_", " ").title()
        desc = data.get("description", "")
        current = data.get("weight", 10)
        with col1:
            st.markdown(f"""
            <div style="margin-top:8px;">
                <span style="font-weight:600; color:#e2e8f0;">{label}</span>
                <span style="font-size:0.75rem; color:#64748b; margin-left:8px;">{desc}</span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            new_val = st.number_input(
                label=label,
                min_value=0,
                max_value=50,
                value=current,
                step=1,
                key=f"weight_{category}",
                label_visibility="collapsed",
            )
        updated_weights[category] = {**data, "weight": new_val}

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Penalties ───────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">⚠️ Penalties</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.82rem; color:#64748b; margin-bottom:16px;">
        Penalties are subtracted from the total score when critical comp elements are missing.
        Values should be negative.
    </div>
    """, unsafe_allow_html=True)

    updated_penalties = {}
    penalty_labels = {
        "no_controller": "No Controller (no smokes)",
        "no_initiator": "No Initiator (no openers)",
        "no_sentinel": "No Sentinel (no anchor)",
        "too_many_duelists": "3+ Duelists",
        "no_smokes": "No smoke utility",
        "no_recon": "No recon utility",
        "no_flash": "No flash utility",
        "no_entry": "No entry fragger",
        "low_map_fit": "Low map fit (<2 agents on-meta)",
    }

    cols = st.columns(3)
    for idx, (key, label) in enumerate(penalty_labels.items()):
        current_val = penalties.get(key, 0)
        with cols[idx % 3]:
            new_val = st.number_input(
                f"{label}",
                min_value=-50,
                max_value=0,
                value=current_val,
                step=1,
                key=f"penalty_{key}",
            )
            updated_penalties[key] = new_val

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Save / Reset ─────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save Rules", use_container_width=True, type="primary"):
            rules["scoring_weights"] = updated_weights
            rules["penalties"] = updated_penalties
            save_rules(rules)
            st.success("✅ Rules saved successfully!")

    with col2:
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            default_rules = {
                "scoring_weights": {
                    "role_balance": {"weight": 25, "description": "Score based on role distribution", "breakdown": {"has_controller": 8, "has_initiator": 6, "has_sentinel": 6, "duelist_count_optimal": 5}},
                    "map_fit": {"weight": 20, "description": "How well agents match the selected map", "breakdown": {"per_agent_on_good_map": 4, "max_possible": 20}},
                    "synergy": {"weight": 20, "description": "Synergy tag overlap between agents", "breakdown": {"per_shared_tag": 2, "max_possible": 20}},
                    "utility_coverage": {"weight": 15, "description": "Coverage of key utility types", "breakdown": {"has_smokes": 5, "has_recon": 4, "has_flash": 3, "has_post_plant": 3}},
                    "attack_strength": {"weight": 10, "description": "Offensive capability of the comp", "breakdown": {"entry_tag": 5, "aggressive_tag": 3, "flash_for_entry": 2}},
                    "defense_strength": {"weight": 10, "description": "Defensive capability of the comp", "breakdown": {"anchor_tag": 4, "defensive_tag": 3, "flank_control_tag": 3}},
                },
                "penalties": {
                    "no_controller": -15, "no_initiator": -10, "no_sentinel": -10,
                    "too_many_duelists": -8, "no_smokes": -12, "no_recon": -8,
                    "no_flash": -5, "no_entry": -6, "low_map_fit": -5,
                },
            }
            rules.update(default_rules)
            save_rules(rules)
            st.success("✅ Rules reset to defaults!")
            st.rerun()

    # ── Scoring Info ─────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📖 Scoring System Explained</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.85rem; color:#94a3b8; line-height:1.8;">
        <p>The scoring engine evaluates your team composition across 6 categories:</p>
        <ul style="margin-left:16px;">
            <li><strong style="color:#e2e8f0;">Role Balance</strong> — Rewards having Controller, Initiator, Sentinel, and 1-2 Duelists.</li>
            <li><strong style="color:#e2e8f0;">Map Fit</strong> — Agents on their <code>good_maps</code> list score higher for the selected map.</li>
            <li><strong style="color:#e2e8f0;">Agent Synergy</strong> — Agents sharing synergy tags (e.g. "aggressive", "entry") score bonus points.</li>
            <li><strong style="color:#e2e8f0;">Utility Coverage</strong> — Checks for smokes, recon, flash, and post-plant utility.</li>
            <li><strong style="color:#e2e8f0;">Attack Strength</strong> — Rewards entry fraggers and aggressive utility.</li>
            <li><strong style="color:#e2e8f0;">Defense Strength</strong> — Rewards anchor agents and flank control.</li>
        </ul>
        <p style="margin-top:12px;">Penalties are subtracted for missing critical elements. Final score is clamped to <strong style="color:#e2e8f0;">0–100</strong>.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
