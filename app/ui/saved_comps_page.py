"""Saved Comps Page - User-specific saved compositions with database"""
import streamlit as st
import json
from app.services.database import get_user_comps, delete_comp

def render():
    st.markdown('<h1 class="page-title">💾 Saved Comps</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Your saved team compositions</p>', unsafe_allow_html=True)
    
    if not st.session_state.get("user_logged_in"):
        st.error("❌ Please login to view saved comps")
        return
    
    user_email = st.session_state.user_email
    comps = get_user_comps(user_email)
    
    if not comps:
        st.markdown("""
        <div style="text-align:center;padding:40px;color:#475569;">
            <div style="font-size:2rem;margin-bottom:10px;">📭</div>
            <div>No saved comps yet.</div>
            <div style="font-size:0.9rem;margin-top:8px;">Build and save a comp from the Builder!</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown(f"**You have {len(comps)} saved comp(s)**")
    st.markdown("---")
    
    for idx, comp in enumerate(comps):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"**{comp.get('name', 'Unnamed')}**")
            agents_str = ", ".join(comp.get('agents', []))
            score = comp.get('score', 0)
            grade = comp.get('grade', '?')
            st.caption(f"🗺️ {comp.get('map', 'Unknown')} · Score: {score} ({grade}) · {agents_str}")
            if comp.get('notes'):
                st.write(f"*{comp['notes'][:100]}...*" if len(comp['notes']) > 100 else f"*{comp['notes']}*")
        
        with col2:
            if st.button("📋 Code", key=f"copy_{idx}", use_container_width=True):
                code = comp.get('code', '')
                st.success(f"Copied: {code}")
        
        with col3:
            if st.button("🗑️ Delete", key=f"delete_{idx}", use_container_width=True):
                delete_comp(user_email, comp.get('id'))
                st.success("Deleted!")
                st.rerun()
        
        st.markdown("---")
    
    # Export all
    if st.button("📥 Export All as JSON", use_container_width=False):
        st.download_button(
            "Download",
            json.dumps(comps, indent=2),
            f"saved_comps_{user_email.split('@')[0]}.json",
            "application/json"
        )
