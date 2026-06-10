"""
Mobile-Responsive Builder Page
Uses Streamlit columns and conditional layouts for mobile/desktop
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.services.data_loader import load_agents, load_maps
from app.services.scoring_improved import score_comp_improved, get_score_label, get_score_color
from app.services.session_manager import init_session, is_logged_in, get_user

def init_responsive_state():
    """Initialize responsive state"""
    init_session()
    
    if "selected_agents" not in st.session_state:
        st.session_state.selected_agents = []
    if "builder_step" not in st.session_state:
        st.session_state.builder_step = 1
    if "builder_map" not in st.session_state:
        st.session_state.builder_map = "Haven"
    if "is_mobile" not in st.session_state:
        st.session_state.is_mobile = False

def get_screen_width():
    """Get estimated screen width"""
    # Streamlit default is 880px, mobile is typically < 600px
    return st.session_state.get("screen_width", 880)

def is_mobile() -> bool:
    """Check if viewing on mobile"""
    # Simple check: use session state or estimate
    return st.session_state.is_mobile or get_screen_width() < 600

def render_responsive():
    """Main responsive builder render"""
    init_responsive_state()
    
    # Check authentication
    if not is_logged_in():
        st.error("⚠️ Please login first")
        return
    
    user = get_user()
    st.markdown(f'<h1 class="page-title">⚙️ Comp Builder</h1>', unsafe_allow_html=True)
    
    # Mobile indicator
    if is_mobile():
        st.info("📱 Mobile Mode - Optimized Layout")
    else:
        st.info("💻 Desktop Mode")
    
    # STEP 1: MAP SELECTION
    if st.session_state.builder_step == 1:
        render_step1_map_selection()
    
    # STEP 2: AGENT SELECTION
    elif st.session_state.builder_step == 2:
        render_step2_agent_selection()
    
    # STEP 3: ANALYSIS
    elif st.session_state.builder_step == 3:
        render_step3_analysis()

def render_step1_map_selection():
    """Step 1 - Map Selection (Mobile Responsive)"""
    st.markdown("### Step 1: Select Map")
    
    maps = [
        ("Ascent", "🏛️"), ("Haven", "🌿"), ("Split", "⚙️"),
        ("Breeze", "❄️"), ("Fracture", "⚡"), ("Icebox", "🧊"),
        ("Lotus", "🌸"), ("Pearl", "🔵"), ("Bind", "🌈")
    ]
    
    if is_mobile():
        # Mobile: single column
        for map_name, icon in maps:
            if st.button(f"{icon} {map_name}", key=f"map_{map_name}", use_container_width=True):
                st.session_state.builder_map = map_name
                st.session_state.builder_step = 2
                st.rerun()
    else:
        # Desktop: 3 columns
        cols = st.columns(3)
        for idx, (map_name, icon) in enumerate(maps):
            with cols[idx % 3]:
                if st.button(f"{icon}\n{map_name}", key=f"map_{map_name}", use_container_width=True):
                    st.session_state.builder_map = map_name
                    st.session_state.builder_step = 2
                    st.rerun()

def render_step2_agent_selection():
    """Step 2 - Agent Selection (Mobile Responsive)"""
    st.markdown(f"### Step 2: Select Agents - {st.session_state.builder_map}")
    
    agents = load_agents()
    selected_agents = st.session_state.selected_agents
    
    # Role filter
    st.markdown("**Filter by Role:**")
    roles = ["All", "Duelist", "Controller", "Initiator", "Sentinel"]
    
    if is_mobile():
        selected_role = st.selectbox("Select role", roles, key="role_filter")
    else:
        role_cols = st.columns(len(roles))
        selected_role = "All"
        for col, role in enumerate(roles):
            with role_cols[col]:
                if st.button(role, use_container_width=True):
                    selected_role = role
    
    # Filter agents
    if selected_role != "All":
        agents = [a for a in agents if a.role == selected_role]
    
    # Agent grid (responsive)
    if is_mobile():
        grid_cols = 1
    else:
        grid_cols = 5
    
    st.markdown("**Available Agents:**")
    cols = st.columns(grid_cols)
    
    for idx, agent in enumerate(agents):
        col = cols[idx % grid_cols]
        with col:
            if agent in selected_agents:
                button_label = f"✅ {agent.name}"
                button_key = f"unselect_{agent.name}"
                action = "remove"
            else:
                button_label = f"⭕ {agent.name}"
                button_key = f"select_{agent.name}"
                action = "add"
            
            if st.button(button_label, use_container_width=True, key=button_key):
                if action == "add" and len(selected_agents) < 5:
                    selected_agents.append(agent)
                    st.session_state.selected_agents = selected_agents
                    st.rerun()
                elif action == "remove":
                    selected_agents.remove(agent)
                    st.session_state.selected_agents = selected_agents
                    st.rerun()
    
    # Show selected agents
    if selected_agents:
        st.markdown(f"**Selected ({len(selected_agents)}/5):**")
        if is_mobile():
            for agent in selected_agents:
                st.write(f"✓ {agent.name} ({agent.role})")
        else:
            cols = st.columns(5)
            for idx, agent in enumerate(selected_agents):
                with cols[idx]:
                    st.write(f"✓ {agent.name}")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.builder_step = 1
            st.rerun()
    with col2:
        if len(selected_agents) == 5:
            if st.button("Next →", use_container_width=True):
                st.session_state.builder_step = 3
                st.rerun()
        else:
            st.write(f"⏳ Select {5 - len(selected_agents)} more")

def render_step3_analysis():
    """Step 3 - Analysis (Mobile Responsive)"""
    st.markdown(f"### Step 3: Analysis - {st.session_state.builder_map}")
    
    agents = st.session_state.selected_agents
    map_name = st.session_state.builder_map
    
    # Calculate score
    score, grade, breakdown = score_comp_improved(agents, map_name)
    
    # Score display
    col1, col2, col3 = st.columns(3) if not is_mobile() else st.columns(1)
    
    with col1 if not is_mobile() else st.container():
        st.metric("Score", f"{score}/100")
    if not is_mobile():
        with col2:
            st.metric("Grade", grade)
        with col3:
            st.metric("Label", get_score_label(score))
    else:
        st.metric("Grade", grade)
        st.metric("Label", get_score_label(score))
    
    # Breakdown
    st.markdown("**Score Breakdown:**")
    for category, points in breakdown.items():
        st.progress(points / 25, text=f"{category}: {points}")
    
    # Agents info
    st.markdown("**Composition:**")
    if is_mobile():
        for agent in agents:
            st.write(f"• {agent.name} ({agent.role})")
    else:
        cols = st.columns(5)
        for idx, agent in enumerate(agents):
            with cols[idx]:
                st.write(f"**{agent.name}**\n{agent.role}")
    
    # Actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.builder_step = 2
            st.rerun()
    with col2:
        if st.button("📥 Save", use_container_width=True):
            st.success("Composition saved!")
    with col3:
        if st.button("📷 Export PNG", use_container_width=True):
            st.info("Exporting...")

def render():
    """Main entry point"""
    render_responsive()

