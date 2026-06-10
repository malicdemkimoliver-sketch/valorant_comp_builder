"""
Agent Database page — two tabs: Browse agents | Map Tier list.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
import streamlit as st
import streamlit.components.v1 as components
from assets.agent_portraits import AGENT_PORTRAITS
from app.services.data_loader import load_agents, load_maps

RC = {"Duelist":"#ff4d6d","Controller":"#7c3aed","Initiator":"#0ea5e9","Sentinel":"#10b981"}
RI = {"Duelist":"⚔️","Controller":"💨","Initiator":"🔍","Sentinel":"🛡️"}
TIER_STYLES = {
    "A": {"color":"#10b981","bg":"#10b98115","label":"A — META PICK","desc":"On good_maps list — fully optimised for this map"},
    "B": {"color":"#f59e0b","bg":"#f59e0b12","label":"B — VIABLE",   "desc":"Role or synergy tag overlaps with map features"},
    "C": {"color":"#ff4d6d","bg":"#ff4d6d10","label":"C — OFF-META", "desc":"No direct fit — playable but sub-optimal"},
}


def _tier_agents(agents, map_data):
    """Classify every agent A/B/C for the given map."""
    map_name    = map_data["name"]
    map_feats   = set(map_data.get("key_features", []))
    pref_roles  = set(map_data.get("preferred_roles", []))
    a, b, c = [], [], []
    for agent in agents:
        if map_name in agent.good_maps:
            a.append(agent)
        elif (agent.role in pref_roles or
              len(set(agent.synergy_tags) & map_feats) > 0):
            b.append(agent)
        else:
            c.append(agent)
    return a, b, c


def _agent_card_html(agent, border_color, bg_color):
    img = AGENT_PORTRAITS.get(agent.name, "")
    role_c = RC.get(agent.role, "#64748b")
    tags = "".join(
        f'<span style="background:rgba(0,212,255,0.07);border:1px solid rgba(0,212,255,0.18);'
        f'color:#00d4ff;padding:1px 5px;border-radius:8px;font-size:0.6rem;margin:1px;display:inline-block;">{t}</span>'
        for t in agent.synergy_tags[:3])
    return f"""<!DOCTYPE html><html><head><style>
    *{{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI',Arial,sans-serif;}}
    body{{background:transparent;}}
    .card{{border:1px solid {border_color}55;border-top:3px solid {border_color};border-radius:10px;
           padding:12px;background:{bg_color};}}
    .hdr{{display:flex;align-items:center;gap:9px;margin-bottom:8px;}}
    img{{width:46px;height:46px;object-fit:cover;border-radius:50%;border:2px solid {border_color};flex-shrink:0;}}
    .nm{{font-weight:700;font-size:0.9rem;color:#e2e8f0;}}
    .rl{{font-size:0.65rem;color:{role_c};margin-top:1px;}}
    .lbl{{font-size:0.63rem;color:#475569;text-transform:uppercase;letter-spacing:1px;margin:6px 0 3px;}}
    ul{{margin:0 0 4px 13px;padding:0;}}
    li{{font-size:0.7rem;color:#94a3b8;margin-bottom:1px;line-height:1.45;}}
    </style></head><body>
    <div class="card">
        <div class="hdr">
            <img src="{img}">
            <div><div class="nm">{agent.name}</div><div class="rl">{RI.get(agent.role,"")} {agent.role}</div></div>
        </div>
        <div class="lbl">Synergy</div>
        <div style="margin-bottom:4px;">{tags}</div>
        <div class="lbl">Strengths</div>
        <ul>{''.join(f"<li>{s}</li>" for s in agent.strengths[:2])}</ul>
    </div></body></html>"""


def render():
    agents_all = load_agents()
    maps_list  = load_maps()
    map_names  = [m["name"] for m in maps_list]

    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">📚 Agent Database</h1>
        <p class="page-subtitle">Browse agents · filter by role and map · view map tier lists</p>
    </div>""", unsafe_allow_html=True)

    tab_browse, tab_tier = st.tabs(["🔍 Browse Agents", "🏆 Map Tier List"])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — BROWSE
    # ══════════════════════════════════════════════════════════════════════════
    with tab_browse:
        st.markdown('<div class="card" style="padding:14px 20px;">', unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        with c1: search = st.text_input("🔎 Search",placeholder="Agent name...")
        with c2: role_f = st.selectbox("🎭 Role",["All Roles","Duelist","Controller","Initiator","Sentinel"])
        with c3: map_f  = st.selectbox("🗺️ Map",["All Maps"]+map_names)
        st.markdown('</div>', unsafe_allow_html=True)

        filtered = agents_all
        if search:            filtered = [a for a in filtered if search.lower() in a.name.lower()]
        if role_f!="All Roles": filtered = [a for a in filtered if a.role==role_f]
        if map_f!="All Maps":   filtered = [a for a in filtered if a.fits_map(map_f)]

        rc = {r:sum(1 for a in filtered if a.role==r) for r in RC}
        scols = st.columns(4)
        for i,(role,cnt) in enumerate(rc.items()):
            c = RC[role]
            with scols[i]:
                st.markdown(f"""
                <div class="stat-card" style="border-left:3px solid {c};">
                    <div class="stat-icon">{RI[role]}</div>
                    <div class="stat-value" style="color:{c};">{cnt}</div>
                    <div class="stat-label">{role}s</div>
                </div>""", unsafe_allow_html=True)

        st.markdown(f'<div style="text-align:right;color:#475569;font-size:0.75rem;margin:6px 0 12px;">Showing {len(filtered)} of {len(agents_all)}</div>', unsafe_allow_html=True)

        if not filtered:
            st.markdown('<div style="text-align:center;padding:60px;color:#475569;">🔍 No agents match.</div>', unsafe_allow_html=True)
            return

        for role in ["Duelist","Controller","Initiator","Sentinel"]:
            role_agents = [a for a in filtered if a.role==role]
            if not role_agents: continue
            color = RC[role]
            st.markdown(f"""
            <div style="border-left:4px solid {color};padding:5px 12px;margin:18px 0 10px;
                         background:rgba(0,0,0,0.18);border-radius:0 6px 6px 0;">
                <span style="color:{color};font-weight:700;">{RI[role]} {role}s</span>
                <span style="color:#334155;font-size:0.7rem;margin-left:5px;">({len(role_agents)})</span>
            </div>""", unsafe_allow_html=True)
            for chunk_start in range(0, len(role_agents), 4):
                chunk = role_agents[chunk_start:chunk_start+4]
                cols  = st.columns(4)
                for i, agent in enumerate(chunk):
                    img  = AGENT_PORTRAITS.get(agent.name,"")
                    tags = "".join(f'<span class="tag">{t}</span>' for t in agent.synergy_tags[:3])
                    with cols[i]:
                        components.html(_agent_card_html(agent, color, "#0f1e35"), height=170, scrolling=False)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — MAP TIER LIST
    # ══════════════════════════════════════════════════════════════════════════
    with tab_tier:
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        col_map, col_role = st.columns([2,2])
        with col_map:
            tier_map_name = st.selectbox("🗺️ Select Map", map_names, key="tier_map")
        with col_role:
            tier_role_f = st.selectbox("🎭 Filter Role", ["All Roles","Duelist","Controller","Initiator","Sentinel"], key="tier_role")

        map_data = next((m for m in maps_list if m["name"]==tier_map_name), None)
        if not map_data:
            st.warning("Map not found."); return

        # Map banner
        bias_full  = "⚔️ Attack-sided" if map_data.get("attack_sided") else ("🛡️ Defense-sided" if map_data.get("defense_sided") else "⚖️ Balanced")
        bias_color = "#ff4d6d" if map_data.get("attack_sided") else ("#10b981" if map_data.get("defense_sided") else "#0ea5e9")
        tags_html  = "".join(
            f'<span style="background:rgba(0,212,255,0.07);border:1px solid rgba(0,212,255,0.18);color:#00d4ff;'
            f'padding:2px 8px;border-radius:10px;font-size:0.68rem;margin:2px;display:inline-block;">{f}</span>'
            for f in map_data.get("key_features",[]))
        st.markdown(f"""
        <div style="background:#0f1e35;border:1px solid #1a2f4a;border-left:4px solid {bias_color};
                     border-radius:10px;padding:14px 18px;margin-bottom:16px;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                <span style="font-size:1.4rem;">{map_data["icon"]}</span>
                <span style="font-family:Rajdhani,sans-serif;font-size:1.2rem;font-weight:700;color:#e2e8f0;">{tier_map_name}</span>
                <span style="font-size:0.7rem;padding:2px 10px;border-radius:20px;
                             background:{bias_color}22;border:1px solid {bias_color}55;color:{bias_color};font-weight:600;">{bias_full}</span>
            </div>
            <div>{tags_html}</div>
            <div style="font-size:0.75rem;color:#475569;margin-top:6px;">{map_data.get("notes","")}</div>
        </div>""", unsafe_allow_html=True)

        # Tier classification
        agents_to_tier = agents_all
        if tier_role_f != "All Roles":
            agents_to_tier = [a for a in agents_all if a.role == tier_role_f]

        a_tier, b_tier, c_tier = _tier_agents(agents_to_tier, map_data)

        # Tier legend
        st.markdown("""
        <div style="display:flex;gap:12px;margin-bottom:14px;flex-wrap:wrap;">
            <span style="font-size:0.72rem;color:#10b981;">🟢 A = fully meta on this map</span>
            <span style="font-size:0.72rem;color:#f59e0b;">🟡 B = viable via role/tag overlap</span>
            <span style="font-size:0.72rem;color:#ff4d6d;">🔴 C = off-meta, use with caution</span>
        </div>""", unsafe_allow_html=True)

        # 3-column kanban
        col_a, col_b, col_c = st.columns(3)

        for col, tier_key, agents_in_tier in [
            (col_a,"A",a_tier),(col_b,"B",b_tier),(col_c,"C",c_tier)
        ]:
            ts = TIER_STYLES[tier_key]
            with col:
                st.markdown(f"""
                <div style="background:{ts['bg']};border:1px solid {ts['color']}44;border-top:3px solid {ts['color']};
                             border-radius:12px;padding:12px 10px;min-height:80px;">
                    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;">
                        <div style="font-family:Rajdhani,sans-serif;font-size:1.3rem;font-weight:800;color:{ts['color']};">{tier_key}</div>
                        <div style="background:{ts['color']}22;border:1px solid {ts['color']}55;border-radius:20px;
                                     padding:2px 9px;font-size:0.65rem;font-weight:700;color:{ts['color']};">{len(agents_in_tier)} agents</div>
                    </div>
                    <div style="font-size:0.65rem;color:#334155;margin-bottom:12px;">{ts['desc']}</div>
                </div>""", unsafe_allow_html=True)

                if not agents_in_tier:
                    st.markdown(f'<div style="text-align:center;padding:20px;color:#1e3a5f;font-size:0.8rem;">None</div>', unsafe_allow_html=True)
                    continue

                for agent in agents_in_tier:
                    components.html(_agent_card_html(agent, ts["color"], ts["bg"]), height=170, scrolling=False)

                    # Quick-add to builder button
                    if st.button(f"➕ Add {agent.name}", key=f"tier_add_{tier_map_name}_{agent.name}", use_container_width=True):
                        cur = list(st.session_state.get("selected_agents",[]))
                        if agent.name not in cur and len(cur)<5:
                            cur.append(agent.name)
                            st.session_state["selected_agents"] = cur
                            st.session_state["builder_map"]     = tier_map_name
                            st.session_state["builder_step"]    = 2
                            st.session_state["active_page"]     = "Builder"
                            st.rerun()
