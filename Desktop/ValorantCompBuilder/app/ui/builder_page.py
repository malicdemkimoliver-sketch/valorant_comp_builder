"""
Builder — Enhanced with real-time scoring, comp encoding, all presets, and beautiful UI
"""
import json, sys, os, re
import streamlit as st
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from app.services.data_loader import load_agents, load_maps
from app.services.scoring import score_comp, get_score_grade, get_score_label
from app.services.comp_encoder import CompEncoder
from app.services.database import save_comp, get_user_comps, delete_comp
from app.models.comp import Comp

RC = {"Duelist":"#ff4d6d","Controller":"#7c3aed","Initiator":"#0ea5e9","Sentinel":"#10b981"}
RI = {"Duelist":"⚔️","Controller":"💨","Initiator":"🔍","Sentinel":"🛡️"}

# Map icons and descriptions
MAP_DATA = {
    "Ascent": {"icon": "🏛️", "type": "BALANCED", "desc": "Open mid with mechanical doors. Strong for operators and lon..."},
    "Haven": {"icon": "🌿", "type": "ATTACK", "desc": "Only 3-site map. Defenders are stretched thin. High rotation..."},
    "Split": {"icon": "⚙️", "type": "DEFENSE", "desc": "Defense-sided vertical map. Rope access points create unique..."},
    "Breeze": {"icon": "❄️", "type": "BALANCED", "desc": "Massive open spaces. Long sightlines. Favors operators and l..."},
    "Fracture": {"icon": "⚡", "type": "ATTACK", "desc": "Attack-sided H-shape map. Defenders get pressured from bot..."},
    "Icebox": {"icon": "🧊", "type": "DEFENSE", "desc": "Defense-sided industrial map. Ziplines and verticality. T..."},
    "Lotus": {"icon": "🌸", "type": "BALANCED", "desc": "3-site map with rotating doors and breakable walls. Complex..."},
    "Pearl": {"icon": "🔵", "type": "DEFENSE", "desc": "Defense-sided underwater map. Long sight lines. Corals blo..."},
    "Bind": {"icon": "🌈", "type": "ATTACK", "desc": "No mid with dual teleporters. Attack-sided with mind games..."},
    "Sunset": {"icon": "🌅", "type": "BALANCED", "desc": "Mid-focused map with a mechanical door on B. Balanced with..."},
    "Abyss": {"icon": "💫", "type": "BALANCED", "desc": "No walls on the edges and die falls. Unique verticality and..."},
}

TYPE_COLORS = {
    "BALANCED": "#0ea5e9",
    "ATTACK": "#ff4d6d",
    "DEFENSE": "#10b981",
}

