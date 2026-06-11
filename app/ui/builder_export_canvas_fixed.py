"""
Fixed Canvas-based PNG Export - Uses current selected agents
"""
import streamlit as st
import json

def render_export_canvas(selected_agents, selected_map, score, grade):
    """
    Render and export composition as PNG using HTML5 Canvas
    NOW USES CURRENT AGENTS instead of session state
    """
    
    # Get role colors
    RC = {
        "Duelist": "#ff4d6d",
        "Controller": "#7c3aed",
        "Initiator": "#0ea5e9",
        "Sentinel": "#10b981"
    }
    
    RI = {
        "Duelist": "⚔️",
        "Controller": "💨",
        "Initiator": "🔍",
        "Sentinel": "🛡️"
    }
    
    # Build agent circles HTML
    agent_circles = ""
    for i, agent in enumerate(selected_agents):
        role = agent.role if hasattr(agent, 'role') else "Unknown"
        color = RC.get(role, "#999999")
        emoji = RI.get(role, "❓")
        x = 150 + (i * 140)
        
        agent_circles += f"""
        <g transform="translate({x}, 280)">
            <circle cx="0" cy="0" r="45" fill="{color}" opacity="0.2" stroke="{color}" stroke-width="2"/>
            <circle cx="0" cy="0" r="40" fill="none" stroke="{color}" stroke-width="3" filter="url(#glow)"/>
            <text x="0" y="-55" font-size="32" text-anchor="middle">{emoji}</text>
            <text x="0" y="8" font-size="16" font-weight="bold" text-anchor="middle" fill="#fff">{agent.name}</text>
            <text x="0" y="25" font-size="12" text-anchor="middle" fill="#aaa">{role}</text>
        </g>
        """
    
    # Get grade color
    grade_colors = {
        "S": "#ffd700",
        "A": "#00d9ff",
        "B": "#0ea5e9",
        "C": "#f59e0b",
        "D": "#ef4444",
        "F": "#7f1d1d"
    }
    grade_color = grade_colors.get(grade, "#999")
    
    # Create canvas HTML
    canvas_html = f"""
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    </head>
    <body style="margin: 0; padding: 20px; background: #0a0e27;">
        <div id="comp-card" style="width: 1200px; background: linear-gradient(135deg, #0f1e35 0%, #1a2f4a 100%); border-radius: 12px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.8);">
            
            <!-- Header -->
            <div style="background: linear-gradient(90deg, #00d9ff 0%, #7c3aed 100%); padding: 30px; text-align: center;">
                <h1 style="margin: 0; color: white; font-size: 32px; font-family: Arial, sans-serif;">Gyd's Comp Helper</h1>
                <p style="margin: 5px 0 0 0; color: #ddd; font-size: 20px;">{selected_map}</p>
            </div>
            
            <!-- Score Badge -->
            <div style="position: absolute; top: 30px; right: 30px; background: {grade_color}; color: #000; padding: 15px 25px; border-radius: 50px; font-weight: bold; font-size: 18px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                {grade} · {score} pts
            </div>
            
            <!-- Agents -->
            <svg width="100%" height="400" style="background: #020817;">
                <defs>
                    <filter id="glow">
                        <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                        <feMerge>
                            <feMergeNode in="coloredBlur"/>
                            <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                    </filter>
                </defs>
                {agent_circles}
            </svg>
            
            <!-- Footer -->
            <div style="padding: 20px; text-align: center; color: #888; font-size: 12px; border-top: 1px solid #333;">
                Generated with Valorant Comp Builder · {selected_map} Meta Analysis
            </div>
        </div>
        
        <script>
        setTimeout(() => {{
            html2canvas(document.getElementById('comp-card'), {{
                backgroundColor: null,
                scale: 2,
                useCORS: true,
                logging: false
            }}).then(canvas => {{
                const link = document.createElement('a');
                link.href = canvas.toDataURL('image/png');
                link.download = 'comp_{selected_map.replace(/ /g, '_')}.png';
                link.click();
            }});
        }}, 500);
        </script>
    </body>
    </html>
    """
    
    st.components.v1.html(canvas_html, height=500)
    st.success("✅ PNG downloaded! Check your downloads folder.")

