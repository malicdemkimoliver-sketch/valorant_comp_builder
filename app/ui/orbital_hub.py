"""
Orbital Hub — Radial orbital timeline that serves as the home screen
and tracks the user's comp-building journey through 3 nodes:
  Node 1 → Map Selection     (step 1)
  Node 2 → Agent Pick        (step 2)
  Node 3 → Analysis          (step 3)

Each node lights up (completed) as the user passes through it.
Clicking a node navigates directly to that step.
"""
import streamlit as st
import streamlit.components.v1 as components
from app.services.data_loader import load_maps


def render():
    """Render the orbital hub home screen."""
    step        = st.session_state.get("builder_step", 1)
    sel_map     = st.session_state.get("builder_map", "")
    sel_agents  = st.session_state.get("selected_agents", [])

    # Determine which nodes are completed
    map_done    = bool(sel_map)
    agents_done = len(sel_agents) > 0
    analysis_done = step >= 3 and agents_done

    # Build status labels for each node
    map_label     = sel_map if sel_map else "Not selected"
    agents_label  = f"{len(sel_agents)}/5 agents" if sel_agents else "No agents"
    score_label   = "View results" if analysis_done else "Build first"

    hub_html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html, body {{ width:100%; height:100%; background:transparent; overflow:hidden; font-family:'Segoe UI',Arial,sans-serif; }}

  .orbit-container {{
    width:100%; height:520px;
    display:flex; align-items:center; justify-content:center;
    position:relative;
  }}

  /* ── Centre core ── */
  .core {{
    position:absolute;
    width:88px; height:88px; border-radius:50%;
    background: radial-gradient(circle at 35% 35%, #7c3aed, #020817);
    border: 2px solid #7c3aed;
    box-shadow: 0 0 40px #7c3aed66, 0 0 80px #7c3aed33;
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    z-index:20; cursor:default;
    animation: corePulse 3s ease-in-out infinite;
  }}
  .core-icon {{ font-size:2rem; line-height:1; }}
  .core-text {{ font-size:0.5rem; color:#a78bfa; font-weight:700; letter-spacing:2px; margin-top:2px; }}

  @keyframes corePulse {{
    0%,100% {{ box-shadow:0 0 40px #7c3aed66, 0 0 80px #7c3aed33; }}
    50%      {{ box-shadow:0 0 60px #7c3aed99, 0 0 120px #7c3aed55; }}
  }}

  /* ── Orbit ring ── */
  .orbit-ring {{
    position:absolute;
    width:380px; height:380px; border-radius:50%;
    border: 1px solid rgba(124,58,237,0.2);
    animation: ringRotate 30s linear infinite;
  }}
  .orbit-ring-2 {{
    position:absolute;
    width:420px; height:420px; border-radius:50%;
    border: 1px dashed rgba(0,212,255,0.08);
    animation: ringRotate 50s linear infinite reverse;
  }}
  @keyframes ringRotate {{
    from {{ transform:rotate(0deg); }}
    to   {{ transform:rotate(360deg); }}
  }}

  /* ── Connection lines ── */
  .connections {{
    position:absolute;
    width:100%; height:100%;
    pointer-events:none;
  }}

  /* ── Nodes ── */
  .node {{
    position:absolute;
    display:flex; flex-direction:column; align-items:center;
    cursor:pointer;
    transition: transform 0.3s ease;
    z-index:10;
  }}
  .node:hover {{ transform: scale(1.08); }}

  .node-circle {{
    width:72px; height:72px; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    font-size:1.8rem;
    border: 2.5px solid;
    position:relative;
    transition: all 0.4s ease;
  }}

  .node-circle.pending {{
    background: #0a1628;
    border-color: #1a2f4a;
    box-shadow: none;
    opacity: 0.7;
  }}

  .node-circle.active {{
    background: linear-gradient(135deg, #00d4ff22, #0a1628);
    border-color: #00d4ff;
    box-shadow: 0 0 24px #00d4ff55, 0 0 48px #00d4ff22;
    animation: activeGlow 2s ease-in-out infinite;
  }}

  .node-circle.completed {{
    background: linear-gradient(135deg, #10b98133, #0a1628);
    border-color: #10b981;
    box-shadow: 0 0 20px #10b98155, 0 0 40px #10b98122;
  }}

  @keyframes activeGlow {{
    0%,100% {{ box-shadow:0 0 24px #00d4ff55, 0 0 48px #00d4ff22; }}
    50%      {{ box-shadow:0 0 36px #00d4ff88, 0 0 72px #00d4ff44; }}
  }}

  /* Check mark overlay for completed */
  .check-badge {{
    position:absolute;
    top:-4px; right:-4px;
    width:22px; height:22px; border-radius:50%;
    background:#10b981;
    border:2px solid #020817;
    display:flex; align-items:center; justify-content:center;
    font-size:0.65rem; font-weight:800; color:#000;
    box-shadow: 0 0 8px #10b98188;
  }}

  /* Active pulse ring */
  .pulse-ring {{
    position:absolute;
    width:88px; height:88px; border-radius:50%;
    border:2px solid #00d4ff44;
    animation: pulseOut 2s ease-out infinite;
    pointer-events:none;
  }}
  @keyframes pulseOut {{
    0%   {{ transform:scale(1); opacity:0.8; }}
    100% {{ transform:scale(1.7); opacity:0; }}
  }}

  /* Node labels */
  .node-step {{
    font-size:0.6rem; color:#475569; text-transform:uppercase;
    letter-spacing:2px; margin-top:8px; font-weight:600;
  }}
  .node-title {{
    font-size:0.85rem; font-weight:700; color:#e2e8f0;
    margin-top:2px; text-align:center;
  }}
  .node-title.completed {{ color:#10b981; }}
  .node-title.active    {{ color:#00d4ff; }}
  .node-subtitle {{
    font-size:0.68rem; color:#475569; margin-top:2px;
    text-align:center; max-width:110px;
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
  }}
  .node-subtitle.completed {{ color:#10b98188; }}
  .node-subtitle.active    {{ color:#00d4ff88; }}

  /* CTA button below each node */
  .node-btn {{
    margin-top:8px;
    padding:5px 14px; border-radius:20px;
    font-size:0.68rem; font-weight:700; letter-spacing:0.5px;
    border:1px solid; cursor:pointer;
    transition:all 0.2s ease;
    background:transparent;
    font-family:'Segoe UI',Arial,sans-serif;
  }}
  .node-btn.pending  {{ border-color:#1a2f4a; color:#334155; }}
  .node-btn.pending:hover {{ border-color:#2a4a70; color:#64748b; }}
  .node-btn.active   {{ border-color:#00d4ff; color:#00d4ff; background:rgba(0,212,255,0.08); }}
  .node-btn.active:hover {{ background:rgba(0,212,255,0.18); }}
  .node-btn.completed {{ border-color:#10b981; color:#10b981; background:rgba(16,185,129,0.08); }}
  .node-btn.completed:hover {{ background:rgba(16,185,129,0.18); }}

  /* Connector SVG lines */
  .connectors {{ position:absolute; width:100%; height:520px; pointer-events:none; top:0; left:0; }}

  /* Progress arc overlay */
  .progress-text {{
    position:absolute;
    bottom:18px; left:50%; transform:translateX(-50%);
    font-size:0.72rem; color:#334155; letter-spacing:1px;
    white-space:nowrap;
  }}
  .progress-text span {{ color:#7c3aed; font-weight:700; }}
</style>
</head>
<body>
<div class="orbit-container" id="oc">

  <!-- SVG connector lines -->
  <svg class="connectors" id="connSvg"></svg>

  <!-- Orbit rings -->
  <div class="orbit-ring"></div>
  <div class="orbit-ring-2"></div>

  <!-- Centre core -->
  <div class="core">
    <div class="core-icon">🎯</div>
    <div class="core-text">GYD'S</div>
  </div>

  <!-- Nodes rendered by JS -->
  <div id="nodes"></div>

  <!-- Progress text -->
  <div class="progress-text">
    Comp Journey &nbsp;·&nbsp;
    <span>{sum([map_done, agents_done, analysis_done])}/3 stages complete</span>
  </div>
</div>

<script>
const MAP_DONE      = {'true' if map_done else 'false'};
const AGENTS_DONE   = {'true' if agents_done else 'false'};
const ANALYSIS_DONE = {'true' if analysis_done else 'false'};

const nodes = [
  {{
    id: 1,
    step: "STEP 1",
    title: "Map Selection",
    subtitle: "{map_label}",
    icon: "🗺️",
    state: MAP_DONE ? (AGENTS_DONE ? 'completed' : 'active') : 'active',
    action: "selectMap",
    btnLabel: MAP_DONE ? "✓ Change Map" : "Select Map →",
  }},
  {{
    id: 2,
    step: "STEP 2",
    title: "Pick Agents",
    subtitle: "{agents_label}",
    icon: "🎮",
    state: AGENTS_DONE ? (ANALYSIS_DONE ? 'completed' : 'active') : (MAP_DONE ? 'active' : 'pending'),
    action: "pickAgents",
    btnLabel: AGENTS_DONE ? "✓ Edit Agents" : "Pick Agents →",
  }},
  {{
    id: 3,
    step: "STEP 3",
    title: "Analysis",
    subtitle: "{score_label}",
    icon: "📊",
    state: ANALYSIS_DONE ? 'completed' : (AGENTS_DONE ? 'active' : 'pending'),
    action: "viewAnalysis",
    btnLabel: ANALYSIS_DONE ? "✓ View Again" : "Analyze →",
  }},
];

// Position nodes on a circle — 3 nodes at 270°, 30°, 150° (top, right, left)
const ANGLES = [270, 30, 150];
const R = 190; // orbit radius
const cx = 0, cy = 0; // relative to center

const container = document.getElementById('nodes');
const svg       = document.getElementById('connSvg');
const oc        = document.getElementById('oc');
const ocRect    = {{ w: oc.offsetWidth || 600, h: 520 }};
const ocCX      = ocRect.w / 2;
const ocCY      = 260;

const nodePositions = [];

nodes.forEach((node, i) => {{
  const angleRad = (ANGLES[i] * Math.PI) / 180;
  const nx = ocCX + R * Math.cos(angleRad);
  const ny = ocCY + R * Math.sin(angleRad);
  nodePositions.push({{ x: nx, y: ny }});

  const wrap = document.createElement('div');
  wrap.className = 'node';
  wrap.style.left = nx + 'px';
  wrap.style.top  = ny + 'px';
  wrap.style.transform = 'translate(-50%, -50%)';

  const hasPulse = node.state === 'active';
  const hasCheck = node.state === 'completed';

  wrap.innerHTML = `
    <div class="node-step">${{node.step}}</div>
    <div class="node-circle ${{node.state}}" id="nc${{node.id}}">
      ${{hasPulse ? '<div class="pulse-ring"></div>' : ''}}
      <span style="position:relative;z-index:2;">${{node.icon}}</span>
      ${{hasCheck ? '<div class="check-badge">✓</div>' : ''}}
    </div>
    <div class="node-title ${{node.state}}">${{node.title}}</div>
    <div class="node-subtitle ${{node.state}}">${{node.subtitle}}</div>
    <button class="node-btn ${{node.state}}" onclick="handleNav('${{node.action}}')">${{node.btnLabel}}</button>
  `;
  container.appendChild(wrap);
}});

// Draw SVG connector lines between centre and each node
const coreCX = ocCX, coreCY = ocCY;
nodePositions.forEach((pos, i) => {{
  const state = nodes[i].state;
  const lineColor = state === 'completed' ? '#10b98155'
                  : state === 'active'    ? '#00d4ff44'
                  : '#1a2f4a33';
  const dashArr  = state === 'pending' ? '6,6' : 'none';

  const line = document.createElementNS('http://www.w3.org/2000/svg','line');
  line.setAttribute('x1', coreCX); line.setAttribute('y1', coreCY);
  line.setAttribute('x2', pos.x);  line.setAttribute('y2', pos.y);
  line.setAttribute('stroke', lineColor);
  line.setAttribute('stroke-width', '1.5');
  if (dashArr !== 'none') line.setAttribute('stroke-dasharray', dashArr);
  svg.appendChild(line);

  // Animated travelling dot on completed lines
  if (state === 'completed' || state === 'active') {{
    const circle = document.createElementNS('http://www.w3.org/2000/svg','circle');
    circle.setAttribute('r', '3');
    circle.setAttribute('fill', state === 'completed' ? '#10b981' : '#00d4ff');
    circle.setAttribute('opacity', '0.8');

    const anim = document.createElementNS('http://www.w3.org/2000/svg','animateMotion');
    anim.setAttribute('dur', (2 + i * 0.4) + 's');
    anim.setAttribute('repeatCount', 'indefinite');
    anim.setAttribute('path', `M${{coreCX}},${{coreCY}} L${{pos.x}},${{pos.y}}`);
    circle.appendChild(anim);
    svg.appendChild(circle);
  }}
}});

// Also draw node-to-node arcs for completed path
if (MAP_DONE && AGENTS_DONE) {{
  const arc = document.createElementNS('http://www.w3.org/2000/svg','path');
  const p0 = nodePositions[0], p1 = nodePositions[1];
  const mx = (p0.x+p1.x)/2, my = (p0.y+p1.y)/2 - 30;
  arc.setAttribute('d', `M${{p0.x}},${{p0.y}} Q${{mx}},${{my}} ${{p1.x}},${{p1.y}}`);
  arc.setAttribute('stroke','#10b98133'); arc.setAttribute('stroke-width','1');
  arc.setAttribute('fill','none'); arc.setAttribute('stroke-dasharray','4,4');
  svg.appendChild(arc);
}}
if (AGENTS_DONE && ANALYSIS_DONE) {{
  const arc2 = document.createElementNS('http://www.w3.org/2000/svg','path');
  const p1 = nodePositions[1], p2 = nodePositions[2];
  const mx = (p1.x+p2.x)/2+30, my = (p1.y+p2.y)/2;
  arc2.setAttribute('d', `M${{p1.x}},${{p1.y}} Q${{mx}},${{my}} ${{p2.x}},${{p2.y}}`);
  arc2.setAttribute('stroke','#10b98133'); arc2.setAttribute('stroke-width','1');
  arc2.setAttribute('fill','none'); arc2.setAttribute('stroke-dasharray','4,4');
  svg.appendChild(arc2);
}}

// Navigation
function handleNav(action) {{
  const msg = JSON.stringify({{ action }});
  window.parent.postMessage(msg, '*');
}}
</script>
</body></html>"""

    components.html(hub_html, height=540, scrolling=False)

    # ── Listen for postMessage from iframe ─────────────────────────────────────
    # Streamlit doesn't natively receive postMessage, so we use query params trick
    # with nav buttons below the orbital as fallback (always visible)
    st.markdown("""
    <div style="height:8px;"></div>
    <div style="text-align:center;color:#1e3a5f;font-size:0.7rem;letter-spacing:1px;">
        ── CLICK A NODE OR USE THE BUTTONS BELOW ──
    </div>
    """, unsafe_allow_html=True)

    step_colors = {
        1: ("#00d4ff", "active" if not map_done else "completed"),
        2: ("#0ea5e9", "pending" if not map_done else ("completed" if agents_done else "active")),
        3: ("#10b981", "pending" if not agents_done else ("completed" if analysis_done else "active")),
    }

    col1, col2, col3, col4 = st.columns([1,1,1,1])

    with col1:
        c, state = step_colors[1]
        icon = "✅" if state == "completed" else ("🟢" if state == "active" else "⬜")
        label = f"{icon} Step 1: Map"
        if state == "completed":
            label += f" ({sel_map})"
        if st.button(label, key="orb_s1", use_container_width=True,
                     type="primary" if state == "active" else "secondary"):
            st.session_state["builder_step"] = 1
            st.session_state["active_page"] = "Builder"
            st.rerun()

    with col2:
        c, state = step_colors[2]
        icon = "✅" if state == "completed" else ("🟢" if state == "active" else "⬜")
        label = f"{icon} Step 2: Agents"
        if state == "completed":
            label += f" ({len(sel_agents)} picked)"
        disabled = not map_done
        if st.button(label, key="orb_s2", use_container_width=True,
                     type="primary" if state == "active" else "secondary",
                     disabled=disabled):
            st.session_state["builder_step"] = 2
            st.session_state["active_page"] = "Builder"
            st.rerun()

    with col3:
        c, state = step_colors[3]
        icon = "✅" if state == "completed" else ("🟢" if state == "active" else "⬜")
        label = f"{icon} Step 3: Analysis"
        disabled = not agents_done
        if st.button(label, key="orb_s3", use_container_width=True,
                     type="primary" if state == "active" else "secondary",
                     disabled=disabled):
            st.session_state["builder_step"] = 3
            st.session_state["active_page"] = "Builder"
            st.rerun()

    with col4:
        if st.button("🔄 Reset Journey", key="orb_reset", use_container_width=True):
            st.session_state["builder_step"] = 1
            st.session_state["selected_agents"] = []
            st.session_state["builder_map"] = load_maps()[0]["name"]
            st.session_state["active_page"] = "Orbital Hub"
            st.rerun()

    # ── Journey status card ────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    steps_html = ""
    step_defs = [
        (1, "🗺️", "Map Selection",  sel_map or "Not selected",   map_done),
        (2, "🎮", "Agent Pick",     f"{len(sel_agents)}/5 agents", agents_done),
        (3, "📊", "Analysis",       "View comp score",             analysis_done),
    ]
    for num, icon, title, sub, done in step_defs:
        c = "#10b981" if done else "#1a2f4a"
        tc = "#10b981" if done else "#334155"
        st.markdown(f"""
        <div style="background:#0a1628;border:1px solid {c};border-radius:10px;
                    padding:12px 16px;margin:4px 0;display:flex;align-items:center;gap:12px;">
            <div style="width:36px;height:36px;border-radius:50%;background:{c}22;
                        border:2px solid {c};display:flex;align-items:center;
                        justify-content:center;font-size:1.1rem;flex-shrink:0;">{icon}</div>
            <div style="flex:1;">
                <div style="font-weight:700;color:#e2e8f0;font-size:0.88rem;">
                    Step {num}: {title}
                </div>
                <div style="font-size:0.72rem;color:#475569;margin-top:1px;">{sub}</div>
            </div>
            <div style="font-size:1.2rem;">{"✅" if done else "⬜"}</div>
        </div>""", unsafe_allow_html=True)