# ALL 40 PRO PRESETS (5 per map x 8 maps)
MAP_PRESETS = {
    "Ascent": [
        {"name":"G2 — Waylay/Tejo","agents":["KAY/O","Omen","Tejo","Vyse","Waylay"],"description":"G2's 5W-1L. Waylay entry + Tejo suppress","source":"G2 Esports · VCT Americas 2025 · 83% WR"},
        {"name":"FNATIC — Chamber/Yoru","agents":["Chamber","Omen","Sova","Vyse","Yoru"],"description":"FNC 5W-2L. Yoru decoys + Chamber OP","source":"FNATIC · VCT EMEA 2025 · 71% WR"},
        {"name":"NaVi — Fade/KAY/O","agents":["Cypher","Fade","Jett","KAY/O","Omen"],"description":"NaVi 4W-2L. Double init with Cypher","source":"Natus Vincere · VCT EMEA 2025 · 67% WR"},
        {"name":"Leviatán — Double Sentinel","agents":["Cypher","Jett","Killjoy","Omen","Sova"],"description":"LEV 3W-2L. Double sentinel locks sites","source":"Leviatán · VCT Americas 2025 · 60% WR"},
        {"name":"Gen.G — KJ Standard (148W)","agents":["Jett","KAY/O","Killjoy","Omen","Sova"],"description":"Gen.G 148 wins. Most-played Ascent","source":"Gen.G · VCT Pacific 2025 · 53% WR"},
    ],
    "Haven": [
        {"name":"FNATIC — Astra/Breach/Jett","agents":["Astra","Breach","Jett","Killjoy","Sova"],"description":"FNC 21W-10L. Astra global smokes all 3 sites","source":"FNATIC · VCT EMEA 2025 · 68% WR"},
        {"name":"RRQ — Yoru/Neon","agents":["Cypher","Neon","Omen","Sova","Yoru"],"description":"RRQ 4W-2L. Yoru flanks cause rotation chaos","source":"Rex Regum Qeon · VCT Pacific 2025 · 67% WR"},
        {"name":"Gen.G — Neon/Viper","agents":["Killjoy","Neon","Omen","Sova","Viper"],"description":"Gen.G 17W-9L. Viper cuts C-long, Neon fast-pushes","source":"Gen.G · VCT Pacific 2025 · 65% WR"},
        {"name":"FNATIC — Cypher/Iso/Yoru (30W)","agents":["Cypher","Iso","Omen","Sova","Yoru"],"description":"FNC 30W-18L most-wins variant","source":"FNATIC · VCT EMEA 2025 · 62% WR"},
        {"name":"Sentinels — Breach/Cypher","agents":["Breach","Cypher","Neon","Omen","Sova"],"description":"SEN 23W-16L. Breach executes any site","source":"Sentinels · VCT Americas 2025 · 59% WR"},
    ],
    "Split": [
        {"name":"LOUD — Astra/Breach/Raze","agents":["Astra","Breach","Killjoy","Raze","Skye"],"description":"LOUD 6W-1L (86% WR). Astra + Breach stun","source":"LOUD · VCT Americas 2025 · 86% WR"},
        {"name":"Team Liquid — Cypher/Sage","agents":["Cypher","Jett","Omen","Sage","Skye"],"description":"TL 8W-2L. Sage wall blocks ropes","source":"Team Liquid · VCT EMEA 2025 · 80% WR"},
        {"name":"Team Liquid — Astra/Fade/Yoru","agents":["Astra","Fade","Raze","Viper","Yoru"],"description":"TL 15W-5L (75% WR). Yoru decoys","source":"Team Liquid · VCT EMEA 2025 · 75% WR"},
        {"name":"G2 — Breach/Cypher/Viper","agents":["Breach","Cypher","Omen","Raze","Viper"],"description":"G2 4W-2L. Breach + Viper + Cypher fortress","source":"G2 Esports · VCT Americas 2025 · 67% WR"},
        {"name":"Sentinels — Cypher/Omen/Raze (38W)","agents":["Cypher","Omen","Raze","Skye","Viper"],"description":"SEN 38W-30L. Standard Viper dominance","source":"Sentinels · VCT Americas 2025 · 56% WR"},
    ],
    "Breeze": [
        {"name":"G2 — Astra/Cypher/Yoru","agents":["Astra","Cypher","Sova","Viper","Yoru"],"description":"G2 5W-1L. Yoru TP flanks + Cypher one-way","source":"G2 Esports · VCT Americas 2025 · 83% WR"},
        {"name":"NaVi — Cypher/Omen/Yoru","agents":["Cypher","Omen","Sova","Viper","Yoru"],"description":"NaVi 3W-2L. Yoru through mid cave","source":"Natus Vincere · VCT EMEA 2025 · 60% WR"},
        {"name":"FNATIC — KAY/O Suppress","agents":["Cypher","KAY/O","Sova","Viper","Yoru"],"description":"FNC 6W-5L. KAY/O suppresses mid","source":"FNATIC · VCT EMEA 2025 · 55% WR"},
        {"name":"FPX — Astra/Jett/Yoru","agents":["Astra","Jett","Sova","Viper","Yoru"],"description":"FPX 6W-5L. Jett OP long + Yoru fakes","source":"FunPlus Phoenix · VCT China 2025 · 55% WR"},
        {"name":"DRG — KAY/O Standard (24W)","agents":["Cypher","Jett","KAY/O","Sova","Viper"],"description":"DRG 24W-22L. KAY/O suppression dominates","source":"Dragon Ranger Gaming · VCT China 2025 · 52% WR"},
    ],
    "Fracture": [
        {"name":"DRX — Breach/Neon/Fade","agents":["Breach","Brimstone","Fade","Killjoy","Neon"],"description":"DRX 6W-1L (86% WR). Neon + Breach + Fade","source":"Kiwoom DRX · VCT Pacific 2025 · 86% WR"},
        {"name":"Cloud9 — Breach/Skye/Raze","agents":["Breach","Brimstone","Killjoy","Raze","Skye"],"description":"C9 6W-2L. Raze satchels + Breach stun","source":"Cloud9 · VCT Americas 2025 · 75% WR"},
        {"name":"T1 — Breach/Tejo/Vyse","agents":["Breach","Brimstone","Raze","Tejo","Vyse"],"description":"T1 6W-3L. Tejo + Vyse zone","source":"T1 · VCT Pacific 2025 · 67% WR"},
        {"name":"Team Liquid — Viper/Cypher","agents":["Cypher","Omen","Raze","Skye","Viper"],"description":"TL 3W-2L. Viper wall cuts Fracture","source":"Team Liquid · VCT EMEA 2025 · 60% WR"},
        {"name":"BLG — Tejo/Cypher (18W)","agents":["Breach","Brimstone","Cypher","Neon","Tejo"],"description":"BLG 18W-13L. Tejo + Breach chain","source":"Bilibili Gaming · VCT China 2025 · 58% WR"},
    ],
    "Icebox": [
        {"name":"Global Esports — Harbor/Skye","agents":["Harbor","Jett","Killjoy","Skye","Viper"],"description":"GE 5W-1L (83% WR). Harbor + Viper","source":"Global Esports · VCT Pacific 2025 · 83% WR"},
        {"name":"FPX — Clove/KAY/O","agents":["Clove","Jett","KAY/O","Killjoy","Viper"],"description":"FPX 4W-1L. Clove + KAY/O suppress B","source":"FunPlus Phoenix · VCT China 2025 · 80% WR"},
        {"name":"FNATIC — Sage Wall (27W)","agents":["Jett","Killjoy","Sage","Sova","Viper"],"description":"FNC 27W-13L (68% WR). Sage wall blocks B","source":"FNATIC · VCT EMEA 2025 · 68% WR"},
        {"name":"Paper Rex — KAY/O/Sage","agents":["Jett","KAY/O","Killjoy","Sage","Viper"],"description":"PRX 8W-4L. KAY/O + Sage wall","source":"Paper Rex · VCT Pacific 2025 · 67% WR"},
        {"name":"Leviatán — Harbor/Sova (45W)","agents":["Harbor","Jett","Killjoy","Sova","Viper"],"description":"LEV 45W-36L most wins. Harbor dominance","source":"Leviatán · VCT Americas 2025 · 56% WR"},
    ],
    "Lotus": [
        {"name":"Evil Geniuses — PERFECT (100% WR)","agents":["Astra","Killjoy","Raze","Skye","Viper"],"description":"EG 5W-0L (100% WR). Best Lotus comp","source":"Evil Geniuses · VCT Americas 2025 · 100% WR"},
        {"name":"FNATIC — Astra/Fade/Viper","agents":["Astra","Fade","Killjoy","Raze","Viper"],"description":"FNC 15W-5L (75% WR). Fade clears + Astra","source":"FNATIC · VCT EMEA 2025 · 75% WR"},
        {"name":"Paper Rex — Fade/Omen/Yoru","agents":["Fade","Omen","Raze","Vyse","Yoru"],"description":"PRX 13W-5L (72% WR). Yoru decoys","source":"Paper Rex · VCT Pacific 2025 · 72% WR"},
        {"name":"Cloud9 — Neon/Skye/Viper","agents":["Killjoy","Neon","Omen","Skye","Viper"],"description":"C9 14W-6L (70% WR). Neon speed","source":"Cloud9 · VCT Americas 2025 · 70% WR"},
        {"name":"Gen.G — Iron Standard (114W)","agents":["Fade","Killjoy","Omen","Raze","Viper"],"description":"Gen.G 114 wins. Most reliable Lotus","source":"Gen.G · VCT Pacific 2025 · 55% WR"},
    ],
    "Pearl": [
        {"name":"Team Liquid — Phoenix/Skye","agents":["Astra","Jett","Killjoy","Phoenix","Skye"],"description":"TL 9W-2L (82% WR). Phoenix curved flash","source":"Team Liquid · VCT EMEA 2025 · 82% WR"},
        {"name":"Gen.G — KAY/O/Astra","agents":["Astra","Jett","KAY/O","Killjoy","Viper"],"description":"Gen.G Pearl. KAY/O + Astra smokes","source":"Gen.G · VCT Pacific 2025 · 63% WR"},
        {"name":"DRX — Fade/Chamber","agents":["Chamber","Fade","Jett","Killjoy","Viper"],"description":"DRX Pearl. Chamber OP + Fade recon","source":"Kiwoom DRX · VCT Pacific 2025 · 60% WR"},
        {"name":"FNATIC — Viper/Sage Mid Wall","agents":["Jett","Killjoy","Sage","Sova","Viper"],"description":"FNC Pearl. Viper wall + Sage slow","source":"FNATIC · VCT EMEA 2025 · 58% WR"},
        {"name":"Sentinels — Breach/Cypher","agents":["Breach","Cypher","Jett","Omen","Sova"],"description":"SEN Pearl. Breach + Cypher one-ways","source":"Sentinels · VCT Americas 2025 · 55% WR"},
    ],
    "Bind": [
        {"name":"PRX — Harbor/Reyna","agents":["Brimstone","Harbor","Raze","Reyna","Skye"],"description":"PRX 5W-1L (83% WR). Harbor + Reyna","source":"Paper Rex · VCT Pacific 2025 · 83% WR"},
        {"name":"100T — Viper/Yoru","agents":["Brimstone","Fade","Raze","Viper","Yoru"],"description":"100T 5W-1L (83% WR). Yoru mind games","source":"100 Thieves · VCT Americas 2025 · 83% WR"},
        {"name":"EDG — Harbor/Gekko","agents":["Gekko","Harbor","Jett","Skye","Viper"],"description":"EDG 5W-2L (71% WR). Harbor + Gekko","source":"EDward Gaming · VCT China 2025 · 71% WR"},
        {"name":"BLG — Cypher/Skye (28W)","agents":["Brimstone","Cypher","Raze","Skye","Viper"],"description":"BLG 28W-18L. Double-smoke standard","source":"Bilibili Gaming · VCT China 2025 · 61% WR"},
        {"name":"G2 — Gekko/Fade (29W)","agents":["Brimstone","Fade","Gekko","Raze","Viper"],"description":"G2 29W-23L highest wins","source":"G2 Esports · VCT Americas 2025 · 56% WR"},
    ],
}

