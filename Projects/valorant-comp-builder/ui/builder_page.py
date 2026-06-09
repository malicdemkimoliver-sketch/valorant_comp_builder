"""
Builder Page - Build and encode team compositions
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from ..services.comp_encoder import CompEncoder

def render():
    """Render the builder page"""
    st.markdown("""
    <div class="page-title">🎯 Build Composition</div>
    <div class="page-subtitle">Create, analyze, and share team compositions</div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["🎮 Builder", "📋 Load Code", "📊 Analysis"])
    
    with tab1:
        st.markdown("### Step 1: Select Map")
        
        maps = CompEncoder.get_available_maps()
        selected_map = st.selectbox(
            "Choose a map:",
            options=maps,
            key="builder_map",
            help="Select the map for your composition"
        )
        
        st.markdown("### Step 2: Select Agents")
        st.info("Select 5 agents for your team composition")
        
        available_agents = CompEncoder.get_available_agents()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            agent1 = st.selectbox("Agent 1", options=available_agents, key="agent1")
        
        with col2:
            agent2 = st.selectbox("Agent 2", options=available_agents, key="agent2")
        
        with col3:
            agent3 = st.selectbox("Agent 3", options=available_agents, key="agent3")
        
        col4, col5 = st.columns(2)
        
        with col4:
            agent4 = st.selectbox("Agent 4", options=available_agents, key="agent4")
        
        with col5:
            agent5 = st.selectbox("Agent 5", options=available_agents, key="agent5")
        
        # Check for duplicates
        selected_agents = [agent1, agent2, agent3, agent4, agent5]
        if len(set(selected_agents)) != 5:
            st.warning("⚠️ You have duplicate agents! Each agent must be unique.")
        else:
            st.markdown("### Step 3: Generate Code")
            
            try:
                # Generate comp code
                comp_code = CompEncoder.encode(selected_map, selected_agents)
                
                st.markdown(f"""
                <div class="card">
                    <p style='margin:0 0 12px 0; color:var(--text-secondary); font-size:0.9rem;'>Your Comp Code:</p>
                    <p style='margin:0; font-family:monospace; font-size:1.1rem; color:var(--accent-cyan); font-weight:600; word-break:break-all;'>{comp_code}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Copy button
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📋 Copy to Clipboard", key="btn_copy_comp", use_container_width=True):
                        st.success(f"✅ Copied: {comp_code}")
                
                with col2:
                    if st.button("💾 Save Composition", key="btn_save_comp", use_container_width=True):
                        if "saved_comps" not in st.session_state:
                            st.session_state.saved_comps = []
                        
                        comp_data = {
                            "code": comp_code,
                            "map": selected_map,
                            "agents": selected_agents,
                            "timestamp": str(__import__("datetime").datetime.now())
                        }
                        st.session_state.saved_comps.append(comp_data)
                        st.success("✅ Composition saved! View in 'Saved Comps'")
                
                # Show agent roles and info
                st.markdown("### Composition Details")
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                agent_info = {
                    "Jett": ("Duelist", "⚔️"),
                    "Reyna": ("Duelist", "⚔️"),
                    "Raze": ("Duelist", "⚔️"),
                    "Phoenix": ("Duelist", "⚔️"),
                    "Yoru": ("Duelist", "⚔️"),
                    "Neon": ("Duelist", "⚔️"),
                    "Iso": ("Duelist", "⚔️"),
                    "Omen": ("Controller", "💨"),
                    "Astra": ("Controller", "💨"),
                    "Brimstone": ("Controller", "💨"),
                    "Harbor": ("Controller", "💨"),
                    "Vyse": ("Controller", "💨"),
                    "Sova": ("Initiator", "🔍"),
                    "Breach": ("Initiator", "🔍"),
                    "Skye": ("Initiator", "🔍"),
                    "Fade": ("Initiator", "🔍"),
                    "Gekko": ("Initiator", "🔍"),
                    "Twitch": ("Initiator", "🔍"),
                    "Sage": ("Sentinel", "🛡️"),
                    "Killjoy": ("Sentinel", "🛡️"),
                    "Cypher": ("Sentinel", "🛡️"),
                    "Chamber": ("Sentinel", "🛡️"),
                    "Clove": ("Sentinel", "🛡️"),
                    "KAY/O": ("Initiator", "🔍"),
                }
                
                agents_with_i = [(agent, i+1) for i, agent in enumerate(selected_agents)]
                
                for i, (agent_name, agent_num) in enumerate(agents_with_i):
                    with st.columns(5)[i]:
                        role, icon = agent_info.get(agent_name, ("Unknown", "❓"))
                        st.markdown(f"""
                        <div class="card" style="text-align:center; padding:16px;">
                            <p style='margin:0; font-size:1.2rem;'>{icon}</p>
                            <p style='margin:8px 0 4px 0; font-weight:600; color:var(--accent-cyan);'>{agent_name}</p>
                            <p style='margin:0; font-size:0.8rem; color:var(--text-secondary);'>{role}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error generating code: {str(e)}")
    
    with tab2:
        st.markdown("### Load Composition from Code")
        st.info("Paste a comp code to load the agents and map")
        
        comp_code_input = st.text_input(
            "Enter comp code:",
            placeholder="Example: VAL-2-AC-JT-OM-KJ-SK-SG",
            help="Paste a code like: VAL-2-AC-JT-OM-KJ-SK-SG"
        )
        
        if comp_code_input:
            try:
                loaded_map, loaded_agents = CompEncoder.decode(comp_code_input)
                
                st.success(f"✅ Loaded: {loaded_map} with {len(loaded_agents)} agents")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Map:** {loaded_map}")
                
                with col2:
                    st.markdown("**Agents:**")
                    st.write(", ".join(loaded_agents))
                
                # Show in builder
                if st.button("📌 Load into Builder", key="btn_load_into_builder"):
                    st.session_state.builder_map = loaded_map
                    st.session_state.agent1 = loaded_agents[0]
                    st.session_state.agent2 = loaded_agents[1]
                    st.session_state.agent3 = loaded_agents[2]
                    st.session_state.agent4 = loaded_agents[3]
                    st.session_state.agent5 = loaded_agents[4]
                    st.success("✅ Loaded into builder! Scroll up to see.")
                    st.rerun()
                
            except Exception as e:
                st.error(f"❌ Invalid code: {str(e)}")
    
    with tab3:
        st.markdown("### Composition Analysis")
        st.info("Analysis features coming soon!")
        st.markdown("""
        - Role balance check
        - Ability coverage analysis
        - Meta fit score (compared to VCT data)
        - Map synergy analysis
        """)
