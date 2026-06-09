"""
Builder — multi-step: Map → Pick Agents → Analysis.
All image blocks use st.components.v1.html (Streamlit strips <img> in st.markdown).
SVG portraits are local data URIs — no external API needed.
"""
import json, sys, os, re
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from assets.agent_portraits import AGENT_PORTRAITS, MAP_SPLASHES, AGENT_ICONS
from app.services.data_loader import load_agents, load_maps, load_rules, save_comp, get_map_by_name
from app.services.scoring import score_comp, get_score_grade, get_score_label
from app.services.validator import validate_comp
from app.services.recommender import recommend_agents
from app.models.comp import Comp

RC = {"Duelist":"#ff4d6d","Controller":"#7c3aed","Initiator":"#0ea5e9","Sentinel":"#10b981"}
RI = {"Duelist":"⚔️","Controller":"💨","Initiator":"🔍","Sentinel":"🛡️"}

def _wr(src):
    m = re.search(r'(\d+)%\s*WR', src)
    return float(m.group(1)) if m else 55.0

def _tier(wr):
    if wr>=96: return "S","#ffd700"
    if wr>=86: return "A","#00ff9f"
    if wr>=76: return "B","#0ea5e9"
    if wr>=61: return "C","#f59e0b"
    return "D","#ff4d6d"

def _similar(sel, presets, threshold=3):
    s = set(sel); best = None; best_n = 0
    for p in presets:
        n = len(s & set(p["agents"]))
        if n >= threshold and n > best_n: best, best_n = p, n
    return best

def _step_bar(current):
    steps = [("1","Select Map"),("2","Pick Agents"),("3","Analysis")]
    h = '<div style="display:flex;align-items:center;justify-content:center;padding:10px 0 6px;">'
    for i,(num,label) in enumerate(steps):
        active=(i+1)==current; done=(i+1)<current
        if active:   bg="#00d4ff22";bc="#00d4ff";fc="#00d4ff";nb="#00d4ff";nc="#000"
        elif done:   bg="#10b98118";bc="#10b98166";fc="#10b981";nb="#10b981";nc="#000"
        else:        bg="transparent";bc="#1a2f4a";fc="#334155";nb="#1a2f4a11";nc="#334155"
        sym="✓" if done else num
        h+=(f'<div style="display:flex;align-items:center;gap:7px;padding:7px 16px;border-radius:25px;'
            f'background:{bg};border:1px solid {bc};">'
            f'<div style="width:20px;height:20px;border-radius:50%;background:{nb};color:{nc};'
            f'display:flex;align-items:center;justify-content:center;font-size:0.7rem;font-weight:800;">{sym}</div>'
            f'<span style="font-size:0.8rem;font-weight:600;color:{fc};">{label}</span></div>')
        if i<2:
            lc="#10b981" if done else "#1a2f4a"
            h+=f'<div style="width:32px;height:2px;background:{lc};"></div>'
    h+="</div>"
    st.markdown(h, unsafe_allow_html=True)

