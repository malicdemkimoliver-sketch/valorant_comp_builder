"""
Meta Tracker Page - VCT statistics and meta analysis
"""
import streamlit as st
import json
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from ..services.comp_encoder import CompEncoder

def load_vct_data():
    """Load VCT meta data"""
    try:
        # Get the path to data file
        current_dir = os.path.dirname(__file__)
        data_path = os.path.join(current_dir, "..", "..", "data", "vct_meta.json")
        
        with open(data_path, 'r') as f:
            return json.load(f)
    except:
        return None

def get_color_for_rate(rate: int) -> str:
    """Get color based on pick rate"""
    if rate >= 80:
        return "#10b981"  # Green - S tier
    elif rate >= 60:
        return "#fbbf24"  # Gold - A tier
    elif rate >= 40:
        return "#f59e0b"  # Orange - B tier
    else:
        return "#ff4d6d"  # Red - C tier

def render():
    """Render the meta tracker page"""
    st.markdown("""
    <div class="page-title">📊 Meta Tracker</div>
    <div class="page-subtitle">VCT Masters London 2026 & Kick Off Statistics</div>
    """, unsafe_allow_html=True)
    
    vct_data = load_vct_data()
    
    if not vct_data:
        st.error("Could not load VCT meta data")
        return
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🔥 Meta Heatmap", "📈 Agent Stats", "🎯 Meta Fit"])
    
    with tab1:
        st.markdown("### Pick Rate Heatmap by Map")
        st.info(f"Data from: {vct_data['series']}")
        
        # Map selector
        maps = list(vct_data["meta_by_map"].keys())
        selected_map = st.selectbox("Select a map:", options=maps, key="meta_map_selector")
        
        if selected_map in vct_data["meta_by_map"]:
            map_data = vct_data["meta_by_map"][selected_map]
            
            # Create heatmap data
            agents = sorted(map_data.keys(), key=lambda x: map_data[x]['pick_rate'], reverse=True)
            pick_rates = [map_data[agent]['pick_rate'] for agent in agents]
            win_rates = [map_data[agent]['win_rate'] for agent in agents]
            tiers = [map_data[agent]['tier'] for agent in agents]
            
            # Create columns for heatmap
            col1, col2, col3 = st.columns([2, 2, 2])
            
            with col1:
                st.markdown("**Agent**")
                for agent in agents:
                    st.markdown(f"{agent}")
            
            with col2:
                st.markdown("**Pick Rate**")
                for i, agent in enumerate(agents):
                    rate = pick_rates[i]
                    color = get_color_for_rate(rate)
                    st.markdown(f"""
                    <div style='background:{color}20; border:1px solid {color}; border-radius:8px; padding:8px; margin:4px 0; text-align:center; font-weight:600; color:{color};'>
                    {rate}%
                    </div>
                    """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("**Win Rate**")
                for i, agent in enumerate(agents):
                    rate = win_rates[i]
                    color = "#00d4ff" if rate > 50 else "#ff4d6d"
                    st.markdown(f"""
                    <div style='background:{color}20; border:1px solid {color}; border-radius:8px; padding:8px; margin:4px 0; text-align:center; font-weight:600; color:{color};'>
                    {rate}%
                    </div>
                    """, unsafe_allow_html=True)
            
            # Legend
            st.markdown("### Tier Definitions")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="card" style="border-left:4px solid #10b981; padding:12px;">
                    <p style='margin:0; font-weight:600; color:#10b981;'>S - Essential</p>
                    <p style='margin:4px 0 0 0; font-size:0.8rem; color:var(--text-secondary);'>80%+ pick rate</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="card" style="border-left:4px solid #fbbf24; padding:12px;">
                    <p style='margin:0; font-weight:600; color:#fbbf24;'>A - Strong</p>
                    <p style='margin:4px 0 0 0; font-size:0.8rem; color:var(--text-secondary);'>50-80% pick rate</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="card" style="border-left:4px solid #f59e0b; padding:12px;">
                    <p style='margin:0; font-weight:600; color:#f59e0b;'>B - Viable</p>
                    <p style='margin:4px 0 0 0; font-size:0.8rem; color:var(--text-secondary);'>20-50% pick rate</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="card" style="border-left:4px solid #ff4d6d; padding:12px;">
                    <p style='margin:0; font-weight:600; color:#ff4d6d;'>C - Niche</p>
                    <p style='margin:4px 0 0 0; font-size:0.8rem; color:var(--text-secondary);'><20% pick rate</p>
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### Agent Statistics Across All Maps")
        
        # Aggregate data across all maps
        agent_stats = {}
        
        for map_name, map_data in vct_data["meta_by_map"].items():
            for agent, stats in map_data.items():
                if agent not in agent_stats:
                    agent_stats[agent] = {
                        "pick_rate": [],
                        "win_rate": [],
                        "appearances": 0
                    }
                
                agent_stats[agent]["pick_rate"].append(stats['pick_rate'])
                agent_stats[agent]["win_rate"].append(stats['win_rate'])
                agent_stats[agent]["appearances"] += 1
        
        # Calculate averages
        for agent in agent_stats:
            agent_stats[agent]["avg_pick_rate"] = round(
                sum(agent_stats[agent]["pick_rate"]) / len(agent_stats[agent]["pick_rate"])
            )
            agent_stats[agent]["avg_win_rate"] = round(
                sum(agent_stats[agent]["win_rate"]) / len(agent_stats[agent]["win_rate"]), 1
            )
        
        # Sort by average pick rate
        sorted_agents = sorted(
            agent_stats.items(),
            key=lambda x: x[1]["avg_pick_rate"],
            reverse=True
        )
        
        # Display as table
        df_data = []
        for agent, stats in sorted_agents:
            df_data.append({
                "Agent": agent,
                "Avg Pick Rate": f"{stats['avg_pick_rate']}%",
                "Avg Win Rate": f"{stats['avg_win_rate']}%",
                "Map Appearances": stats['appearances']
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    with tab3:
        st.markdown("### Meta Fit Score")
        st.info("Compare your composition against the current VCT meta")
        
        # Select map and agents
        selected_map = st.selectbox("Select map:", options=list(vct_data["meta_by_map"].keys()), key="metafit_map")
        
        available_agents = CompEncoder.get_available_agents()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            agent1 = st.selectbox("Agent 1:", options=available_agents, key="metafit_agent1")
        with col2:
            agent2 = st.selectbox("Agent 2:", options=available_agents, key="metafit_agent2")
        with col3:
            agent3 = st.selectbox("Agent 3:", options=available_agents, key="metafit_agent3")
        
        col1, col2 = st.columns(2)
        with col1:
            agent4 = st.selectbox("Agent 4:", options=available_agents, key="metafit_agent4")
        with col2:
            agent5 = st.selectbox("Agent 5:", options=available_agents, key="metafit_agent5")
        
        selected_agents = [agent1, agent2, agent3, agent4, agent5]
        
        if len(set(selected_agents)) == 5:  # All unique
            # Calculate meta fit
            map_meta = vct_data["meta_by_map"].get(selected_map, {})
            
            total_pick_rate = 0
            agent_scores = []
            
            for agent in selected_agents:
                if agent in map_meta:
                    pick_rate = map_meta[agent]['pick_rate']
                    total_pick_rate += pick_rate
                    agent_scores.append({
                        "agent": agent,
                        "pick_rate": pick_rate,
                        "tier": map_meta[agent]['tier']
                    })
                else:
                    agent_scores.append({
                        "agent": agent,
                        "pick_rate": 0,
                        "tier": "U"
                    })
            
            # Calculate meta fit score
            avg_pick_rate = total_pick_rate / 5
            
            # Score interpretation
            if avg_pick_rate >= 80:
                fit_score = "S - Pro Meta"
                color = "#10b981"
            elif avg_pick_rate >= 70:
                fit_score = "A - High Meta"
                color = "#fbbf24"
            elif avg_pick_rate >= 50:
                fit_score = "B - Medium Meta"
                color = "#f59e0b"
            else:
                fit_score = "C - Low Meta"
                color = "#ff4d6d"
            
            st.markdown(f"""
            <div class="card" style="border-left:6px solid {color};">
                <p style='margin:0 0 8px 0; color:var(--text-secondary); font-size:0.9rem;'>Meta Fit Score</p>
                <p style='margin:0; font-size:1.8rem; font-weight:700; color:{color};'>{fit_score}</p>
                <p style='margin:8px 0 0 0; color:var(--text-secondary); font-size:0.9rem;'>Average Pick Rate: {avg_pick_rate:.0f}%</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Agent breakdown
            st.markdown("### Agent Meta Alignment")
            
            for agent_score in agent_scores:
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**{agent_score['agent']}**")
                
                with col2:
                    pick_rate = agent_score['pick_rate']
                    st.markdown(f"Pick: **{pick_rate}%**")
                
                with col3:
                    tier = agent_score['tier']
                    tier_color = {
                        "S": "#10b981",
                        "A": "#fbbf24",
                        "B": "#f59e0b",
                        "C": "#ff4d6d",
                        "U": "#94a3b8"
                    }.get(tier, "#94a3b8")
                    
                    st.markdown(f"""
                    <div style='text-align:center; color:{tier_color};'>
                    <strong>{tier} Tier</strong>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Please select 5 unique agents")