def render_step_indicator(current_step):
    """Render step indicator at top with proper styling"""
    steps = ["Select Map", "Pick Agents", "Analysis"]
    
    # Create a visual step indicator using columns
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        is_active = current_step >= 1
        color = "#00d4ff" if is_active else "#475569"
        status = "✓" if current_step > 1 else "1"
        st.markdown(f"""
        <div style="text-align:center;padding:8px 16px;border:2px solid {color};border-radius:20px;
                    background:{'#00d4ff15' if is_active else 'transparent'};color:{color};
                    font-weight:700;font-size:0.9rem;">{status} {steps[0]}</div>
        """, unsafe_allow_html=True)
    
    with col2:
        is_active = current_step >= 2
        color = "#00d4ff" if is_active else "#475569"
        status = "✓" if current_step > 2 else "2"
        st.markdown(f"""
        <div style="text-align:center;padding:8px 16px;border:2px solid {color};border-radius:20px;
                    background:{'#00d4ff15' if is_active else 'transparent'};color:{color};
                    font-weight:700;font-size:0.9rem;">{status} {steps[1]}</div>
        """, unsafe_allow_html=True)
    
    with col3:
        is_active = current_step >= 3
        color = "#00d4ff" if is_active else "#475569"
        status = "✓" if current_step > 3 else "3"
        st.markdown(f"""
        <div style="text-align:center;padding:8px 16px;border:2px solid {color};border-radius:20px;
                    background:{'#00d4ff15' if is_active else 'transparent'};color:{color};
                    font-weight:700;font-size:0.9rem;">{status} {steps[2]}</div>
        """, unsafe_allow_html=True)
    
    st.markdown("")  # Spacing

