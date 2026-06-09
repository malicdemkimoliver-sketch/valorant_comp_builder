"""
Saved Comps Page - View and manage saved compositions
"""
import streamlit as st
import json
from datetime import datetime

def render():
    """Render the saved comps page"""
    st.markdown("""
    <div class="page-title">💾 Saved Compositions</div>
    <div class="page-subtitle">Your collection of team compositions</div>
    """, unsafe_allow_html=True)
    
    if "saved_comps" not in st.session_state:
        st.session_state.saved_comps = []
    
    saved_comps = st.session_state.saved_comps
    
    if not saved_comps:
        st.info("📝 No saved compositions yet. Go to 'Build Composition' to create and save one!")
    else:
        st.markdown(f"### You have {len(saved_comps)} saved composition(s)")
        
        for idx, comp in enumerate(saved_comps):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"""
                <div class="card">
                    <p style='margin:0 0 8px 0; font-weight:600; color:var(--accent-cyan);'>{comp['map']}</p>
                    <p style='margin:0 0 8px 0; font-family:monospace; font-size:0.9rem; color:var(--text-secondary);'>{comp['code']}</p>
                    <p style='margin:0; font-size:0.85rem; color:var(--text-secondary);'>
                        Agents: {', '.join(comp['agents'])}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("📋", key=f"copy_{idx}", help="Copy code"):
                    st.success(f"Copied: {comp['code']}")
            
            with col3:
                if st.button("🗑️", key=f"delete_{idx}", help="Delete"):
                    st.session_state.saved_comps.pop(idx)
                    st.rerun()
        
        # Export all
        st.markdown("### Export All Compositions")
        
        export_json = json.dumps(saved_comps, indent=2)
        
        st.download_button(
            label="📥 Download as JSON",
            data=export_json,
            file_name=f"comps_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
