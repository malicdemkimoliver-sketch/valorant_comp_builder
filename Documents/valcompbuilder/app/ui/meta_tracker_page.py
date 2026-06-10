"""
Meta Tracker Page — VCT pick rates and win rates by map
"""
import streamlit as st
from app.services.meta_service import get_all_meta_agents_for_map, load_meta_data
from app.services.data_loader import load_maps, load_agents

def get_color_for_pick_rate(pick_rate):
    """Get heatmap color for pick rate (green=high, amber=medium, red=low)"""
    if pick_rate >= 80:
        return "#10b981"  # Green (S tier)
    elif pick_rate >= 50:
        return "#f59e0b"  # Amber (A tier)
    else:
        return "#ff4d6d"  # Red (B/C tier)

def get_color_for_win_rate(win_rate):
    """Get heatmap color for win rate (cyan=high, purple=medium, dark=low)"""
    if win_rate >= 52:
        return "#00d4ff"  # Cyan (strong)
    elif win_rate >= 49:
        return "#a78bfa"  # Purple (neutral)
    else:
        return "#64748b"  # Gray (weak)

def render():
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">📊 Meta Tracker</h1>
        <p class="page-subtitle">VCT pick rates & win rates by map — see what the pros are playing</p>
    </div>
    """, unsafe_allow_html=True)

    maps_list = load_maps()
    map_names = [m["name"] for m in maps_list]

    # Map selector
    col1, col2 = st.columns([2, 3])
    with col1:
        selected_map = st.selectbox("🗺️ Select Map", map_names, key="meta_map")
    with col2:
        st.markdown("")

    # Get meta data for selected map
    map_meta = get_all_meta_agents_for_map(selected_map)
    
    if not map_meta:
        st.warning(f"No meta data available for {selected_map}")
        return

    # Build table data
    agents_data = []
    for agent_name, stats in map_meta.items():
        agents_data.append({
            "name": agent_name,
            "pick_rate": stats.get("pick_rate", 0),
            "win_rate": stats.get("win_rate", 0),
            "tier": stats.get("tier", "?")
        })

    # Sort by pick rate (descending)
    agents_data.sort(key=lambda x: x["pick_rate"], reverse=True)

    # Render as properly aligned table with consistent grid
    st.markdown("""
    <style>
    .meta-table {
        width: 100%;
        display: flex;
        flex-direction: column;
        margin: 20px 0;
        border: 1px solid #1a2f4a;
        border-radius: 8px;
        overflow: hidden;
    }
    .meta-row {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr;
        gap: 0;
        border-bottom: 1px solid #1a2f4a;
    }
    .meta-row:last-child {
        border-bottom: none;
    }
    .meta-header {
        background: #0f1e35;
        border-bottom: 2px solid #334155;
    }
    .meta-cell {
        padding: 14px 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #e2e8f0;
        font-size: 0.9rem;
    }
    .meta-header .meta-cell {
        font-weight: 700;
        color: #e2e8f0;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .agent-name-cell {
        justify-content: flex-start;
        font-weight: 600;
    }
    .stat-cell {
        font-weight: 700;
        border-radius: 6px;
    }
    .tier-cell {
        justify-content: center;
    }
    .tier-badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    </style>
    
    <div class="meta-table">
        <div class="meta-row meta-header">
            <div class="meta-cell">Agent</div>
            <div class="meta-cell">Pick Rate</div>
            <div class="meta-cell">Win Rate</div>
            <div class="meta-cell">Tier</div>
        </div>
    """, unsafe_allow_html=True)

    # Render data rows
    for data in agents_data:
        agent_name = data["name"]
        pick_rate = data["pick_rate"]
        win_rate = data["win_rate"]
        tier = data["tier"]
        
        # Colors
        pick_color = get_color_for_pick_rate(pick_rate)
        win_color = get_color_for_win_rate(win_rate)
        
        # Tier colors
        tier_colors = {
            "S": ("#ffd700", "S — Essential"),
            "A": ("#10b981", "A — Strong"),
            "B": ("#f59e0b", "B — Viable"),
            "C": ("#ff4d6d", "C — Niche"),
        }
        tier_color, tier_label = tier_colors.get(tier, ("#64748b", "?"))
        
        st.markdown(f"""
        <div class="meta-row">
            <div class="meta-cell agent-name-cell">{agent_name}</div>
            <div class="meta-cell stat-cell" style="background-color: {pick_color}22; color: {pick_color};">{pick_rate}%</div>
            <div class="meta-cell stat-cell" style="background-color: {win_color}22; color: {win_color};">{win_rate}%</div>
            <div class="meta-cell tier-cell"><span class="tier-badge" style="background-color: {tier_color}22; border: 1px solid {tier_color}; color: {tier_color};">{tier_label}</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Stats summary
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    s_tier = [a for a in agents_data if a["tier"] == "S"]
    a_tier = [a for a in agents_data if a["tier"] == "A"]
    b_tier = [a for a in agents_data if a["tier"] == "B"]
    c_tier = [a for a in agents_data if a["tier"] == "C"]
    
    with col1:
        st.markdown(f"""
        <div style="background:#ffd70015;border:1px solid #ffd70044;border-radius:10px;padding:16px;text-align:center;">
            <div style="font-size:1.8rem;font-weight:800;color:#ffd700;">{len(s_tier)}</div>
            <div style="font-size:0.75rem;color:#ffd700;font-weight:700;">S TIER</div>
            <div style="font-size:0.65rem;color:#94a3b8;margin-top:4px;">Essential Meta</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background:#10b98115;border:1px solid #10b98144;border-radius:10px;padding:16px;text-align:center;">
            <div style="font-size:1.8rem;font-weight:800;color:#10b981;">{len(a_tier)}</div>
            <div style="font-size:0.75rem;color:#10b981;font-weight:700;">A TIER</div>
            <div style="font-size:0.65rem;color:#94a3b8;margin-top:4px;">Strong Meta</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background:#f59e0b15;border:1px solid #f59e0b44;border-radius:10px;padding:16px;text-align:center;">
            <div style="font-size:1.8rem;font-weight:800;color:#f59e0b;">{len(b_tier)}</div>
            <div style="font-size:0.75rem;color:#f59e0b;font-weight:700;">B TIER</div>
            <div style="font-size:0.65rem;color:#94a3b8;margin-top:4px;">Viable Meta</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background:#ff4d6d15;border:1px solid #ff4d6d44;border-radius:10px;padding:16px;text-align:center;">
            <div style="font-size:1.8rem;font-weight:800;color:#ff4d6d;">{len(c_tier)}</div>
            <div style="font-size:0.75rem;color:#ff4d6d;font-weight:700;">C TIER</div>
            <div style="font-size:0.65rem;color:#94a3b8;margin-top:4px;">Niche Pick</div>
        </div>
        """, unsafe_allow_html=True)

    # Legend
    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.85rem;color:#94a3b8;">
        <strong style="color:#e2e8f0;">📊 How to Read:</strong>
        <ul style="margin-left:16px;margin-top:8px;line-height:1.8;">
            <li><strong style="color:#ffd700;">Pick Rate</strong>: % of pro matches the agent is picked (green = essential, amber = common, red = niche)</li>
            <li><strong style="color:#00d4ff;">Win Rate</strong>: % of matches won with the agent (cyan = strong, purple = neutral, gray = weak)</li>
            <li><strong style="color:#ffd700;">Tier</strong>: VCT classification (S=80%+ pick, A=50-80%, B=20-50%, C=&lt;20%)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

