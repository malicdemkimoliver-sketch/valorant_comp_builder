"""
Landing Page - Official Valorant Media Background
"""
import streamlit as st

def render():
    """Render landing page with Valorant background"""
    
    # Official Valorant background image from their CDN
    valorant_bg = "https://images.contentstack.io/v3/assets/bltfe521ce715202d50/blt5e5c4e0b79274e1e/5eff0002f1b76f0923e48a9b/V_AGENTS_587x900_Jett.png"
    
    # Alternative backgrounds available:
    # - Agents showcase
    # - Abilities showcase  
    # - Game art
    # Using a clean gradient overlay with official Valorant colors
    
    custom_css = """
    <style>
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
    }
    
    @keyframes fade-in {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Main container with Valorant official colors */
    .stMainBlockContainer {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 27, 75, 0.95) 50%, rgba(46, 16, 101, 0.95) 100%),
                    url('https://images.contentstack.io/v3/assets/bltfe521ce715202d50/bltf4bc3fb4e5b5ab96/5eff1589a8a4840923c5d05b/177A5043-Edit.jpg');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    [data-testid="stSidebar"] {
        display: none;
    }
    
    .landing-container {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 40px 20px;
        backdrop-filter: blur(0px);
    }
    
    .landing-content {
        text-align: center;
        max-width: 600px;
        animation: fade-in 0.8s ease-out;
    }
    
    .landing-title {
        font-size: 3.2rem;
        font-weight: 900;
        background: linear-gradient(135deg, #ff4655 0%, #ff8c42 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 16px;
        animation: float 3s ease-in-out infinite;
        letter-spacing: -1px;
    }
    
    .landing-subtitle {
        font-size: 1.1rem;
        color: #e2e8f0;
        margin-bottom: 32px;
        line-height: 1.6;
        font-weight: 400;
    }
    
    .cta-button {
        background: linear-gradient(135deg, #ff4655 0%, #ff6b35 100%);
        color: white;
        padding: 14px 32px;
        border: none;
        border-radius: 4px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 8px 24px rgba(255, 70, 85, 0.3);
        min-width: 280px;
    }
    
    .cta-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 32px rgba(255, 70, 85, 0.4);
    }
    
    .features-container {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
        margin-top: 40px;
        max-width: 420px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .feature-card {
        background: rgba(255, 70, 85, 0.08);
        border: 1px solid rgba(255, 70, 85, 0.2);
        border-radius: 4px;
        padding: 12px 14px;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .feature-card:hover {
        background: rgba(255, 70, 85, 0.12);
        border-color: rgba(255, 70, 85, 0.4);
        transform: translateY(-2px);
    }
    
    .feature-card h4 {
        color: #ff4655;
        margin: 0 0 4px 0;
        font-size: 0.9rem;
        font-weight: 700;
    }
    
    .feature-card p {
        color: #cbd5e1;
        font-size: 0.8rem;
        margin: 0;
        line-height: 1.3;
    }
    
    .footer-text {
        margin-top: 48px;
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 400;
    }
    
    .badge {
        display: inline-block;
        background: rgba(255, 70, 85, 0.15);
        color: #ff8c42;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-top: 8px;
        letter-spacing: 0.5px;
    }
    
    </style>
    """
    
    st.markdown(custom_css, unsafe_allow_html=True)
    
    # Main content
    st.markdown("""
    <div class="landing-container">
        <div class="landing-content">
            <div class="landing-title">VALORANT<br>COMP BUILDER</div>
            <div class="landing-subtitle">
                Create winning team compositions with VCT meta insights.<br>
                Analyze agent picks and build the perfect team.
            </div>
    """, unsafe_allow_html=True)
    
    # Button
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        if st.button("🎯 LET'S BUILD A COMP", use_container_width=True, 
                    key="landing_button"):
            st.session_state.current_page = "builder"
            st.rerun()
    
    # Features
    st.markdown("""
        <div class="features-container">
            <div class="feature-card">
                <h4>🎯 BUILD</h4>
                <p>Create compositions instantly</p>
            </div>
            <div class="feature-card">
                <h4>📊 META</h4>
                <p>VCT pro statistics</p>
            </div>
            <div class="feature-card">
                <h4>💾 SAVE</h4>
                <p>Login to save</p>
            </div>
            <div class="feature-card">
                <h4>📈 ANALYZE</h4>
                <p>Compare agents</p>
            </div>
        </div>
        
        <div class="footer-text">
            <span class="badge">NO LOGIN REQUIRED</span><br>
            Explore all features • Login only to save
        </div>
        </div>
    """, unsafe_allow_html=True)

