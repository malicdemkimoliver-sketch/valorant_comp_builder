"""
Saved Comps page — view, load, and delete saved compositions.
"""
import streamlit as st
from app.services.data_loader import load_saved_comps, delete_comp, load_agents
from app.services.scoring import get_score_grade, get_score_label

ROLE_COLORS = {
    "Duelist": "#ff4d6d",
    "Controller": "#7c3aed",
    "Initiator": "#0ea5e9",
    "Sentinel": "#10b981",
}

ROLE_ICONS = {
    "Duelist": "⚔️",
    "Controller": "💨",
    "Initiator": "🔍",
    "Sentinel": "🛡️",
}


def render():
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">💾 Saved Comps</h1>
        <p class="page-subtitle">Load, review, and manage your saved team compositions</p>
    </div>
    """, unsafe_allow_html=True)

    comps = load_saved_comps()
    all_agents = load_agents()

    if not comps:
        st.markdown("""
        <div class="card" style="text-align:center; padding:60px;">
            <div style="font-size:3rem;">📭</div>
            <div style="font-size:1.2rem; color:#64748b; margin-top:16px;">No saved compositions yet.</div>
            <div style="font-size:0.9rem; color:#475569; margin-top:8px;">
                Go to the Builder page and save a comp to see it here.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Summary row
    st.markdown(f"""
    <div class="card" style="padding:12px 20px; margin-bottom:16px;">
        <span style="color:#94a3b8; font-size:0.9rem;">
            📦 <strong style="color:#e2e8f0;">{len(comps)}</strong> saved compositions
        </span>
    </div>
    """, unsafe_allow_html=True)

    for i, comp in enumerate(comps):
        name = comp.get("name", f"Comp #{i+1}")
        map_name = comp.get("map_name", "Unknown")
        score = comp.get("score", 0)
        notes = comp.get("notes", "")
        saved_at = comp.get("saved_at", "")
        grade, grade_color = get_score_grade(score)
        label = get_score_label(score)

        agents_data = comp.get("agents", [])
        agent_names = [a["name"] for a in agents_data]
        agent_roles = [(a["name"], a["role"]) for a in agents_data]

        # Agent pills
        pills_html = ""
        for aname, arole in agent_roles:
            color = ROLE_COLORS.get(arole, "#64748b")
            icon = ROLE_ICONS.get(arole, "")
            # Find icon from full agent data
            a_obj = next((x for x in all_agents if x.name == aname), None)
            agent_icon = a_obj.icon if a_obj else "🎮"
            pills_html += f'<span class="agent-pill" style="border-color:{color}; color:{color};">{agent_icon} {aname}</span>'

        st.markdown(f"""
        <div class="saved-comp-card">
            <div class="saved-comp-header">
                <div>
                    <div class="saved-comp-name">{name}</div>
                    <div style="font-size:0.8rem; color:#64748b;">
                        🗺️ {map_name} &nbsp;·&nbsp; 🕒 {saved_at}
                    </div>
                </div>
                <div class="saved-score-badge" style="border-color:{grade_color}; color:{grade_color};">
                    <span style="font-size:1.4rem; font-weight:800;">{score}</span>
                    <span style="font-size:0.7rem;">{grade}</span>
                </div>
            </div>
            <div class="agent-pills-row">{pills_html}</div>
            {f'<div class="saved-notes">📝 {notes}</div>' if notes else ""}
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            if st.button(f"📂 Load to Builder", key=f"load_{i}", use_container_width=True):
                st.session_state["builder_agents"] = agent_names
                st.session_state["builder_map"] = map_name
                st.session_state["active_page"] = "Builder"
                st.success(f"✅ Loaded '{name}' — go to Builder page!")
                st.rerun()

        with col2:
            st.markdown(f"""
            <div style="padding:6px; text-align:center; font-size:0.8rem; color:#94a3b8;">
                Score: <strong style="color:{grade_color};">{score}/100</strong> — {label}
            </div>
            """, unsafe_allow_html=True)

        with col3:
            if st.button(f"🗑️ Delete", key=f"del_{i}", use_container_width=True):
                delete_comp(i)
                st.warning(f"Deleted '{name}'")
                st.rerun()

        st.markdown('<hr style="border-color:#1e293b; margin:8px 0;">', unsafe_allow_html=True)
