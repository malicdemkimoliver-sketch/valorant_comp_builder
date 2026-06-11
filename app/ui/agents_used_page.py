"""
Your Agent Stats Page - Disabled Temporarily
"""
import streamlit as st

def render():
    st.markdown('<h1 class="page-title">📊 Your Agent Stats</h1>', unsafe_allow_html=True)
    
    st.info("""
    **📊 Agent Stats Feature - Coming Soon**
    
    We're currently working on integrating tracker.gg data. 
    Check back soon for real-time agent statistics!
    
    **For now, use:**
    - 🎯 **Build Composition** - Create and score teams
    - 📈 **Meta Tracker** - View VCT pro player meta
    """)
    
    st.markdown("### 📋 Example Stats")
    st.write("When enabled, you'll see your personal agent win rates, K/D ratios, and pick rates compared to the VCT meta.")

