"""
Orbital Hub — clean radial orbital timeline, centred, no list below.
3 nodes orbit the core. Clicking a node button navigates to that step.
Nodes light up green with ✓ as each stage is completed.
"""
import streamlit as st
import streamlit.components.v1 as components
from app.services.data_loader import load_maps


def render():
    step          = st.session_state.get("builder_step", 1)
    sel_map       = st.session_state.get("builder_map", "")
    sel_agents    = st.session_state.get("selected_agents", [])
    analysis_done = step >= 3 and len(sel_agents) > 0

    map_done    = bool(sel_map)
    agents_done = len(sel_agents) > 0

    map_sub    = sel_map if sel_map else "Not selected"
    agents_sub = f"{len(sel_agents)}/5 agents" if sel_agents else "No agents yet"
    score_sub  = "Ready to view" if analysis_done else ("Pick agents first" if not agents_done else "Run analysis")

    # Node states
    def state(done_cond, prev_cond=True):
        if done_cond:    return "completed"
        if prev_cond:    return "active"
        return "pending"

    n1_state = state(map_done and agents_done,  True)        # map
    n2_state = state(agents_done and analysis_done, map_done) # agents
    n3_state = state(analysis_done, agents_done)              # analysis

    stages_done = sum([map_done, agents_done, analysis_done])

    HUB = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{
    width:100%;height:100%;
    background:#020817;
    display:flex;align-items:center;justify-content:center;
    font-family:'Segoe UI',Arial,sans-serif;
    overflow:hidden;
}}

.scene{{
    position:relative;
    width:560px;height:560px;
    display:flex;align-items:center;justify-content:center;
}}

/* ── Orbit rings ── */
.ring{{
    position:absolute;border-radius:50%;border:1px solid;pointer-events:none;
}}
.ring1{{width:360px;height:360px;border-color:rgba(124,58,237,0.18);
        animation:spin 30s linear infinite;}}
.ring2{{width:400px;height:400px;border-color:rgba(0,212,255,0.07);
        border-style:dashed;animation:spin 50s linear infinite reverse;}}
@keyframes spin{{from{{transform:rotate(0deg)}}to{{transform:rotate(360deg)}}}}

