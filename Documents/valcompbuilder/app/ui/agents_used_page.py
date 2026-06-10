"""
Agents Used Page - Display user's agent statistics from tracker.gg
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.services.tracker_gg_scraper import get_player_agents_used, compare_with_meta, get_best_agents_for_player
from app.services.meta_service import get_all_meta_agents_for_map

def render():
    """Render agents used page"""
    
    st.markdown('<h1 class="page-title">📊 Your Agents Stats</h1>', unsafe_allow_html=True)
    
    # Check authentication - works with both email and Google login
    if not st.session_state.get("user_logged_in", False) and not st.session_state.get("user_info"):
        st.error("⚠️ Please login first to access this page")
        return
    
    st.markdown("""
    Enter your Riot ID to see your personal agent statistics across all maps.
    This pulls data from tracker.gg and shows you how your agents compare to the meta.
    """)
    
    # Input section
    col1, col2, col3 = st.columns(3)
    with col1:
        riot_name = st.text_input(
            "Riot Name",
            placeholder="YourName",
            key="riot_name_input"
        )
    with col2:
        tagline = st.text_input(
            "Tagline",
            placeholder="NA1",
            key="tagline_input",
            max_chars=5
        )
    with col3:
        search_button = st.button("🔍 Get Stats", use_container_width=True)
    
    if search_button:
        if not riot_name or not tagline:
            st.error("❌ Please enter both Riot Name and Tagline")
        else:
            render_player_stats(riot_name, tagline)

def render_player_stats(riot_name: str, tagline: str):
    """Display player's agent statistics"""
    
    with st.spinner(f"Fetching stats for {riot_name}#{tagline}..."):
        agent_stats = get_player_agents_used(riot_name, tagline)
    
    if "error" in agent_stats:
        st.error(f"❌ {agent_stats['error']}")
        return
    
    if not agent_stats:
        st.warning("⚠️ No agent data found. Make sure you've played at least a few games.")
        return
    
    # Display summary
    st.markdown(f"### {riot_name}#{tagline} - Agent Statistics")
    
    # Get best agents
    best_agents = get_best_agents_for_player(agent_stats)
    
    if best_agents:
        col1, col2, col3 = st.columns(3)
        with col1:
            best = best_agents[0]
            st.metric(
                "🏆 Best Agent",
                best["agent"],
                f"{best['win_rate']:.1f}% WR"
            )
        with col2:
            st.metric(
                "📊 Total Agents",
                len(agent_stats),
                "agents played"
            )
        with col3:
            avg_wr = sum(a.get("win_rate", 0) for a in agent_stats.values()) / len(agent_stats)
            st.metric(
                "📈 Avg Win Rate",
                f"{avg_wr:.1f}%",
                "across agents"
            )
    
    # Detailed agent table
    st.markdown("### Agent Breakdown")
    
    # Create table data
    table_data = []
    for agent_name in sorted(agent_stats.keys()):
        stats = agent_stats[agent_name]
        table_data.append({
            "Agent": agent_name,
            "Pick Rate": f"{stats.get('pick_rate', 0):.1f}%",
            "Win Rate": f"{stats.get('win_rate', 0):.1f}%",
            "K/D": f"{stats.get('kd_ratio', 0):.2f}"
        })
    
    # Display as table
    if table_data:
        st.dataframe(table_data, use_container_width=True)
    
    # Agent comparison with meta
    st.markdown("### vs Meta Comparison")
    
    selected_map = st.selectbox(
        "Select map to compare with meta",
        ["Ascent", "Haven", "Split", "Breeze", "Fracture", "Icebox", "Lotus", "Pearl", "Bind"],
        key="meta_comparison_map"
    )
    
    meta_for_map = get_all_meta_agents_for_map(selected_map)
    
    if meta_for_map:
        comparison_data = []
        for agent_name in sorted(agent_stats.keys()):
            if agent_name in meta_for_map:
                player_stats = agent_stats[agent_name]
                meta_stats = meta_for_map[agent_name]
                
                player_wr = player_stats.get("win_rate", 0)
                meta_wr = meta_stats.get("win_rate", 50)
                diff = player_wr - meta_wr
                
                # Emoji indicator
                if diff > 3:
                    emoji = "🟢"
                    status = "Above Meta"
                elif diff > -3:
                    emoji = "🟡"
                    status = "In Line"
                else:
                    emoji = "🔴"
                    status = "Below Meta"
                
                comparison_data.append({
                    "Agent": agent_name,
                    "Your WR": f"{player_wr:.1f}%",
                    "Meta WR": f"{meta_wr:.1f}%",
                    "Diff": f"{diff:+.1f}%",
                    "Status": f"{emoji} {status}"
                })
        
        if comparison_data:
            st.dataframe(comparison_data, use_container_width=True)
    
    # Recommendations
    st.markdown("### 💡 Recommendations")
    
    if best_agents:
        st.success(f"**Play {best_agents[0]['agent']}** - You have the highest win rate on this agent!")
        
        if len(best_agents) > 1:
            st.info(f"**Backup pick:** {best_agents[1]['agent']} ({best_agents[1]['win_rate']:.1f}% WR)")
    
    # Export option
    if st.button("📥 Export Stats as CSV"):
        csv_data = "Agent,Pick Rate %,Win Rate %,K/D\n"
        for agent_name, stats in agent_stats.items():
            csv_data += f"{agent_name},{stats.get('pick_rate', 0):.1f},{stats.get('win_rate', 0):.1f},{stats.get('kd_ratio', 0):.2f}\n"
        
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=f"{riot_name}_{tagline}_agents.csv",
            mime="text/csv"
        )

