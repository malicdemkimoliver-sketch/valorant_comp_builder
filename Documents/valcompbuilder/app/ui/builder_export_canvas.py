"""
Canvas-based PNG export using HTML5 Canvas + client-side rendering
This is the original design from Gyd's Comp Helper
"""
import streamlit as st
import streamlit.components.v1 as components
import json

def render_png_export_button(agents, selected_map, score, grade, strengths, weaknesses, warnings):
    """
    Render the PNG export button using HTML5 Canvas
    agents: list of agent objects with .icon, .name, .role
    selected_map: string
    score: int
    grade: str (S, A, B, C, D, F)
    strengths/weaknesses/warnings: list of strings
    """
    
    # Color map for roles
    role_colors = {
        "Duelist": "#ff4d6d",
        "Controller": "#7c3aed",
        "Initiator": "#0ea5e9",
        "Sentinel": "#10b981",
    }
    
    # Build agent data JSON
    agent_dj = json.dumps([
        {
            "name": a.name,
            "icon": a.icon,
            "role": a.role,
            "color": role_colors.get(a.role, "#64748b")
        }
        for a in agents
    ])
    
    # Build pros/cons/warns arrays
    pros_js = json.dumps(strengths)
    cons_js = json.dumps(weaknesses)
    warns_js = json.dumps(warnings)
    
    # Grade color map
    grade_colors = {
        "S": "#ffd700",
        "A": "#00ff9f",
        "B": "#0ea5e9",
        "C": "#f59e0b",
        "D": "#ff4d6d",
        "F": "#ff0000"
    }
    
    # Label map
    grade_labels = {
        "S": "Elite Comp - Tournament Ready",
        "A": "Excellent Comp - Highly Recommended",
        "B": "Good Comp - Solid Strategy",
        "C": "Viable Comp - Needs Refinement",
        "D": "Playable - Many Issues",
        "F": "Poor Comp - Rework Needed"
    }
    
    lb = grade_labels.get(grade, "Unknown")
    
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
        const gcMap={{"S":"#ffd700","A":"#00ff9f","B":"#0ea5e9","C":"#f59e0b","D":"#ff4d6d","F":"#ff0000"}};
        const gc = gcMap['{grade}'] || '#94a3b8';
        ctx.fillStyle = gc+'33';
        ctx.beginPath(); ctx.roundRect(W-128,18,112,38,10); ctx.fill();
        ctx.strokeStyle = gc; ctx.lineWidth=1.5;
        ctx.beginPath(); ctx.roundRect(W-128,18,112,38,10); ctx.stroke();
        ctx.fillStyle=gc; ctx.font='bold 18px Segoe UI,Arial,sans-serif';
        ctx.textAlign='center'; ctx.fillText('{score}/100  {grade}', W-72, 41);

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
        const mapName = '{selected_map}'.replace(/ /g, '_');
        link.download = 'comp_' + mapName + '.png';
        link.href = cv.toDataURL('image/png');
        link.click();
    }}
    </script>
    """, height=50)