def _html(content, h):
    """Wrap content in a minimal full-page iframe."""
    full = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
    html,body{{margin:0;padding:0;background:transparent;font-family:'Segoe UI',Arial,sans-serif;
               -webkit-font-smoothing:antialiased;}}
    img{{display:block;}}
    </style></head><body>{content}</body></html>"""
    components.html(full, height=h, scrolling=False)

# ── PRESETS ────────────────────────────────────────────────────────────────────
MAP_PRESETS = {
    "Ascent":[
        {"name":"G2 — Waylay/Tejo","agents":["KAY/O","Omen","Tejo","Vyse","Waylay"],"description":"G2's 5W-1L. Waylay entry + Tejo suppress + Vyse zone control.","source":"G2 Esports · VCT Americas 2025 · 83% WR"},
        {"name":"FNATIC — Chamber/Yoru","agents":["Chamber","Omen","Sova","Vyse","Yoru"],"description":"FNC 5W-2L. Yoru decoys + Chamber OP on mid + Vyse arc rose.","source":"FNATIC · VCT EMEA 2025 · 71% WR"},
        {"name":"NaVi — Fade/KAY/O","agents":["Cypher","Fade","Jett","KAY/O","Omen"],"description":"NaVi 4W-2L. Double init with Cypher B-side lock.","source":"Natus Vincere · VCT EMEA 2025 · 67% WR"},
        {"name":"Leviatán — Double Sentinel","agents":["Cypher","Deadlock","Jett","Omen","Sova"],"description":"LEV 3W-2L. Double sentinel locks sites while Jett+Sova take mid.","source":"Leviatán · VCT Americas 2025 · 60% WR"},
        {"name":"Gen.G — KJ Standard (148W)","agents":["Jett","KAY/O","Killjoy","Omen","Sova"],"description":"Gen.G's most-played Ascent — 148 wins in VCT.","source":"Gen.G · VCT Pacific 2025 · 53% WR"},
    ],
    "Abyss":[
        {"name":"G2 — Chamber/Yoru","agents":["Astra","Breach","Chamber","Sova","Yoru"],"description":"G2 4W-1L. Yoru TP flanks + Chamber OP ledge holds on Abyss.","source":"G2 Esports · VCT Americas 2025 · 80% WR"},
        {"name":"DRX — Cypher/KAY/O","agents":["Cypher","Jett","KAY/O","Omen","Sova"],"description":"DRX 15W-8L. Most proven Abyss comp at pro level.","source":"Kiwoom DRX · VCT Pacific 2025 · 65% WR"},
        {"name":"DFM — Astra Global","agents":["Astra","Jett","KAY/O","Omen","Sova"],"description":"DFM Abyss (8W-8L). Astra global stars cover wide site lanes.","source":"DetonatioN FocusMe · VCT Pacific 2025 · 50% WR"},
        {"name":"MIBR — Astra/Cypher","agents":["Astra","Cypher","Jett","KAY/O","Sova"],"description":"MIBR 6W-6L. Full site coverage on Abyss open layout.","source":"MIBR · VCT Americas 2025 · 50% WR"},
        {"name":"Heretics — Gekko/Cypher","agents":["Astra","Cypher","Gekko","Jett","Sova"],"description":"TH 2W-3L. Gekko plant + Cypher flank cover on Abyss.","source":"Team Heretics · VCT EMEA 2025 · 40% WR"},
    ],
    "Bind":[
        {"name":"PRX — Harbor/Reyna","agents":["Brimstone","Harbor","Raze","Reyna","Skye"],"description":"PRX 5W-1L. Harbor Cove plants + Reyna self-sustain entry.","source":"Paper Rex · VCT Pacific 2025 · 83% WR"},
        {"name":"100T — Viper/Yoru","agents":["Brimstone","Fade","Raze","Viper","Yoru"],"description":"100T 5W-1L. Yoru TPs + Bind teleporters = max mind games.","source":"100 Thieves · VCT Americas 2025 · 83% WR"},
        {"name":"EDG — Harbor/Gekko","agents":["Gekko","Harbor","Jett","Skye","Viper"],"description":"EDG 5W-2L. Harbor Cove shields + Gekko Wingman guaranteed plants.","source":"EDward Gaming · VCT China 2025 · 71% WR"},
        {"name":"BLG — Cypher/Skye (28W)","agents":["Brimstone","Cypher","Raze","Skye","Viper"],"description":"BLG 28W-18L most wins. Proven double-smoke standard on Bind.","source":"Bilibili Gaming · VCT China 2025 · 61% WR"},
        {"name":"G2 — Gekko/Fade (29W)","agents":["Brimstone","Fade","Gekko","Raze","Viper"],"description":"G2 29W-23W highest wins. Fade recon + Gekko plant utility.","source":"G2 Esports · VCT Americas 2025 · 56% WR"},
    ],
    "Breeze":[
        {"name":"G2 — Astra/Cypher/Yoru","agents":["Astra","Cypher","Sova","Viper","Yoru"],"description":"G2 5W-1L. Yoru TP flanks on open layout + Cypher one-way mid.","source":"G2 Esports · VCT Americas 2025 · 83% WR"},
        {"name":"NaVi — Cypher/Omen/Yoru","agents":["Cypher","Omen","Sova","Viper","Yoru"],"description":"NaVi 3W-2L. Yoru through mid cave + Cypher one-way B.","source":"Natus Vincere · VCT EMEA 2025 · 60% WR"},
        {"name":"FNATIC — KAY/O Suppress","agents":["Cypher","KAY/O","Sova","Viper","Yoru"],"description":"FNC 6W-5L. KAY/O suppresses defender util mid-rotation.","source":"FNATIC · VCT EMEA 2025 · 55% WR"},
        {"name":"FPX — Astra/Jett/Yoru","agents":["Astra","Jett","Sova","Viper","Yoru"],"description":"FPX 6W-5L. Jett OP long + Yoru fakes force bad rotations.","source":"FunPlus Phoenix · VCT China 2025 · 55% WR"},
        {"name":"DRG — KAY/O Standard (24W)","agents":["Cypher","Jett","KAY/O","Sova","Viper"],"description":"DRG 24W-22L most wins. KAY/O suppression dominates.","source":"Dragon Ranger Gaming · VCT China 2025 · 52% WR"},
    ],
    "Fracture":[
        {"name":"DRX — Breach/Neon/Fade","agents":["Breach","Brimstone","Fade","Killjoy","Neon"],"description":"DRX 6W-1L (86% WR). Neon speed + Breach stun + Fade recon.","source":"Kiwoom DRX · VCT Pacific 2025 · 86% WR"},
        {"name":"Cloud9 — Breach/Skye/Raze","agents":["Breach","Brimstone","Killjoy","Raze","Skye"],"description":"C9 6W-2L. Raze satchels + Breach stun + Skye flash.","source":"Cloud9 · VCT Americas 2025 · 75% WR"},
        {"name":"T1 — Breach/Tejo/Vyse","agents":["Breach","Brimstone","Raze","Tejo","Vyse"],"description":"T1 6W-3L. Tejo suppress + Vyse zone + Breach stuns.","source":"T1 · VCT Pacific 2025 · 67% WR"},
        {"name":"Team Liquid — Viper/Cypher","agents":["Cypher","Omen","Raze","Skye","Viper"],"description":"TL 3W-2L. Viper wall cuts Fracture H-shape.","source":"Team Liquid · VCT EMEA 2025 · 60% WR"},
        {"name":"BLG — Tejo/Cypher (18W)","agents":["Breach","Brimstone","Cypher","Neon","Tejo"],"description":"BLG 18W-13L most wins. Tejo + Breach stun chain dominates.","source":"Bilibili Gaming · VCT China 2025 · 58% WR"},
    ],
    "Haven":[
        {"name":"FNATIC — Astra/Breach/Jett","agents":["Astra","Breach","Jett","Killjoy","Sova"],"description":"FNC 21W-10L (68% WR). Astra global smokes all 3 Haven sites.","source":"FNATIC · VCT EMEA 2025 · 68% WR"},
        {"name":"RRQ — Yoru/Neon","agents":["Cypher","Neon","Omen","Sova","Yoru"],"description":"RRQ 4W-2L. Yoru flanks cause rotation chaos across 3 sites.","source":"Rex Regum Qeon · VCT Pacific 2025 · 67% WR"},
        {"name":"Gen.G — Neon/Viper","agents":["Killjoy","Neon","Omen","Sova","Viper"],"description":"Gen.G 17W-9L (65% WR). Viper cuts C-long, Neon fast-pushes.","source":"Gen.G · VCT Pacific 2025 · 65% WR"},
        {"name":"FNATIC — Cypher/Iso/Yoru (30W)","agents":["Cypher","Iso","Omen","Sova","Yoru"],"description":"FNC 30W-18L most-wins variant. Yoru C-long + Cypher B.","source":"FNATIC · VCT EMEA 2025 · 62% WR"},
        {"name":"Sentinels — Breach/Cypher","agents":["Breach","Cypher","Neon","Omen","Sova"],"description":"SEN 23W-16L. Breach executes any site — Cypher locks B flank.","source":"Sentinels · VCT Americas 2025 · 59% WR"},
    ],
    "Icebox":[
        {"name":"Global Esports — Harbor/Skye","agents":["Harbor","Jett","Killjoy","Skye","Viper"],"description":"GE 5W-1L. Harbor High Tide covers B while Viper wall cuts mid.","source":"Global Esports · VCT Pacific 2025 · 83% WR"},
        {"name":"FPX — Clove/KAY/O","agents":["Clove","Jett","KAY/O","Killjoy","Viper"],"description":"FPX 4W-1L. Clove smokes + KAY/O suppresses B-tube defenders.","source":"FunPlus Phoenix · VCT China 2025 · 80% WR"},
        {"name":"FNATIC — Sage Wall (27W)","agents":["Jett","Killjoy","Sage","Sova","Viper"],"description":"FNC 27W-13L (68% WR). Sage wall blocks B zipline — EMEA dominant.","source":"FNATIC · VCT EMEA 2025 · 68% WR"},
        {"name":"Paper Rex — KAY/O/Sage","agents":["Jett","KAY/O","Killjoy","Sage","Viper"],"description":"PRX 8W-4L. KAY/O suppresses then Sage wall blocks retreat.","source":"Paper Rex · VCT Pacific 2025 · 67% WR"},
        {"name":"Leviatán — Harbor/Sova (45W)","agents":["Harbor","Jett","Killjoy","Sova","Viper"],"description":"LEV 45W-36L most wins. Harbor + Viper dominate B-site.","source":"Leviatán · VCT Americas 2025 · 56% WR"},
    ],
    "Lotus":[
        {"name":"Evil Geniuses — PERFECT (100% WR)","agents":["Astra","Killjoy","Raze","Skye","Viper"],"description":"EG 5W-0L (100% WR). Best Lotus comp in VCT history.","source":"Evil Geniuses · VCT Americas 2025 · 100% WR"},
        {"name":"FNATIC — Astra/Fade/Viper","agents":["Astra","Fade","Killjoy","Raze","Viper"],"description":"FNC 15W-5L (75% WR). Fade clears corridors for Astra-smoked executes.","source":"FNATIC · VCT EMEA 2025 · 75% WR"},
        {"name":"Paper Rex — Fade/Omen/Yoru","agents":["Fade","Omen","Raze","Vyse","Yoru"],"description":"PRX 13W-5L (72% WR). Yoru decoys panic defenders at doors.","source":"Paper Rex · VCT Pacific 2025 · 72% WR"},
        {"name":"Cloud9 — Neon/Skye/Viper","agents":["Killjoy","Neon","Omen","Skye","Viper"],"description":"C9 14W-6L (70% WR). Neon speed forces early commitment.","source":"Cloud9 · VCT Americas 2025 · 70% WR"},
        {"name":"Gen.G — Iron Standard (114W)","agents":["Fade","Killjoy","Omen","Raze","Viper"],"description":"Gen.G's 114 wins in VCT. Most reliable Lotus comp globally.","source":"Gen.G · VCT Pacific 2025 · 55% WR"},
    ],
    "Pearl":[
        {"name":"Team Liquid — Phoenix/Skye","agents":["Astra","Jett","Killjoy","Phoenix","Skye"],"description":"TL 9W-2L (82% WR). Phoenix curved flash through Pearl's tight B.","source":"Team Liquid · VCT EMEA 2025 · 82% WR"},
        {"name":"Gen.G — KAY/O/Astra","agents":["Astra","Jett","KAY/O","Killjoy","Viper"],"description":"Gen.G Pearl. KAY/O suppresses mid-rotate + Astra smokes both sites.","source":"Gen.G · VCT Pacific 2025 · 63% WR"},
        {"name":"DRX — Fade/Chamber","agents":["Chamber","Fade","Jett","Killjoy","Viper"],"description":"DRX Pearl. Chamber OP mid + Fade prowlers clear B.","source":"Kiwoom DRX · VCT Pacific 2025 · 60% WR"},
        {"name":"FNATIC — Viper/Sage Mid Wall","agents":["Jett","Killjoy","Sage","Sova","Viper"],"description":"FNC Pearl. Viper wall mid + Sage slow-orb B site.","source":"FNATIC · VCT EMEA 2025 · 58% WR"},
        {"name":"Sentinels — Breach/Cypher","agents":["Breach","Cypher","Jett","Omen","Sova"],"description":"SEN Pearl. Breach stuns through B-link + Cypher one-ways.","source":"Sentinels · VCT Americas 2025 · 55% WR"},
    ],
    "Split":[
        {"name":"LOUD — Astra/Breach/Raze","agents":["Astra","Breach","Killjoy","Raze","Skye"],"description":"LOUD 6W-1L (86% WR). Astra + Breach stun through Split walls.","source":"LOUD · VCT Americas 2025 · 86% WR"},
        {"name":"Team Liquid — Cypher/Sage","agents":["Cypher","Jett","Omen","Sage","Skye"],"description":"TL 8W-2L (80% WR). Sage wall blocks ropes + Cypher punishes.","source":"Team Liquid · VCT EMEA 2025 · 80% WR"},
        {"name":"Team Liquid — Astra/Fade/Yoru","agents":["Astra","Fade","Raze","Viper","Yoru"],"description":"TL 15W-5L (75% WR). Yoru decoys in Split's tight corridors.","source":"Team Liquid · VCT EMEA 2025 · 75% WR"},
        {"name":"G2 — Breach/Cypher/Viper","agents":["Breach","Cypher","Omen","Raze","Viper"],"description":"G2 4W-2L (67% WR). Breach + Viper + Cypher = Split fortress.","source":"G2 Esports · VCT Americas 2025 · 67% WR"},
        {"name":"Sentinels — Cypher/Omen/Raze (38W)","agents":["Cypher","Omen","Raze","Skye","Viper"],"description":"SEN 38W-30L. Standard Viper + Cypher one-ways dominance.","source":"Sentinels · VCT Americas 2025 · 56% WR"},
    ],
    "Sunset":[
        {"name":"Paper Rex — Gekko/Sage/Viper","agents":["Gekko","KAY/O","Omen","Sage","Viper"],"description":"PRX 4W-1L (80% WR). Sage wall blocks B-link + Gekko plants spike.","source":"Paper Rex · VCT Pacific 2025 · 80% WR"},
        {"name":"Team Heretics — Cypher/KAY/O","agents":["Cypher","KAY/O","Omen","Raze","Sova"],"description":"TH 9W-4L (69% WR). KAY/O suppresses B-link, Cypher locks A.","source":"Team Heretics · VCT EMEA 2025 · 69% WR"},
        {"name":"Paper Rex — Breach/Gekko/Sage","agents":["Breach","Gekko","Omen","Raze","Sage"],"description":"PRX 9W-4L (69% WR) variant. Breach stuns door + Gekko plant.","source":"Paper Rex · VCT Pacific 2025 · 69% WR"},
        {"name":"Sentinels — Breach/Cypher/Fade","agents":["Breach","Cypher","Fade","Neon","Omen"],"description":"SEN 8W-4L (67% WR). Neon speed + Fade haunt + Breach stun.","source":"Sentinels · VCT Americas 2025 · 67% WR"},
        {"name":"EDG — Gekko/Cypher/Viper","agents":["Cypher","Gekko","Omen","Raze","Viper"],"description":"EDG 6W-3L (67% WR). Viper wall B-link + Gekko plant assist.","source":"EDward Gaming · VCT China 2025 · 67% WR"},
    ],
}

def render():
    agents_list = load_agents()
    maps_list   = load_maps()
    rules       = load_rules()
    map_names   = [m["name"] for m in maps_list]

    if "selected_agents" not in st.session_state: st.session_state["selected_agents"]=[]
    if "builder_step"    not in st.session_state: st.session_state["builder_step"]=1
    if "builder_map"     not in st.session_state: st.session_state["builder_map"]=map_names[0]

    step         = st.session_state["builder_step"]
    selected_map = st.session_state["builder_map"]

    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">⚙️ Comp Builder</h1>
        <p class="page-subtitle">Pick a map · choose agents · analyze your comp</p>
    </div>""", unsafe_allow_html=True)

    _step_bar(step)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ══ STEP 1 — MAP ══════════════════════════════════════════════════════════
    if step == 1:
        st.markdown('<div style="font-size:1rem;font-weight:700;color:#e2e8f0;margin-bottom:12px;">🗺️ Choose Your Map</div>', unsafe_allow_html=True)

        for row_start in range(0, len(maps_list), 4):
            row_maps = maps_list[row_start:row_start+4]
            cols = st.columns(4)
            for ci, m in enumerate(row_maps):
                chosen     = m["name"] == selected_map
                bias       = "⚔️ Attack" if m.get("attack_sided") else ("🛡️ Defense" if m.get("defense_sided") else "⚖️ Balanced")
                bc_color   = "#ff4d6d" if m.get("attack_sided") else ("#10b981" if m.get("defense_sided") else "#0ea5e9")
                border_col = "#00d4ff" if chosen else "#1a2f4a"
                bg         = "linear-gradient(160deg,#132240,#0d1b2e)" if chosen else "#0f1e35"
                glow       = "box-shadow:0 0 20px rgba(0,212,255,0.3);" if chosen else ""
                splash     = MAP_SPLASHES.get(m["name"], "")
                check_html = '<div style="position:absolute;top:8px;right:8px;width:22px;height:22px;border-radius:50%;background:#00d4ff;color:#000;display:flex;align-items:center;justify-content:center;font-size:0.65rem;font-weight:800;">✓</div>' if chosen else ""
                desc       = m.get("description","")[:60]

                with cols[ci]:
                    _html(f"""
                    <div style="border:2px solid {border_col};border-radius:12px;overflow:hidden;
                                background:{bg};{glow}position:relative;cursor:pointer;">
                        {check_html}
                        <img src="{splash}" style="width:100%;height:88px;object-fit:cover;opacity:0.75;display:block;">
                        <div style="padding:10px;text-align:center;">
                            <div style="font-size:1.3rem;margin-bottom:2px;">{m["icon"]}</div>
                            <div style="font-weight:700;font-size:0.95rem;
                                        color:{"#00d4ff" if chosen else "#e2e8f0"};">{m["name"]}</div>
                            <div style="font-size:0.62rem;color:{bc_color};font-weight:600;margin:3px 0;">
                                {bias}</div>
                            <div style="font-size:0.6rem;color:#475569;line-height:1.35;">{desc}...</div>
                        </div>
                    </div>""", 188)

                    label = f"{'✓ ' if chosen else ''}{m['name']}"
                    if st.button(label, key=f"map_{m['name']}", use_container_width=True,
                                 type="primary" if chosen else "secondary"):
                        st.session_state["builder_map"] = m["name"]
                        st.session_state["selected_agents"] = []
                        st.rerun()

        # Map info strip
        md = get_map_by_name(selected_map)
        if md:
            bias_full  = "⚔️ Attack-sided" if md.get("attack_sided") else ("🛡️ Defense-sided" if md.get("defense_sided") else "⚖️ Balanced")
            bias_color = "#ff4d6d" if md.get("attack_sided") else ("#10b981" if md.get("defense_sided") else "#0ea5e9")
            tags = "".join(f'<span style="background:rgba(0,212,255,0.08);border:1px solid rgba(0,212,255,0.2);color:#00d4ff;padding:2px 8px;border-radius:10px;font-size:0.68rem;margin:2px 3px 2px 0;display:inline-block;">{f}</span>' for f in md.get("key_features",[]))
            st.markdown(f"""
            <div style="background:#0f1e35;border:1px solid #1a2f4a;border-left:4px solid #00d4ff;
                         border-radius:10px;padding:14px 18px;margin:12px 0;">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                    <span style="font-size:1.3rem;">{md["icon"]}</span>
                    <span style="font-weight:700;font-size:1rem;color:#00d4ff;">{selected_map}</span>
                    <span style="font-size:0.7rem;padding:2px 9px;border-radius:20px;
                                 background:{bias_color}22;border:1px solid {bias_color}55;
                                 color:{bias_color};font-weight:600;">{bias_full}</span>
                </div>
                <div style="margin-bottom:8px;">{tags}</div>
                <div style="font-size:0.78rem;color:#64748b;">{md.get("notes","")}</div>
            </div>""", unsafe_allow_html=True)

        c1, c_hub, _ = st.columns([1,1,2])
        with c1:
            if st.button("Next: Pick Agents →", type="primary", use_container_width=True, key="s1next"):
                st.session_state["builder_step"] = 2
                st.session_state["active_page"] = "Orbital Hub"
                st.rerun()
        with c_hub:
            if st.button("🌐 Back to Hub", use_container_width=True, key="s1hub"):
                st.session_state["active_page"] = "Orbital Hub"
                st.rerun()

    # ══ STEP 2 — AGENT PICKER ═════════════════════════════════════════════════
    elif step == 2:
        sel   = st.session_state["selected_agents"]
        s_obj = [a for a in agents_list if a.name in sel]

        # ── Sticky CSS injected once ──────────────────────────────────────────
        st.markdown("""
        <style>
        /* Sticky selected-agents bar — freezes below the Streamlit toolbar */
        .sticky-team-bar {
            position: sticky;
            top: 3.2rem;
            z-index: 999;
            background: #020817;
            padding: 6px 0 4px;
            border-bottom: 1px solid #1a2f4a;
            margin-bottom: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

        # ── Enlarged map header ───────────────────────────────────────────────
        md = get_map_by_name(selected_map)
        splash_uri = MAP_SPLASHES.get(selected_map, "")
        bias_full  = "⚔️ Attack-sided" if md and md.get("attack_sided") else ("🛡️ Defense-sided" if md and md.get("defense_sided") else "⚖️ Balanced")
        bias_color = "#ff4d6d" if md and md.get("attack_sided") else ("#10b981" if md and md.get("defense_sided") else "#0ea5e9")
        map_icon   = md["icon"] if md else "🗺️"
        map_note   = md.get("notes","") if md else ""
        _html(f"""
        <div style="position:relative;border-radius:14px;overflow:hidden;
                    border:1px solid #1a2f4a;margin-bottom:10px;">
            <img src="{splash_uri}" style="width:100%;height:120px;object-fit:cover;
                                           opacity:0.55;display:block;">
            <div style="position:absolute;inset:0;background:linear-gradient(90deg,
                         rgba(2,8,23,0.92) 0%,rgba(2,8,23,0.6) 60%,rgba(2,8,23,0.2) 100%);
                         display:flex;align-items:center;padding:0 24px;gap:18px;">
                <div style="font-size:3rem;line-height:1;">{map_icon}</div>
                <div>
                    <div style="font-family:Rajdhani,sans-serif;font-size:2rem;font-weight:800;
                                color:#e2e8f0;letter-spacing:1px;line-height:1;">{selected_map.upper()}</div>
                    <div style="display:flex;align-items:center;gap:8px;margin-top:4px;">
                        <span style="font-size:0.72rem;padding:2px 10px;border-radius:20px;
                                     background:{bias_color}25;border:1px solid {bias_color}66;
                                     color:{bias_color};font-weight:600;">{bias_full}</span>
                        <span style="font-size:0.72rem;color:#64748b;">{map_note[:60]}...</span>
                    </div>
                </div>
            </div>
        </div>""", 130)

        # ── Sticky selected-agents freeze row ─────────────────────────────────
        # Builds a horizontal scrollable agent bar that stays visible while scrolling
        rc_counts = {"Duelist":0,"Controller":0,"Initiator":0,"Sentinel":0}
        for a in s_obj:
            if a.role in rc_counts: rc_counts[a.role]+=1
        role_pills_html = "".join(
            f'<span style="font-size:0.68rem;padding:2px 9px;border-radius:14px;'
            f'background:{RC[r]}20;border:1px solid {RC[r]}55;color:{RC[r]};margin:0 2px;">'
            f'{RI[r]} {cnt}</span>'
            for r,cnt in rc_counts.items() if cnt>0)

        # Build mini-avatar strip for the freeze row
        slots_strip = ""
        for i in range(5):
            if i < len(s_obj):
                a = s_obj[i]; c = RC.get(a.role,"#64748b")
                img = AGENT_PORTRAITS.get(a.name,"")
                slots_strip += f"""
                <div style="display:flex;flex-direction:column;align-items:center;gap:3px;
                             min-width:72px;padding:4px;">
                    <div style="position:relative;">
                        <img src="{img}" style="width:44px;height:44px;object-fit:cover;
                                                border-radius:50%;border:2px solid {c};">
                        <div style="position:absolute;bottom:-2px;right:-2px;width:14px;height:14px;
                                     border-radius:50%;background:{c};border:1.5px solid #020817;
                                     display:flex;align-items:center;justify-content:center;
                                     font-size:0.45rem;font-weight:800;color:#000;">{i+1}</div>
                    </div>
                    <div style="font-size:0.62rem;font-weight:700;color:#e2e8f0;
                                white-space:nowrap;max-width:68px;overflow:hidden;
                                text-overflow:ellipsis;">{a.name}</div>
                    <div style="font-size:0.55rem;color:{c};">{a.role[:3].upper()}</div>
                </div>"""
            else:
                slots_strip += f"""
                <div style="display:flex;flex-direction:column;align-items:center;gap:3px;
                             min-width:72px;padding:4px;">
                    <div style="width:44px;height:44px;border-radius:50%;
                                 border:1.5px dashed #1e3a5f;display:flex;
                                 align-items:center;justify-content:center;
                                 background:rgba(0,0,0,0.15);">
                        <span style="font-size:0.9rem;opacity:0.2;">+</span>
                    </div>
                    <div style="font-size:0.6rem;color:#1e3a5f;">Slot {i+1}</div>
                </div>"""

        # Comp score preview
        score_preview = ""
        if s_obj:
            raw_prev,_=score_comp(s_obj,selected_map,rules)
            gr_prev,gc_prev=get_score_grade(raw_prev)
            score_preview = f"""
            <div style="margin-left:auto;padding:0 16px;display:flex;flex-direction:column;
                         align-items:center;border-left:1px solid #1a2f4a;">
                <div style="font-size:1.6rem;font-weight:800;color:{gc_prev};
                             font-family:Rajdhani,sans-serif;line-height:1;">{raw_prev}</div>
                <div style="font-size:0.65rem;color:{gc_prev};font-weight:700;">{gr_prev}</div>
                <div style="font-size:0.55rem;color:#475569;margin-top:1px;">SCORE</div>
            </div>"""

        st.markdown('<div class="sticky-team-bar">', unsafe_allow_html=True)
        _html(f"""
        <div style="background:#0a1628;border:1px solid #1a2f4a;border-radius:10px;
                    padding:8px 12px;display:flex;align-items:center;gap:0;">
            <div style="flex-shrink:0;margin-right:12px;">
                <div style="font-size:0.62rem;color:#475569;text-transform:uppercase;
                             letter-spacing:1px;margin-bottom:2px;">Selected ({len(sel)}/5)</div>
                <div style="display:flex;gap:2px;">{role_pills_html}</div>
            </div>
            <div style="display:flex;gap:0;overflow-x:auto;flex:1;">{slots_strip}</div>
            {score_preview}
        </div>""", 82)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Presets expander ─────────────────────────────────────────────────
        with st.expander(f"📋 Pro/Meta Presets for {selected_map} — sorted by Tier", expanded=False):
            map_comps = MAP_PRESETS.get(selected_map,[])
            tiers = {"S":[],"A":[],"B":[],"C":[],"D":[]}
            for p in map_comps:
                w=_wr(p["source"]); t,_=_tier(w); tiers[t].append((w,p))
            tc_map = {"S":"#ffd700","A":"#00ff9f","B":"#0ea5e9","C":"#f59e0b","D":"#ff4d6d"}
            tl_map = {"S":"S — 96–100% WR","A":"A — 86–95% WR","B":"B — 76–85% WR","C":"C — 61–75% WR","D":"D — ≤60% WR"}
            for tk in ["S","A","B","C","D"]:
                entries = sorted(tiers[tk],key=lambda x:-x[0])
                if not entries: continue
                tc = tc_map[tk]
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:8px;margin:10px 0 5px;">
                    <div style="width:32px;height:32px;border-radius:7px;background:{tc}20;
                                border:2px solid {tc};display:flex;align-items:center;
                                justify-content:center;font-weight:800;font-size:1rem;color:{tc};">{tk}</div>
                    <span style="color:{tc};font-size:0.78rem;font-weight:600;">{tl_map[tk]}</span>
                </div>""", unsafe_allow_html=True)
                for w,p in entries:
                    valid = [n for n in p["agents"] if any(a.name==n for a in agents_list)]
                    pills = "".join(
                        f'<span style="background:{RC.get(next((a.role for a in agents_list if a.name==n),""),"#64748b")}20;'
                        f'color:{RC.get(next((a.role for a in agents_list if a.name==n),""),"#64748b")};'
                        f'border:1px solid {RC.get(next((a.role for a in agents_list if a.name==n),""),"#64748b")}44;'
                        f'padding:2px 8px;border-radius:10px;font-size:0.68rem;margin:2px;display:inline-block;">'
                        f'{AGENT_ICONS.get(n,"?")} {n}</span>' for n in valid)
                    ci2, cb2 = st.columns([4,1])
                    with ci2:
                        st.markdown(f"""
                        <div style="background:#0a1628;border:1px solid #1a2f4a;border-radius:8px;
                                    padding:10px 14px;margin:3px 0;">
                            <div style="font-weight:700;color:#e2e8f0;font-size:0.85rem;margin-bottom:3px;">{p["name"]}</div>
                            <div style="font-size:0.72rem;color:#475569;margin-bottom:5px;">{p["description"]}</div>
                            <div>{pills}</div>
                        </div>""", unsafe_allow_html=True)
                    with cb2:
                        if st.button("Apply", key=f"pre_{p['name'][:15]}", use_container_width=True):
                            st.session_state["selected_agents"]=valid[:5]; st.rerun()

        # ── Similarity alert ─────────────────────────────────────────────────
        if len(sel)>=2:
            sim = _similar(sel, MAP_PRESETS.get(selected_map,[]))
            if sim:
                wr=_wr(sim["source"]); tier_l,tc=_tier(wr)
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#7c3aed15,#00d4ff10);
                             border:1px solid #7c3aed55;border-radius:10px;
                             padding:11px 16px;margin:6px 0;display:flex;align-items:center;gap:10px;">
                    <span style="font-size:1.3rem;flex-shrink:0;">🎯</span>
                    <div>
                        <span style="font-weight:700;color:#e2e8f0;">Building close to </span>
                        <span style="color:#00d4ff;font-weight:700;">"{sim["name"]}"</span>
                        <span style="font-size:0.75rem;color:#64748b;display:block;margin-top:2px;">
                            {sim["description"]} · <span style="color:{tc};font-weight:700;">Tier {tier_l} · {wr:.0f}% WR</span>
                        </span>
                    </div>
                </div>""", unsafe_allow_html=True)

        # ── Team slots ───────────────────────────────────────────────────────
        rc = {"Duelist":0,"Controller":0,"Initiator":0,"Sentinel":0}
        for a in s_obj:
            if a.role in rc: rc[a.role]+=1
        role_pills = "".join(
            f'<span style="font-size:0.7rem;padding:2px 9px;border-radius:15px;'
            f'background:{RC[r]}20;border:1px solid {RC[r]}55;color:{RC[r]};margin:2px;">'
            f'{RI[r]} {cnt}</span>'
            for r,cnt in rc.items() if cnt>0)

        st.markdown(f"""
        <div style="background:#0f1e35;border:1px solid #1a2f4a;border-radius:12px;
                    padding:12px 16px 8px;margin-bottom:4px;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
                <div style="font-weight:700;font-size:0.95rem;color:#e2e8f0;">👥 Team — {len(sel)}/5</div>
                <div>{role_pills}</div>
            </div>""", unsafe_allow_html=True)

        slot_cols = st.columns(5)
        for i in range(5):
            with slot_cols[i]:
                if i < len(s_obj):
                    a=s_obj[i]; c=RC.get(a.role,"#64748b")
                    img=AGENT_PORTRAITS.get(a.name,""); fit=a.fits_map(selected_map)
                    _html(f"""
                    <div style="border:2px solid {c};border-radius:10px;padding:10px 6px;
                                text-align:center;background:linear-gradient(160deg,{c}20,{c}08);
                                position:relative;">
                        <div style="position:absolute;top:4px;right:4px;font-size:0.65rem;">
                            {"✅" if fit else "⚠️"}</div>
                        <img src="{img}" style="width:54px;height:54px;object-fit:cover;
                                              border-radius:50%;border:2px solid {c};
                                              display:block;margin:0 auto 5px;">
                        <div style="font-weight:700;font-size:0.82rem;color:#e2e8f0;
                                    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{a.name}</div>
                        <div style="font-size:0.62rem;color:{c};">{a.role}</div>
                    </div>""", 108)
                    if st.button("✕ Remove", key=f"rem_{i}", use_container_width=True):
                        cur=list(st.session_state["selected_agents"]); cur.remove(a.name)
                        st.session_state["selected_agents"]=cur; st.rerun()
                else:
                    _html(f"""
                    <div style="border:1px dashed #1e3a5f;border-radius:10px;padding:20px 6px;
                                text-align:center;background:rgba(0,0,0,0.08);">
                        <div style="font-size:1rem;opacity:0.15;">👤</div>
                        <div style="font-size:0.65rem;color:#1e3a5f;margin-top:5px;">Slot {i+1}</div>
                    </div>""", 80)

        st.markdown("</div>", unsafe_allow_html=True)

        c1,c2,c3 = st.columns([1,2,1])
        with c1:
            if sel and st.button("🗑️ Clear All", key="clr"):
                st.session_state["selected_agents"]=[]; st.rerun()
        with c2:
            if sel and st.button("View Analysis →", type="primary", use_container_width=True, key="to_s3"):
                st.session_state["builder_step"]=3
                st.session_state["active_page"] = "Orbital Hub"
                st.rerun()
        with c3:
            if st.button("🌐 Hub", use_container_width=True, key="s2hub"):
                st.session_state["active_page"] = "Orbital Hub"
                st.rerun()

        # ── Live stats ───────────────────────────────────────────────────────
        if s_obj:
            raw,bdwn=score_comp(s_obj,selected_map,rules)
            gr,gc=get_score_grade(raw); lb=get_score_label(raw)
            st.markdown('<div style="font-weight:700;color:#e2e8f0;margin:14px 0 8px;">📊 Live Comp Stats</div>', unsafe_allow_html=True)
            sc=st.columns(4)
            for col,(t,v,clr,sub) in zip(sc,[
                ("Score",f"{raw}/100",gc,f"Grade {gr}"),
                ("Map Fit",f"{sum(1 for a in s_obj if a.fits_map(selected_map))}/{len(s_obj)}","#0ea5e9","on-meta"),
                ("Roles",f"{len(set(a.role for a in s_obj))}/4","#10b981","covered"),
                ("Slots",f"{5-len(s_obj)}","#f59e0b","remaining"),
            ]):
                with col:
                    st.markdown(f"""
                    <div style="background:#0f1e35;border:1px solid #1a2f4a;border-radius:10px;
                                padding:11px;text-align:center;border-top:3px solid {clr};">
                        <div style="font-size:0.65rem;color:#475569;text-transform:uppercase;letter-spacing:1px;">{t}</div>
                        <div style="font-size:1.4rem;font-weight:800;color:{clr};font-family:Rajdhani,sans-serif;">{v}</div>
                        <div style="font-size:0.62rem;color:#334155;">{sub}</div>
                    </div>""", unsafe_allow_html=True)

            # Per-agent stat rows
            st.markdown(f'<div style="font-size:0.75rem;color:#475569;text-transform:uppercase;letter-spacing:1px;margin:12px 0 6px;">Agent Details on {selected_map}</div>', unsafe_allow_html=True)
            for agent in s_obj:
                clr=RC.get(agent.role,"#64748b"); img=AGENT_PORTRAITS.get(agent.name,"")
                fits=agent.fits_map(selected_map)
                tags="".join(f'<span style="background:rgba(0,212,255,0.08);border:1px solid rgba(0,212,255,0.2);color:#00d4ff;padding:1px 7px;border-radius:10px;font-size:0.65rem;margin:2px;display:inline-block;">{t}</span>' for t in agent.synergy_tags[:4])
                utils="".join(f'<span style="background:#0a1628;border:1px solid #1a2f4a;border-radius:4px;padding:1px 6px;font-size:0.62rem;color:#64748b;margin:2px;display:inline-block;">{u}</span>' for u in agent.utility[:4])
                _html(f"""
                <div style="background:#0a1628;border:1px solid #1a2f4a;border-radius:10px;
                            padding:10px 14px;display:flex;align-items:center;gap:12px;">
                    <img src="{img}" style="width:46px;height:46px;object-fit:cover;border-radius:50%;
                                           border:2px solid {clr};flex-shrink:0;">
                    <div style="flex:1;min-width:0;">
                        <div style="display:flex;align-items:center;gap:6px;margin-bottom:5px;flex-wrap:wrap;">
                            <span style="font-weight:700;color:#e2e8f0;font-size:0.88rem;">{agent.name}</span>
                            <span style="font-size:0.63rem;padding:1px 7px;border-radius:10px;
                                         background:{clr}20;border:1px solid {clr}44;color:{clr};">{agent.role}</span>
                            <span style="font-size:0.68rem;">{"✅ Meta" if fits else "⚠️ Off-meta"}</span>
                        </div>
                        <div style="margin-bottom:4px;line-height:1.6;">{tags}</div>
                        <div style="line-height:1.6;">{utils}</div>
                    </div>
                </div>""", 90)

        # ── Synergy finder ───────────────────────────────────────────────────
        recs = recommend_agents(s_obj, agents_list, selected_map, rules)
        if recs:
            st.markdown('<div style="font-weight:700;color:#e2e8f0;margin:14px 0 8px;">🔗 Synergy Finder — Suggested Picks</div>', unsafe_allow_html=True)
            rcols = st.columns(min(len(recs),3))
            for i,rec in enumerate(recs):
                ag=rec["agent"]; c=RC.get(ag.role,"#64748b")
                img=AGENT_PORTRAITS.get(ag.name,"")
                prio=rec.get("priority","medium")
                badge_c="#ff4d6d" if prio=="high" else "#0ea5e9"
                badge_l="HIGH PRIORITY" if prio=="high" else "SUGGESTED"
                with rcols[i]:
                    _html(f"""
                    <div style="background:#0a1628;border:1px solid {c}44;border-left:3px solid {c};
                                border-radius:10px;padding:12px;">
                        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;flex-wrap:wrap;">
                            <img src="{img}" style="width:38px;height:38px;object-fit:cover;
                                                    border-radius:50%;border:2px solid {c};flex-shrink:0;">
                            <div style="flex:1;min-width:0;">
                                <div style="font-weight:700;color:#e2e8f0;font-size:0.85rem;">{ag.name}</div>
                                <div style="font-size:0.65rem;color:{c};">{RI.get(ag.role,"")} {ag.role}</div>
                            </div>
                            <span style="font-size:0.6rem;padding:1px 7px;border-radius:10px;
                                          background:{badge_c}20;border:1px solid {badge_c}44;
                                          color:{badge_c};white-space:nowrap;">{badge_l}</span>
                        </div>
                        <div style="font-size:0.76rem;color:#94a3b8;line-height:1.5;">{rec["reason"]}</div>
                    </div>""", 116)
                    if st.button(f"+ Add {ag.name}", key=f"rec_{ag.name}", use_container_width=True,
                                 disabled=len(sel)>=5):
                        cur=list(st.session_state["selected_agents"])
                        if ag.name not in cur and len(cur)<5:
                            cur.append(ag.name); st.session_state["selected_agents"]=cur; st.rerun()

        # ── Agent picker grid ────────────────────────────────────────────────
        st.markdown('<div style="font-weight:700;color:#e2e8f0;margin:16px 0 6px;font-size:1rem;">🎮 Pick Agents by Role <span style="font-size:0.7rem;color:#334155;font-weight:400;margin-left:8px;">click to add · click again to remove · max 5</span></div>', unsafe_allow_html=True)

        for role in ["Duelist","Controller","Initiator","Sentinel"]:
            role_agents=[a for a in agents_list if a.role==role]
            color=RC[role]
            st.markdown(f"""
            <div style="border-left:4px solid {color};padding:5px 12px;margin:10px 0 6px;
                         background:rgba(0,0,0,0.18);border-radius:0 6px 6px 0;">
                <span style="color:{color};font-weight:700;">{RI[role]} {role}s</span>
                <span style="color:#334155;font-size:0.7rem;margin-left:5px;">({len(role_agents)})</span>
            </div>""", unsafe_allow_html=True)

            cols=st.columns(len(role_agents))
            for i,agent in enumerate(role_agents):
                is_sel=agent.name in st.session_state["selected_agents"]
                fits=agent.fits_map(selected_map)
                locked=len(sel)>=5 and not is_sel
                img=AGENT_PORTRAITS.get(agent.name,"")
                border=f"2px solid {color}" if is_sel else "1px solid #1a2f4a"
                bg=f"linear-gradient(160deg,{color}25,{color}08)" if is_sel else "#0f1e35"
                op="0.3" if locked else "1"
                glow=f"box-shadow:0 0 16px {color}55;" if is_sel else ""
                fit_dot_c="#10b981" if fits else "#f59e0b"
                chk_html=f'<div style="position:absolute;top:3px;right:3px;width:16px;height:16px;border-radius:50%;background:{color};color:#000;display:flex;align-items:center;justify-content:center;font-size:0.55rem;font-weight:800;">✓</div>' if is_sel else ""

                with cols[i]:
                    _html(f"""
                    <div style="border:{border};background:{bg};opacity:{op};{glow}
                                border-radius:10px;padding:8px 4px 6px;text-align:center;
                                position:relative;">
                        {chk_html}
                        <div style="position:absolute;top:5px;left:5px;width:7px;height:7px;
                                     border-radius:50%;background:{fit_dot_c};"></div>
                        <img src="{img}" style="width:62px;height:62px;object-fit:cover;
                                               border-radius:50%;border:2px solid {color};
                                               display:block;margin:4px auto;">
                        <div style="font-weight:700;font-size:0.76rem;color:{"#e2e8f0" if not locked else "#334155"};
                                    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
                                    padding:0 4px;margin-top:4px;">{agent.name}</div>
                    </div>""", 102)
                    lbl="✓ Remove" if is_sel else "Add"
                    if st.button(lbl, key=f"pick_{agent.name}", use_container_width=True, disabled=locked):
                        cur=list(st.session_state["selected_agents"])
                        if agent.name in cur: cur.remove(agent.name)
                        elif len(cur)<5: cur.append(agent.name)
                        st.session_state["selected_agents"]=cur; st.rerun()

        cb,_=st.columns([1,4])
        with cb:
            if st.button("← Back to Map",key="bk_map"):
                st.session_state["builder_step"]=1; st.rerun()

    # ══ STEP 3 — ANALYSIS ═════════════════════════════════════════════════════
    elif step == 3:
        sel  =st.session_state["selected_agents"]
        s_obj=[a for a in agents_list if a.name in sel]
        if not s_obj:
            st.warning("No agents selected."); 
            if st.button("← Back"): st.session_state["builder_step"]=2; st.rerun()
            return

        raw,bdwn=score_comp(s_obj,selected_map,rules)
        gr,gc=get_score_grade(raw); lb=get_score_label(raw)
        warns,strs,weaks=validate_comp(s_obj,selected_map,rules)

        # Similarity alert
        sim=_similar(sel,MAP_PRESETS.get(selected_map,[]))
        if sim:
            wr=_wr(sim["source"]); tl,tc=_tier(wr)
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#7c3aed15,#00d4ff10);border:1px solid #7c3aed55;
                         border-radius:10px;padding:12px 16px;margin-bottom:10px;
                         display:flex;align-items:center;gap:10px;">
                <span style="font-size:1.3rem;">🎯</span>
                <div>
                    <span style="font-weight:700;color:#e2e8f0;">Comp similar to </span>
                    <span style="color:#00d4ff;font-weight:700;">"{sim["name"]}"</span>
                    <span style="font-size:0.75rem;color:#64748b;display:block;margin-top:2px;">
                        {sim["description"]} · <span style="color:{tc};font-weight:700;">Tier {tl} · {wr:.0f}% WR</span>
                    </span>
                </div>
            </div>""", unsafe_allow_html=True)

        # Team visual
        st.markdown(f'<div style="font-weight:700;color:#e2e8f0;margin-bottom:8px;font-size:0.95rem;">🗺️ {selected_map} · 👥 Final Team</div>', unsafe_allow_html=True)
        tcols=st.columns(5)
        for i in range(5):
            with tcols[i]:
                if i<len(s_obj):
                    ag=s_obj[i]; c=RC.get(ag.role,"#64748b")
                    img=AGENT_PORTRAITS.get(ag.name,""); fit=ag.fits_map(selected_map)
                    _html(f"""
                    <div style="text-align:center;border:2px solid {c};border-radius:12px;
                                padding:12px 6px;background:linear-gradient(160deg,{c}20,{c}08);">
                        <img src="{img}" style="width:68px;height:68px;object-fit:cover;
                                               border-radius:50%;border:3px solid {c};
                                               display:block;margin:0 auto 6px;">
                        <div style="font-weight:700;color:#e2e8f0;font-size:0.88rem;
                                    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{ag.name}</div>
                        <div style="font-size:0.63rem;color:{c};margin:2px 0;">{ag.role}</div>
                        <div style="font-size:0.6rem;">{"✅ On-meta" if fit else "⚠️ Off-meta"}</div>
                    </div>""", 148)

        # Score + breakdown
        cs,cb2=st.columns([1,2])
        with cs:
            st.markdown(f"""
            <div class="card score-card">
                <div class="card-title">🏆 Score</div>
                <div class="score-circle" style="border-color:{gc};">
                    <div class="score-number" style="color:{gc};">{raw}</div>
                    <div class="score-grade" style="color:{gc};">{gr}</div>
                </div>
                <div class="score-label" style="color:{gc};">{lb}</div>
            </div>""", unsafe_allow_html=True)
        with cb2:
            st.markdown('<div class="card"><div class="card-title">📈 Breakdown</div>', unsafe_allow_html=True)
            for cat,mx in {"Role Balance":25,"Map Fit":20,"Agent Synergy":20,"Utility Coverage":15,"Attack Strength":10,"Defense Strength":10}.items():
                val=bdwn.get(cat,0); pct=int((val/mx)*100) if mx else 0
                bc2=gc if pct>=70 else ("#ffd700" if pct>=40 else "#ff4444")
                st.markdown(f'<div class="score-bar-row"><div class="score-bar-label">{cat}</div><div class="score-bar-track"><div class="score-bar-fill" style="width:{pct}%;background:{bc2};"></div></div><div class="score-bar-val">{val}/{mx}</div></div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # S/W/Warn
        cs2,cw,cwa=st.columns(3)
        for col,title,items,cls in [(cs2,"✅ Strengths",strs,"strength-item"),(cw,"❌ Weaknesses",weaks,"weakness-item"),(cwa,"⚠️ Warnings",warns,"warning-item")]:
            with col:
                st.markdown(f'<div class="card"><div class="card-title">{title}</div>', unsafe_allow_html=True)
                if items:
                    for it in items:
                        pfx="✔" if "Strength" in title else ("✖" if "Weakness" in title else "⚠")
                        st.markdown(f'<div class="{cls}">{pfx} {it}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div style="color:#475569;font-size:0.8rem;">{"✅ No warnings!" if "Warning" in title else "None detected."}</div>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

        # Save + Export
        csave,cexp=st.columns(2)
        with csave:
            st.markdown('<div class="card"><div class="card-title">💾 Save Comp</div>', unsafe_allow_html=True)
            cname=st.text_input("Comp name",placeholder="e.g. Haven Breach Chain",key="save_name")
            notes=st.text_area("Notes",placeholder="Strategy notes...",key="save_notes",height=60)
            if st.button("💾 Save",use_container_width=True,type="primary"):
                if cname:
                    obj=Comp(agents=s_obj,map_name=selected_map,score=raw,warnings=warns,strengths=strs,weaknesses=weaks,notes=notes,name=cname)
                    data=obj.to_dict(); data["saved_at"]=datetime.now().strftime("%Y-%m-%d %H:%M")
                    save_comp(data); st.success(f"✅ Saved '{cname}'!")
                else: st.warning("Enter a comp name first.")
            st.markdown("</div>", unsafe_allow_html=True)

        with cexp:
            st.markdown('<div class="card"><div class="card-title">📤 Export</div>', unsafe_allow_html=True)
            edata={"comp_name":st.session_state.get("save_name","My Comp"),"map":selected_map,"score":raw,"grade":gr,"label":lb,"agents":[{"name":a.name,"role":a.role,"icon":a.icon} for a in s_obj],"strengths":strs,"weaknesses":weaks,"warnings":warns,"generated_by":"Gyd's Comp Helper","exported_at":datetime.now().strftime("%Y-%m-%d %H:%M")}
            st.download_button("📥 Download JSON",data=json.dumps(edata,indent=2),file_name=f"comp_{selected_map.lower()}_{datetime.now().strftime('%Y%m%d')}.json",mime="application/json",use_container_width=True)
            agent_dj = json.dumps([{
                "name":  a.name,
                "role":  a.role,
                "color": RC.get(a.role,"#64748b"),
                "icon":  AGENT_ICONS.get(a.name, a.icon),
            } for a in s_obj])
            pros_js  = json.dumps(strs[:3])
            cons_js  = json.dumps(weaks[:3])
            warns_js = json.dumps(warns[:2])

            # Build each agent's SVG as a 2D canvas draw — avoids all taint/CORS issues
            # We draw the role-colored circle + emoji icon directly on canvas
            components.html(f"""
            <button onclick="doExport()" style="background:linear-gradient(135deg,#7c3aed,#0ea5e9);
                border:none;color:#fff;padding:10px 0;border-radius:8px;font-size:0.85rem;
                font-weight:600;cursor:pointer;width:100%;margin-top:6px;font-family:'Segoe UI',sans-serif;">
                🖼️ Save as Image (PNG)
            </button>
            <script>
            function doExport() {{
                const W=960, H=600;
                const agents={agent_dj};
                const pros={pros_js}, cons={cons_js}, warns={warns_js};
                const cv = document.createElement('canvas');
                cv.width = W; cv.height = H;
                const ctx = cv.getContext('2d');

                // ── Background ──────────────────────────────────────────────
                ctx.fillStyle = '#020817'; ctx.fillRect(0,0,W,H);
                ctx.fillStyle = '#0d1b2e';
                ctx.beginPath(); ctx.roundRect(8,8,W-16,H-16,16); ctx.fill();
                ctx.strokeStyle = '#1a2f4a'; ctx.lineWidth = 1.5;
                ctx.beginPath(); ctx.roundRect(8,8,W-16,H-16,16); ctx.stroke();

                // ── Top gradient bar ─────────────────────────────────────────
                const g = ctx.createLinearGradient(0,0,W,0);
                g.addColorStop(0,'#7c3aed'); g.addColorStop(1,'#00d4ff');
                ctx.fillStyle = g; ctx.fillRect(8,8,W-16,4);

                // ── Header ───────────────────────────────────────────────────
                ctx.fillStyle='#e2e8f0'; ctx.font='bold 22px Segoe UI,Arial,sans-serif';
                ctx.textAlign='left'; ctx.fillText("Gyd's Comp Helper", 28, 46);
                const hw = ctx.measureText("Gyd's Comp Helper").width;
                ctx.fillStyle='#00d4ff'; ctx.fillText(' — {selected_map}', 28+hw, 46);

                // ── Score badge ──────────────────────────────────────────────
                const gcMap={{"S":"#ffd700","A":"#00ff9f","B":"#0ea5e9","C":"#f59e0b","D":"#ff4d6d"}};
                const gc = gcMap['{gr}'] || '#94a3b8';
                ctx.fillStyle = gc+'33';
                ctx.beginPath(); ctx.roundRect(W-128,18,112,38,10); ctx.fill();
                ctx.strokeStyle = gc; ctx.lineWidth=1.5;
                ctx.beginPath(); ctx.roundRect(W-128,18,112,38,10); ctx.stroke();
                ctx.fillStyle=gc; ctx.font='bold 18px Segoe UI,Arial,sans-serif';
                ctx.textAlign='center'; ctx.fillText('{raw}/100  {gr}', W-72, 41);

                // ── Subtitle ─────────────────────────────────────────────────
                ctx.fillStyle='#64748b'; ctx.font='13px Segoe UI,Arial,sans-serif';
                ctx.textAlign='left'; ctx.fillText('{lb}  ·  {selected_map}', 28, 66);

                // ── Divider ──────────────────────────────────────────────────
                ctx.fillStyle='#1a2f4a'; ctx.fillRect(28,76,W-56,1);

                // ── Agent portraits — drawn purely with canvas (no img loading) ──
                const slotW = (W-56) / agents.length;
                const agentY = 156; // center Y of portrait circles

                agents.forEach((ag, i) => {{
                    const cx = 28 + i*slotW + slotW/2;

                    // Outer glow ring
                    ctx.save();
                    ctx.shadowColor = ag.color;
                    ctx.shadowBlur  = 14;
                    ctx.strokeStyle = ag.color;
                    ctx.lineWidth   = 3;
                    ctx.beginPath(); ctx.arc(cx, agentY, 50, 0, Math.PI*2); ctx.stroke();
                    ctx.restore();

                    // Radial gradient fill inside circle (role color)
                    const rg = ctx.createRadialGradient(cx, agentY-15, 5, cx, agentY, 50);
                    rg.addColorStop(0, ag.color+'55');
                    rg.addColorStop(1, '#0a1628');
                    ctx.fillStyle = rg;
                    ctx.beginPath(); ctx.arc(cx, agentY, 49, 0, Math.PI*2); ctx.fill();

                    // Decorative inner ring
                    ctx.strokeStyle = ag.color + '40';
                    ctx.lineWidth = 1;
                    ctx.beginPath(); ctx.arc(cx, agentY, 40, 0, Math.PI*2); ctx.stroke();

                    // Emoji icon — large, centered
                    ctx.font = '40px Segoe UI Emoji,Apple Color Emoji,sans-serif';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillStyle = '#ffffff';
                    ctx.fillText(ag.icon, cx, agentY+2);
                    ctx.textBaseline = 'alphabetic';

                    // Agent name pill
                    ctx.fillStyle = ag.color + '30';
                    ctx.beginPath(); ctx.roundRect(cx-40, agentY+56, 80, 22, 11); ctx.fill();
                    ctx.strokeStyle = ag.color + '88';
                    ctx.lineWidth = 1;
                    ctx.beginPath(); ctx.roundRect(cx-40, agentY+56, 80, 22, 11); ctx.stroke();
                    ctx.fillStyle = '#e2e8f0';
                    ctx.font = 'bold 12px Segoe UI,Arial,sans-serif';
                    ctx.textAlign = 'center';
                    ctx.fillText(ag.name, cx, agentY+71);

                    // Role label
                    ctx.fillStyle = ag.color;
                    ctx.font = '10px Segoe UI,Arial,sans-serif';
                    ctx.fillText(ag.role, cx, agentY+90);
                }});

                // ── Divider between agents and analysis ──────────────────────
                ctx.fillStyle = '#1a2f4a'; ctx.fillRect(28, agentY+102, W-56, 1);

                // ── Analysis columns ─────────────────────────────────────────
                function wrapText(text, x, y, maxW, lineH) {{
                    const words = text.split(' '); let line=''; let cy=y;
                    words.forEach(w => {{
                        const test = line+w+' ';
                        if (ctx.measureText(test).width > maxW && line) {{
                            ctx.fillText(line.trim(), x, cy); line=w+' '; cy+=lineH;
                        }} else {{ line=test; }}
                    }});
                    ctx.fillText(line.trim(), x, cy);
                    return cy + lineH;
                }}

                const colW3 = (W-56)/3;
                const colY  = agentY + 120;
                const cols = [
                    {{ label:'✅  STRENGTHS', color:'#10b981', textColor:'#6ee7b7', items:pros,   x:28 }},
                    {{ label:'❌  WEAKNESSES', color:'#ff4d6d', textColor:'#fca5a5', items:cons,   x:28+colW3 }},
                    {{ label:'⚠️  WARNINGS',  color:'#f59e0b', textColor:'#fde68a', items:warns,  x:28+colW3*2 }},
                ];
                cols.forEach(col => {{
                    // Column header
                    ctx.fillStyle = col.color;
                    ctx.font = 'bold 11px Segoe UI,Arial,sans-serif';
                    ctx.textAlign = 'left';
                    ctx.fillText(col.label, col.x, colY);
                    ctx.fillStyle = col.color + '55';
                    ctx.fillRect(col.x, colY+4, colW3-12, 1);

                    if (col.items.length === 0) {{
                        ctx.fillStyle = '#10b981';
                        ctx.font = '11px Segoe UI,Arial,sans-serif';
                        ctx.fillText('✅ None — solid comp!', col.x, colY+22);
                    }} else {{
                        let ty = colY+22;
                        col.items.forEach((item, i) => {{
                            ctx.fillStyle = col.textColor;
                            ctx.font = '11px Segoe UI,Arial,sans-serif';
                            ty = wrapText('• '+item, col.x, ty, colW3-16, 15);
                            ty += 4;
                        }});
                    }}
                }});

                // ── Role pills row ────────────────────────────────────────────
                const roleMap = {{"Duelist":"#ff4d6d","Controller":"#7c3aed","Initiator":"#0ea5e9","Sentinel":"#10b981"}};
                const roleCounts = {{}};
                agents.forEach(a => {{ roleCounts[a.role] = (roleCounts[a.role]||0)+1; }});
                let rx=28; const ry=H-38;
                Object.entries(roleCounts).forEach(([role,cnt]) => {{
                    const rc=roleMap[role]||'#64748b';
                    const label=cnt+' '+role+(cnt>1?'s':'');
                    ctx.font='bold 10px Segoe UI,Arial,sans-serif';
                    const tw=ctx.measureText(label).width+20;
                    ctx.fillStyle=rc+'22'; ctx.beginPath();
                    ctx.roundRect(rx,ry,tw,20,10); ctx.fill();
                    ctx.strokeStyle=rc; ctx.lineWidth=1;
                    ctx.beginPath(); ctx.roundRect(rx,ry,tw,20,10); ctx.stroke();
                    ctx.fillStyle=rc; ctx.textAlign='center';
                    ctx.fillText(label, rx+tw/2, ry+13);
                    rx+=tw+8;
                }});

                // ── Footer ────────────────────────────────────────────────────
                ctx.fillStyle='#334155'; ctx.font='10px Segoe UI,Arial,sans-serif';
                ctx.textAlign='right';
                ctx.fillText("Generated by Gyd's Comp Helper · "+new Date().toLocaleDateString(), W-20, H-16);

                // ── Download ──────────────────────────────────────────────────
                const link = document.createElement('a');
                link.download = 'comp_{selected_map.replace(" ","_")}.png';
                link.href = cv.toDataURL('image/png');
                link.click();
            }}
            </script>""", height=50)
            st.markdown("</div>", unsafe_allow_html=True)

        cb1,cb3,_=st.columns([1,1,3])
        with cb1:
            if st.button("← Back to Agents",key="bk_ag"): st.session_state["builder_step"]=2;st.rerun()
        with cb3:
            if st.button("🔄 Start Over",key="restart"):
                st.session_state["builder_step"]=1
                st.session_state["selected_agents"]=[]
                st.session_state["active_page"]="Orbital Hub"
                st.rerun()
