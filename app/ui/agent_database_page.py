"""
Agent Database page — avatar grid with role filter, map filter, search.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
import streamlit as st
import streamlit.components.v1 as components
from assets.agent_portraits import AGENT_PORTRAITS
from app.services.data_loader import load_agents, load_maps

ROLE_COLORS = {
    "Duelist": "#ff4d6d", "Controller": "#7c3aed",
    "Initiator": "#0ea5e9", "Sentinel": "#10b981",
}
ROLE_ICONS = {
    "Duelist": "⚔️", "Controller": "💨",
    "Initiator": "🔍", "Sentinel": "🛡️",
}


def render():
    agents = load_agents()
    maps   = load_maps()
    map_names = [m["name"] for m in maps]

    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">📚 Agent Database</h1>
        <p class="page-subtitle">Browse every agent · filter by role and map · explore synergies</p>
    </div>""", unsafe_allow_html=True)

    # ── Filters ───────────────────────────────────────────────────────────────
    st.markdown('<div class="card" style="padding:14px 20px;">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: search      = st.text_input("🔎 Search", placeholder="Agent name...")
    with c2: role_filter = st.selectbox("🎭 Role", ["All Roles","Duelist","Controller","Initiator","Sentinel"])
    with c3: map_filter  = st.selectbox("🗺️ Map", ["All Maps"] + map_names)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Apply filters ──────────────────────────────────────────────────────────
    filtered = agents
    if search:      filtered = [a for a in filtered if search.lower() in a.name.lower()]
    if role_filter != "All Roles": filtered = [a for a in filtered if a.role == role_filter]
    if map_filter  != "All Maps":  filtered = [a for a in filtered if a.fits_map(map_filter)]

    # ── Stats row ──────────────────────────────────────────────────────────────
    role_counts = {"Duelist":0,"Controller":0,"Initiator":0,"Sentinel":0}
    for a in filtered:
        if a.role in role_counts: role_counts[a.role] += 1

    scols = st.columns(4)
    for i,(role,cnt) in enumerate(role_counts.items()):
        c = ROLE_COLORS[role]
        with scols[i]:
            st.markdown(f"""
            <div class="stat-card" style="border-left:3px solid {c};">
                <div class="stat-icon">{ROLE_ICONS[role]}</div>
                <div class="stat-value" style="color:{c};">{cnt}</div>
                <div class="stat-label">{role}s</div>
            </div>""", unsafe_allow_html=True)

    st.markdown(f'<div style="text-align:right;color:#475569;font-size:0.78rem;margin:6px 0 12px;">Showing {len(filtered)} of {len(agents)} agents</div>', unsafe_allow_html=True)

    if not filtered:
        st.markdown('<div style="text-align:center;padding:60px;color:#475569;font-size:1.1rem;">🔍 No agents match your filters.</div>', unsafe_allow_html=True)
        return

    # ── Avatar grid grouped by role ────────────────────────────────────────────
    for role in ["Duelist","Controller","Initiator","Sentinel"]:
        role_agents = [a for a in filtered if a.role == role]
        if not role_agents: continue
        color = ROLE_COLORS[role]

        st.markdown(f"""
        <div style="border-left:4px solid {color};padding:6px 14px;margin:20px 0 12px;
             border-radius:0 6px 6px 0;background:rgba(0,0,0,0.2);">
            <span style="font-family:'Rajdhani',sans-serif;font-size:1.1rem;font-weight:700;color:{color};">
                {ROLE_ICONS[role]} {role}s
            </span>
            <span style="font-size:0.75rem;color:#334155;margin-left:8px;">({len(role_agents)})</span>
        </div>""", unsafe_allow_html=True)

        chunk_size = 4
        for start in range(0, len(role_agents), chunk_size):
            chunk = role_agents[start:start+chunk_size]
            cols  = st.columns(chunk_size)
            for i, agent in enumerate(chunk):
                img  = AGENT_PORTRAITS.get(agent.name,"")
                tags = " ".join(f'<span class="tag">{t}</span>' for t in agent.synergy_tags[:3])
                good_maps_str = ", ".join(agent.good_maps[:4])
                strengths_li  = "".join(f"<li>{s}</li>" for s in agent.strengths[:3])
                weaknesses_li = "".join(f"<li>{w}</li>" for w in agent.weaknesses[:2])

                with cols[i]:
                    card_html = f"""<!DOCTYPE html><html><head><style>
                    *{{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI',sans-serif;}}
                    body{{background:transparent;}}
                    .card{{background:#0f1e35;border:1px solid #1a2f4a;border-top:3px solid {color};
                           border-radius:10px;padding:14px;min-height:260px;}}
                    .hdr{{display:flex;align-items:center;gap:10px;margin-bottom:10px;
                           padding-bottom:8px;border-bottom:1px solid #1a2f4a;}}
                    img{{width:52px;height:52px;object-fit:cover;border-radius:50%;
                         border:2px solid {color};flex-shrink:0;}}
                    .fb{{width:52px;height:52px;border-radius:50%;border:2px solid {color};
                         flex-shrink:0;display:flex;align-items:center;justify-content:center;
                         font-size:1.6rem;background:#0a1628;}}
                    .nm{{font-weight:700;font-size:1rem;color:#e2e8f0;}}
                    .rl{{font-size:0.72rem;color:{color};}}
                    .lbl{{font-size:0.65rem;color:#475569;text-transform:uppercase;
                           letter-spacing:1px;margin:7px 0 3px;}}
                    ul{{margin:0 0 4px 14px;padding:0;}}
                    li{{font-size:0.72rem;color:#94a3b8;margin-bottom:2px;line-height:1.5;}}
                    .sl li{{color:#10b981;}} .wl li{{color:#ff6b6b;}}
                    .maps{{font-size:0.7rem;color:#7c3aed;margin-bottom:5px;}}
                    .tag{{display:inline-block;font-size:0.62rem;padding:1px 6px;border-radius:10px;
                           background:rgba(0,212,255,0.08);border:1px solid rgba(0,212,255,0.2);
                           color:#00d4ff;margin:1px;}}
                    </style></head><body>
                    <div class="card">
                        <div class="hdr">
                            <img src="{img}" onerror="this.style.display='none';document.getElementById('f_{agent.name.replace("/","_").replace(" ","_")}').style.display='flex'">
                            <div class="fb" id="f_{agent.name.replace("/","_").replace(" ","_")}" style="display:none;">{agent.icon}</div>
                            <div><div class="nm">{agent.name}</div><div class="rl">{ROLE_ICONS.get(agent.role,"")} {agent.role}</div></div>
                        </div>
                        <div class="lbl">✅ Strengths</div>
                        <ul class="sl">{strengths_li}</ul>
                        <div class="lbl">❌ Weaknesses</div>
                        <ul class="wl">{weaknesses_li}</ul>
                        <div class="lbl">🗺️ Good Maps</div>
                        <div class="maps">{good_maps_str}</div>
                        <div class="lbl">🏷️ Tags</div>
                        <div>{tags}</div>
                    </div>
                    </body></html>"""
                    components.html(card_html, height=290, scrolling=False)