/* ── Centre core ── */
.core{{
    position:absolute;width:90px;height:90px;border-radius:50%;
    background:radial-gradient(circle at 38% 35%,#7c3aed,#020817 80%);
    border:2px solid #7c3aed88;
    box-shadow:0 0 40px #7c3aed55,0 0 80px #7c3aed22;
    display:flex;flex-direction:column;align-items:center;justify-content:center;
    z-index:20;animation:coreGlow 3s ease-in-out infinite;
}}
@keyframes coreGlow{{
    0%,100%{{box-shadow:0 0 40px #7c3aed55,0 0 80px #7c3aed22;}}
    50%     {{box-shadow:0 0 60px #7c3aed88,0 0 120px #7c3aed44;}}
}}
.core-icon{{font-size:2rem;line-height:1;}}
.core-lbl{{font-size:0.42rem;color:#a78bfa;font-weight:700;letter-spacing:2.5px;margin-top:3px;}}

/* ── SVG overlay (lines + dots) ── */
.svg-overlay{{position:absolute;width:100%;height:100%;pointer-events:none;top:0;left:0;}}

/* ── Node wrapper ── */
.node{{
    position:absolute;
    display:flex;flex-direction:column;align-items:center;
    transform:translate(-50%,-50%);
    cursor:pointer;
    z-index:10;
}}

/* ── Node circle ── */
.nc{{
    width:74px;height:74px;border-radius:50%;
    display:flex;align-items:center;justify-content:center;
    font-size:1.9rem;position:relative;
    transition:all 0.35s ease;
    border:2.5px solid;
}}
.nc.pending{{background:#0a1628;border-color:#1e3a5f;opacity:0.55;}}
.nc.active{{
    background:linear-gradient(135deg,#00d4ff18,#0a1628);
    border-color:#00d4ff;
    box-shadow:0 0 22px #00d4ff55,0 0 44px #00d4ff22;
    animation:activeGlow 2s ease-in-out infinite;
}}
.nc.completed{{
    background:linear-gradient(135deg,#10b98128,#0a1628);
    border-color:#10b981;
    box-shadow:0 0 18px #10b98155,0 0 36px #10b98122;
}}
@keyframes activeGlow{{
    0%,100%{{box-shadow:0 0 22px #00d4ff55,0 0 44px #00d4ff22;}}
    50%     {{box-shadow:0 0 34px #00d4ff88,0 0 68px #00d4ff44;}}
}}

/* Pulse ring for active node */
.pulse{{
    position:absolute;width:90px;height:90px;border-radius:50%;
    border:2px solid #00d4ff33;pointer-events:none;
    animation:pulseOut 2.2s ease-out infinite;
}}
@keyframes pulseOut{{
    0%  {{transform:scale(1);opacity:0.7;}}
    100%{{transform:scale(1.75);opacity:0;}}
}}

/* Check badge */
.chk{{
    position:absolute;top:-3px;right:-3px;
    width:22px;height:22px;border-radius:50%;
    background:#10b981;border:2px solid #020817;
    display:flex;align-items:center;justify-content:center;
    font-size:0.6rem;font-weight:800;color:#000;
    box-shadow:0 0 8px #10b98188;
}}

/* Node text */
.n-step{{font-size:0.58rem;color:#334155;text-transform:uppercase;
          letter-spacing:2px;font-weight:600;margin-top:9px;}}
.n-title{{font-size:0.88rem;font-weight:700;margin-top:3px;text-align:center;}}
.n-title.pending  {{color:#334155;}}
.n-title.active   {{color:#00d4ff;}}
.n-title.completed{{color:#10b981;}}
.n-sub{{font-size:0.67rem;text-align:center;margin-top:2px;max-width:105px;
         white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.n-sub.pending  {{color:#1e3a5f;}}
.n-sub.active   {{color:#00d4ff88;}}
.n-sub.completed{{color:#10b98188;}}

/* CTA button */
.n-btn{{
    margin-top:9px;padding:6px 16px;border-radius:20px;
    font-size:0.68rem;font-weight:700;letter-spacing:0.4px;
    border:1.5px solid;cursor:pointer;background:transparent;
    font-family:'Segoe UI',Arial,sans-serif;
    transition:all 0.2s ease;
}}
.n-btn.pending  {{border-color:#1e3a5f;color:#1e3a5f;cursor:not-allowed;}}
.n-btn.active   {{border-color:#00d4ff;color:#00d4ff;}}
.n-btn.active:hover{{background:rgba(0,212,255,0.12);}}
.n-btn.completed{{border-color:#10b981;color:#10b981;}}
.n-btn.completed:hover{{background:rgba(16,185,129,0.12);}}

/* Progress footer */
.footer{{
    position:absolute;bottom:14px;left:50%;transform:translateX(-50%);
    font-size:0.7rem;color:#1e3a5f;letter-spacing:1px;white-space:nowrap;
    text-align:center;
}}
.footer span{{color:#7c3aed;font-weight:700;}}
</style></head>
<body>
<div class="scene">
  <div class="ring ring1"></div>
  <div class="ring ring2"></div>
  <svg class="svg-overlay" id="svg"></svg>
  <div class="core">
    <div class="core-icon">🎯</div>
    <div class="core-lbl">GYD'S</div>
  </div>
  <div id="nodes"></div>
  <div class="footer">Comp Journey &nbsp;·&nbsp; <span>{stages_done}/3 stages complete</span></div>
</div>

<script>
const NODES = [
  {{
    id:1, angle:270,
    state:"{n1_state}",
    icon:"🗺️", step:"STEP 1", title:"Map Selection",
    sub:"{map_sub}",
    btn: "{('✓ Change Map' if map_done else 'Select Map →')}",
    action:"step1"
  }},
  {{
    id:2, angle:30,
    state:"{n2_state}",
    icon:"🎮", step:"STEP 2", title:"Pick Agents",
    sub:"{agents_sub}",
    btn:"{('✓ Edit Agents' if agents_done else 'Pick Agents →')}",
    action:"step2"
  }},
  {{
    id:3, angle:150,
    state:"{n3_state}",
    icon:"📊", step:"STEP 3", title:"Analysis",
    sub:"{score_sub}",
    btn:"{('✓ View Again' if analysis_done else 'Analyze →')}",
    action:"step3"
  }},
];

const R = 175; // orbit radius
const CX = 280, CY = 280; // centre of 560×560 scene
const svg    = document.getElementById('svg');
const nWrap  = document.getElementById('nodes');
svg.setAttribute('viewBox','0 0 560 560');
svg.setAttribute('width','560');svg.setAttribute('height','560');

const stateColor = {{
  completed: '#10b981',
  active:    '#00d4ff',
  pending:   '#1e3a5f'
}};

NODES.forEach((n, i) => {{
  const rad = (n.angle * Math.PI) / 180;
  const nx  = CX + R * Math.cos(rad);
  const ny  = CY + R * Math.sin(rad);
  const col = stateColor[n.state];

  // ── SVG line from core to node ──────────────────────────────────
  const line = document.createElementNS('http://www.w3.org/2000/svg','line');
  line.setAttribute('x1', CX); line.setAttribute('y1', CY);
  line.setAttribute('x2', nx); line.setAttribute('y2', ny);
  line.setAttribute('stroke', col);
  line.setAttribute('stroke-width', n.state==='pending' ? '1' : '1.5');
  line.setAttribute('stroke-opacity', n.state==='pending' ? '0.25' : '0.5');
  if (n.state==='pending') line.setAttribute('stroke-dasharray','5,5');
  svg.appendChild(line);

  // Travelling dot along line (active + completed only)
  if (n.state !== 'pending') {{
    const dot = document.createElementNS('http://www.w3.org/2000/svg','circle');
    dot.setAttribute('r','3');
    dot.setAttribute('fill', col);
    dot.setAttribute('opacity','0.85');
    const anim = document.createElementNS('http://www.w3.org/2000/svg','animateMotion');
    anim.setAttribute('dur', (1.8 + i*0.5)+'s');
    anim.setAttribute('repeatCount','indefinite');
    anim.setAttribute('path',`M${{CX}},${{CY}} L${{nx}},${{ny}}`);
    dot.appendChild(anim);
    svg.appendChild(dot);
  }}

  // Arc between completed consecutive nodes
  if (i>0 && n.state==='completed' && NODES[i-1].state==='completed') {{
    const prev = NODES[i-1];
    const pr   = (prev.angle * Math.PI)/180;
    const px   = CX + R * Math.cos(pr);
    const py   = CY + R * Math.sin(pr);
    const arc  = document.createElementNS('http://www.w3.org/2000/svg','path');
    const mx   = (px+nx)/2 + (CY-(py+ny)/2)*0.18;
    const my   = (py+ny)/2 + (CX-(px+nx)/2)*0.18;
    arc.setAttribute('d',`M${{px}},${{py}} Q${{mx}},${{my}} ${{nx}},${{ny}}`);
    arc.setAttribute('stroke','#10b98144');arc.setAttribute('stroke-width','1.5');
    arc.setAttribute('fill','none');arc.setAttribute('stroke-dasharray','4,4');
    svg.appendChild(arc);
  }}

  // ── DOM node ────────────────────────────────────────────────────
  const div = document.createElement('div');
  div.className = 'node';
  div.style.left = nx+'px';
  div.style.top  = ny+'px';

  const isPending   = n.state==='pending';
  const isActive    = n.state==='active';
  const isCompleted = n.state==='completed';

  div.innerHTML = `
    <div class="n-step">${{n.step}}</div>
    <div class="nc ${{n.state}}" id="nc${{n.id}}">
      ${{isActive    ? '<div class="pulse"></div>' : ''}}
      <span style="position:relative;z-index:2;">${{n.icon}}</span>
      ${{isCompleted ? '<div class="chk">✓</div>' : ''}}
    </div>
    <div class="n-title ${{n.state}}">${{n.title}}</div>
    <div class="n-sub   ${{n.state}}">${{n.sub}}</div>
    <button class="n-btn ${{n.state}}" ${{isPending?'disabled':''}}
            onclick="nav('${{n.action}}')">${{n.btn}}</button>
  `;
  nWrap.appendChild(div);
}});

function nav(action) {{
  window.parent.postMessage(JSON.stringify({{action}}), '*');
}}
</script>
</body></html>"""

    # Centre the orbital iframe + make nav buttons compact
    st.markdown("""
    <style>
    iframe[title="orbital_hub"] { display:block; margin:0 auto; border:none !important; }
    </style>""", unsafe_allow_html=True)

    components.html(HUB, height=560, scrolling=False)

    # ── Minimal centred nav controls (iframe can't trigger Streamlit reruns,
    #    so these compact buttons are the actual clickable navigation) ──────────
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        b1, b2, b3, b4 = st.columns([3, 3, 3, 2])
        with b1:
            if st.button("🗺️ Map" + (" ✓" if map_done else ""), key="hub_s1",
                         use_container_width=True,
                         type="primary" if not map_done else "secondary"):
                st.session_state["builder_step"] = 1
                st.session_state["active_page"]  = "Builder"
                st.rerun()
        with b2:
            if st.button("🎮 Agents" + (" ✓" if agents_done else ""), key="hub_s2",
                         use_container_width=True, disabled=not map_done,
                         type="primary" if (map_done and not agents_done) else "secondary"):
                st.session_state["builder_step"] = 2
                st.session_state["active_page"]  = "Builder"
                st.rerun()
        with b3:
            if st.button("📊 Analysis" + (" ✓" if analysis_done else ""), key="hub_s3",
                         use_container_width=True, disabled=not agents_done,
                         type="primary" if (agents_done and not analysis_done) else "secondary"):
                st.session_state["builder_step"] = 3
                st.session_state["active_page"]  = "Builder"
                st.rerun()
        with b4:
            if st.button("🔄", key="hub_reset", use_container_width=True,
                         help="Reset journey"):
                st.session_state["builder_step"]    = 1
                st.session_state["selected_agents"] = []
                st.session_state["builder_map"]     = load_maps()[0]["name"]
                st.session_state["active_page"]     = "Orbital Hub"
                st.rerun()