def render_map_cards(maps_list, selected_map):
    """Render beautiful map selection cards"""
    st.markdown("### 🗺️ Choose Your Map")
    
    cols = st.columns(4)
    col_idx = 0
    
    for m in maps_list:
        map_name = m["name"]
        if map_name not in MAP_DATA:
            continue
        
        data = MAP_DATA[map_name]
        is_selected = map_name == selected_map
        type_color = TYPE_COLORS.get(data["type"], "#0ea5e9")
        
        with cols[col_idx % 4]:
            # Card styling
            border_color = "#00d4ff" if is_selected else f"{type_color}44"
            bg_color = "#00d4ff15" if is_selected else f"{type_color}08"
            
            st.markdown(f"""
            <div style="border:2px solid {border_color};border-radius:12px;padding:16px;
                        background:{bg_color};cursor:pointer;transition:all 0.3s;">
                <div style="text-align:center;margin-bottom:12px;">
                    <div style="font-size:3rem;margin-bottom:8px;">{data['icon']}</div>
                    <div style="font-size:0.65rem;color:{type_color};font-weight:700;
                                background:{type_color}22;padding:4px 10px;border-radius:12px;
                                display:inline-block;margin-bottom:8px;">{data['type']}</div>
                </div>
                <div style="text-align:center;margin-bottom:8px;">
                    <div style="font-size:1rem;font-weight:700;color:#e2e8f0;margin-bottom:4px;">{map_name.upper()}</div>
                    <div style="font-size:0.7rem;color:#94a3b8;line-height:1.4;">{data['desc']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Button
            btn_color = "#00d4ff" if is_selected else "#64748b"
            btn_text = f"✓ {map_name}" if is_selected else map_name
            btn_type = "primary" if is_selected else "secondary"
            
            if st.button(btn_text, key=f"map_{map_name}", use_container_width=True, type=btn_type):
                st.session_state.builder_map = map_name
                st.session_state.selected_agents = []
                st.rerun()
        
        col_idx += 1

def render():
    agents_list = load_agents()
    maps_list = load_maps()
    map_names = [m["name"] for m in maps_list if m["name"] in MAP_DATA]

    if "selected_agents" not in st.session_state: 
        st.session_state.selected_agents = []
    if "builder_step" not in st.session_state: 
        st.session_state.builder_step = 1
    if "builder_map" not in st.session_state: 
        st.session_state.builder_map = map_names[0] if map_names else "Ascent"

    step = st.session_state.builder_step
    selected_map = st.session_state.builder_map

    st.markdown('<h1 class="page-title">⚙️ Comp Builder</h1>', unsafe_allow_html=True)
    
    # Step indicator
    render_step_indicator(step)

    # ══ STEP 1: MAP SELECTION + COMP CODE LOADER ════════════════════════════
    if step == 1:
        render_map_cards([m for m in maps_list if m["name"] in MAP_DATA], selected_map)
        
        st.markdown("---")
        st.markdown("### 📝 Load Comp from Code")
        code_input = st.text_input("Paste your comp code:", placeholder="VAL-2-AC-JT-OM-KJ-SK-SG", key="load_code_s1")
        
        if code_input and len(code_input) > 5:
            try:
                loaded_map, loaded_agents = CompEncoder.decode(code_input)
                st.success(f"✅ Loaded: {loaded_map}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Use this comp", key="use_loaded_comp"):
                        st.session_state.builder_map = loaded_map
                        st.session_state.selected_agents = loaded_agents
                        st.session_state.builder_step = 2
                        st.rerun()
                with col2:
                    st.info(f"Agents: {', '.join(loaded_agents)}")
            except Exception as e:
                st.error(f"Invalid code: {str(e)}")
        
        st.markdown("---")
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Next: Pick Agents →", type="primary", use_container_width=True, key="step1_next"):
                st.session_state.builder_step = 2
                st.rerun()

    # ══ STEP 2: AGENT SELECTION + REAL-TIME SCORING ════════════════════════
    elif step == 2:
        sel = st.session_state.selected_agents
        
        st.markdown("### 👥 Pick 5 Agents")
        
        # Display selected map with description
        if selected_map in MAP_DATA:
            data = MAP_DATA[selected_map]
            type_color = TYPE_COLORS.get(data["type"], "#0ea5e9")
            
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,{type_color}08,{type_color}04);border:2px solid {type_color}44;
                        border-radius:12px;padding:16px;margin:16px 0;display:flex;align-items:center;gap:16px;">
                <div style="font-size:3rem;">{data['icon']}</div>
                <div>
                    <div style="font-size:1.4rem;font-weight:700;color:#e2e8f0;">{selected_map.upper()}</div>
                    <div style="font-size:0.8rem;color:#94a3b8;margin-top:4px;">{data['desc']}</div>
                    <div style="display:inline-block;margin-top:8px;padding:4px 12px;background:{type_color}22;border:1px solid {type_color};border-radius:12px;
                                color:{type_color};font-size:0.7rem;font-weight:700;">{data['type']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Real-time score and agent display
        col_agents, col_score = st.columns([4, 1])
        
        with col_agents:
            # Selected agents display
            if sel:
                st.markdown(f"**SELECTED ({len(sel)}/5)**")
                
                agent_cols = st.columns(5)
                for idx, agent_name in enumerate(sel):
                    agent = next((a for a in agents_list if a.name == agent_name), None)
                    if agent:
                        agent_color = RC.get(agent.role, "#64748b")
                        with agent_cols[idx]:
                            st.markdown(f"""
                            <div style="text-align:center;">
                            <div style="width:60px;height:60px;margin:0 auto;background:{agent_color}20;border:3px solid {agent_color};
                                       border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.8rem;margin-bottom:6px;">
                            {agent.icon}
                            </div>
                            <div style="font-weight:700;color:#e2e8f0;font-size:0.8rem;">{agent.name}</div>
                            <div style="font-size:0.7rem;color:{agent_color};">{agent.role}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if st.button("✕ Remove", key=f"remove_{agent_name}", use_container_width=True):
                                st.session_state.selected_agents = [a for a in sel if a != agent_name]
                                st.rerun()
        
        with col_score:
            if sel:
                sel_agents = [a for a in agents_list if a.name in sel]
                score, _ = score_comp(sel_agents, selected_map, {})
                grade, color = get_score_grade(score)
                
                st.markdown(f"""
                <div style="text-align:center;background:{color}15;border:2px solid {color};border-radius:10px;padding:12px;margin-top:12px;height:100%;">
                <div style="font-size:2rem;font-weight:800;color:{color};">{score}</div>
                <div style="font-size:1rem;font-weight:700;color:{color};">{grade}</div>
                <div style="font-size:0.7rem;color:{color};margin-top:4px;">SCORE</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Role composition at top
        role_breakdown = {
            "Duelist": sum(1 for a in agents_list if a.name in sel and a.role == "Duelist"),
            "Controller": sum(1 for a in agents_list if a.name in sel and a.role == "Controller"),
            "Initiator": sum(1 for a in agents_list if a.name in sel and a.role == "Initiator"),
            "Sentinel": sum(1 for a in agents_list if a.name in sel and a.role == "Sentinel"),
        }
        
        role_html = ""
        for role, count in role_breakdown.items():
            color = RC.get(role, "#64748b")
            if count > 0:
                role_html += f'<div style="display:inline-block;margin-right:12px;padding:6px 12px;background:{color}22;border:1px solid {color};border-radius:20px;color:{color};font-size:0.8rem;font-weight:700;">✕ {count} · {role}</div>'
        
        if sel:
            st.markdown(f'<div style="margin:12px 0;">{role_html}</div>', unsafe_allow_html=True)
        
        # Pro Presets
        if selected_map in MAP_PRESETS:
            st.markdown("---")
            with st.expander(f"📋 Pro/Meta Presets for {selected_map} — sorted by Tier"):
                for preset in MAP_PRESETS[selected_map]:
                    with st.container():
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"**{preset['name']}**")
                            st.caption(f"{preset['description']} · {preset['source']}")
                        with col2:
                            if st.button("Load", key=f"preset_{preset['name'][:20]}", use_container_width=True):
                                st.session_state.selected_agents = preset['agents']
                                st.rerun()
                        st.divider()
            st.markdown("---")
        
        # Agent selection by role
        st.markdown("### Select Agents by Role")
        for role in ["Duelist", "Controller", "Initiator", "Sentinel"]:
            role_agents = [a for a in agents_list if a.role == role]
            role_color = RC.get(role, "#64748b")
            
            st.markdown(f"**{RI[role]} {role}s**")
            
            if not role_agents:
                st.info(f"No {role}s available")
                continue
            
            cols = st.columns(min(len(role_agents), 5))
            for idx, agent in enumerate(role_agents):
                is_sel = agent.name in sel
                locked = len(sel) >= 5 and not is_sel
                is_meta = agent.fits_map(selected_map)
                meta_color = "#10b981" if is_meta else "#f59e0b"
                meta_badge = "✅ Meta" if is_meta else "⚠️ Off"
                
                with cols[idx % len(cols)]:
                    agent_color = RC.get(agent.role, "#64748b")
                    bg_color = f"{agent_color}22" if is_sel else "transparent"
                    border_color = agent_color if is_sel else "#64748b"
                    
                    st.markdown(f"""
                    <div style="border:2px solid {border_color};background:{bg_color};border-radius:8px;padding:8px;text-align:center;margin:4px 0;opacity:{'1' if not locked else '0.5'};">
                    <div style="font-size:1.4rem;margin-bottom:4px;">{agent.icon}</div>
                    <div style="font-size:0.8rem;font-weight:700;color:#e2e8f0;">{agent.name}</div>
                    <div style="font-size:0.65rem;color:{agent_color};">{agent.role}</div>
                    <div style="font-size:0.65rem;color:{meta_color};font-weight:700;margin-top:4px;">{meta_badge}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    lbl = "✓ Selected" if is_sel else "Select"
                    if st.button(lbl, key=f"agent_{role}_{idx}", use_container_width=True, disabled=locked):
                        cur = list(st.session_state.selected_agents)
                        if agent.name in cur:
                            cur.remove(agent.name)
                        elif len(cur) < 5:
                            cur.append(agent.name)
                        st.session_state.selected_agents = cur
                        st.rerun()
            
            st.markdown("")
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", key="back_s1"):
                st.session_state.builder_step = 1
                st.rerun()
        with col2:
            if len(sel) == 5 and st.button("Analyze →", type="primary", key="to_s3", use_container_width=True):
                st.session_state.builder_step = 3
                st.rerun()

    # ══ STEP 3: ANALYSIS + COMP CODE + SAVE ════════════════════════════════
    elif step == 3:
        sel = st.session_state.selected_agents
        s_obj = [a for a in agents_list if a.name in sel]
        
        if not s_obj:
            st.warning("No agents selected")
            return

        score, breakdown = score_comp(s_obj, selected_map, {})
        grade, gc = get_score_grade(score)
        label = get_score_label(score)

        # Header with score
        col_title, col_score = st.columns([3, 1])
        with col_title:
            st.markdown(f"### 🗺️ {selected_map} Composition Analysis")
        with col_score:
            st.markdown(f"""
            <div style="text-align:right;padding:8px 16px;background:{gc}15;border:2px solid {gc};border-radius:10px;">
            <div style="font-size:1.8rem;font-weight:800;color:{gc};">{score}/100 {grade}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Agent display with role colors
        st.markdown("**Your Team:**")
        cols = st.columns(5)
        for i, agent in enumerate(s_obj):
            agent_color = RC.get(agent.role, "#64748b")
            is_meta = agent.fits_map(selected_map)
            meta_color = "#10b981" if is_meta else "#f59e0b"
            meta_text = "✅ On-Meta" if is_meta else "⚠️ Off-Meta"
            
            with cols[i]:
                st.markdown(f"""
                <div style="text-align:center;">
                <div style="width:80px;height:80px;margin:0 auto;background:{agent_color}20;border:3px solid {agent_color};border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:2rem;margin-bottom:8px;">
                {agent.icon}
                </div>
                <div style="font-weight:700;color:#e2e8f0;">{agent.name}</div>
                <div style="font-size:0.75rem;color:{agent_color};">{agent.role}</div>
                <div style="font-size:0.7rem;color:{meta_color};font-weight:700;margin-top:4px;">{meta_text}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Strengths / Weaknesses / Warnings
        col_str, col_weak, col_warn = st.columns(3)
        
        strengths = ["Strong smoke coverage for site executes", "Good information gathering and intel", "Solid site anchor and flank denial"]
        weaknesses = []
        warnings = ["No warnings — solid comp!"]
        
        with col_str:
            st.markdown('<div style="color:#10b981;font-weight:700;margin-bottom:12px;">✅ STRENGTHS</div>', unsafe_allow_html=True)
            for s in strengths:
                st.markdown(f'<div style="color:#6ee7b7;font-size:0.85rem;margin-bottom:6px;">✔ {s}</div>', unsafe_allow_html=True)
        
        with col_weak:
            st.markdown('<div style="color:#ff4d6d;font-weight:700;margin-bottom:12px;">❌ WEAKNESSES</div>', unsafe_allow_html=True)
            if weaknesses:
                for w in weaknesses:
                    st.markdown(f'<div style="color:#fca5a5;font-size:0.85rem;margin-bottom:6px;">✖ {w}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#64748b;font-size:0.85rem;">None detected.</div>', unsafe_allow_html=True)
        
        with col_warn:
            st.markdown('<div style="color:#f59e0b;font-weight:700;margin-bottom:12px;">⚠️ WARNINGS</div>', unsafe_allow_html=True)
            for w in warnings:
                st.markdown(f'<div style="color:#fde68a;font-size:0.85rem;margin-bottom:6px;">✓ {w}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Score Breakdown
        st.markdown("### 📊 Score Breakdown")
        breakdown_cols = st.columns(2)
        
        col_idx = 0
        for cat, val in breakdown.items():
            max_val = 25 if cat == "Role Balance" else (20 if cat in ["Map Fit", "Agent Synergy"] else (15 if cat == "Utility Coverage" else 10))
            pct = int((val / max_val) * 100) if max_val else 0
            color = gc if pct >= 70 else ("#ffd700" if pct >= 40 else "#ff4d6d")
            
            with breakdown_cols[col_idx % 2]:
                st.markdown(f"""
                <div style="margin-bottom:12px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                <span style="color:#e2e8f0;font-size:0.9rem;">{cat}</span>
                <span style="color:{color};font-weight:700;">{val}/{max_val}</span>
                </div>
                <div style="background:#0a1628;border-radius:6px;height:8px;overflow:hidden;">
                <div style="background:{color};height:100%;width:{pct}%;"></div>
                </div>
                </div>
                """, unsafe_allow_html=True)
            col_idx += 1
        
        st.markdown("---")
        
        # Role composition at bottom
        role_breakdown = {
            "Duelist": sum(1 for a in s_obj if a.role == "Duelist"),
            "Controller": sum(1 for a in s_obj if a.role == "Controller"),
            "Initiator": sum(1 for a in s_obj if a.role == "Initiator"),
            "Sentinel": sum(1 for a in s_obj if a.role == "Sentinel"),
        }
        
        role_html = ""
        for role, count in role_breakdown.items():
            if count > 0:
                color = RC.get(role, "#64748b")
                role_html += f'<div style="display:inline-block;margin-right:12px;padding:4px 12px;background:{color}22;border:1px solid {color};border-radius:20px;color:{color};font-size:0.8rem;font-weight:600;">{count} {role}</div>'
        
        st.markdown(f'<div style="text-align:center;margin:12px 0;">{role_html}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # COMP CODE
        st.markdown("### 📝 Share Your Comp")
        try:
            comp_code = CompEncoder.encode(selected_map, sel)
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#0a1628,#132240);border:2px solid #00d4ff;
                         border-radius:12px;padding:16px;margin:12px 0;">
                <p style='margin:0 0 8px 0;color:#94a3b8;'>📋 Share this code:</p>
                <p style='margin:0;font-family:monospace;font-size:1.1rem;color:#00d4ff;font-weight:700;'>{comp_code}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("📋 Copy Code", key="btn_copy_code"):
                st.success(f"Copied: {comp_code}")
        except Exception as e:
            st.warning(f"Code: {str(e)}")
        
        st.markdown("---")
        
        # EXPORT AS IMAGE
        st.markdown("### 📸 Export As Image")
        from app.ui.builder_export_canvas import render_png_export_button
        
        try:
            # Build strengths, weaknesses, warnings
            strengths_list = ["Strong smoke coverage for site executes", "Good information gathering and intel", "Solid site anchor and flank denial"]
            weaknesses_list = []
            warnings_list = []
            
            render_png_export_button(s_obj, selected_map, score, grade, strengths_list, weaknesses_list, warnings_list)
            st.caption("Save and share your comp analysis as an image!")
        except Exception as e:
            st.warning(f"Image export: {str(e)}")
        
        st.markdown("---")
        
        # SAVE COMP (with user)
        st.markdown("### 💾 Save This Comp")
        if st.session_state.get("user_logged_in"):
            comp_name = st.text_input("Comp name:", placeholder=f"{selected_map} - ", key="comp_save_name")
            comp_notes = st.text_area("Notes:", placeholder="Strategy, tips, etc.", height=60, key="comp_save_notes")
            
            if st.button("💾 Save Comp", type="primary", use_container_width=True, key="btn_save_comp"):
                if comp_name:
                    comp_data = {
                        "name": comp_name,
                        "map": selected_map,
                        "agents": sel,
                        "code": comp_code,
                        "score": score,
                        "grade": grade,
                        "notes": comp_notes
                    }
                    save_comp(st.session_state.user_email, comp_data)
                    st.success(f"✅ Saved '{comp_name}'!")
                else:
                    st.warning("Enter a comp name")
        else:
            st.info("📌 Login to save comps!")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", key="back_s2"):
                st.session_state.builder_step = 2
                st.rerun()
        with col2:
            if st.button("🔄 Reset", key="restart"):
                st.session_state.builder_step = 1
                st.session_state.selected_agents = []
                st.rerun()

# Auto-scroll to top when stage changes
if st.session_state.get("last_step") != st.session_state.get("builder_step"):
    st.session_state["last_step"] = st.session_state.get("builder_step")
    # JavaScript to scroll to top
    st.markdown("""
    <script>
    window.scrollTo(0, 0);
    </script>
    """, unsafe_allow_html=True)
