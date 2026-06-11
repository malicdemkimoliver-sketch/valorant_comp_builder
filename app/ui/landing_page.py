"""
Landing page V3 — professional, modern, properly spaced.
Fixes from V2: scroll indicator no longer overlaps the title (hero is a
flex column with the indicator as a flow item, not absolutely overlapping),
and the CTA button below the feature cards has generous breathing room.
"""
import streamlit as st

BG_IMAGE = "https://media.valorant-api.com/maps/7eaecc1b-4337-bbf6-6ab9-04b8f06b3319/splash.png"


def render():
    st.markdown(f"""
    <style>
      [data-testid="stSidebar"], header {{ display: none !important; }}
      .block-container {{ padding: 0 !important; max-width: 100% !important; }}

      /* ── HERO ── */
      .vlp-hero {{
        min-height: 92vh; display: flex; flex-direction: column;
        align-items: center; justify-content: center; position: relative;
        background:
          linear-gradient(135deg, rgba(15,25,35,0.90) 0%, rgba(26,35,50,0.84) 50%, rgba(45,27,61,0.90) 100%),
          url('{BG_IMAGE}') center/cover no-repeat;
        text-align: center; padding: 40px 24px 70px;
      }}
      .vlp-title {{
        font-family:'Rajdhani','Segoe UI',sans-serif; font-weight: 900; letter-spacing: 4px;
        font-size: clamp(2.4rem, 7vw, 5rem); line-height: 1.08; margin: 0;
        animation: vlp-float 3.5s ease-in-out infinite;
      }}
      .vlp-title .red    {{ color:#ff4655; text-shadow:0 4px 24px rgba(255,70,85,0.4); }}
      .vlp-title .orange {{ color:#ff8c42; text-shadow:0 4px 24px rgba(255,140,66,0.35); }}
      .vlp-sub {{
        color:#cbd5e1; font-size: clamp(0.95rem, 2.2vw, 1.18rem);
        max-width: 600px; margin: 22px auto 0; line-height: 1.6;
      }}
      @keyframes vlp-float {{ 0%,100%{{transform:translateY(0)}} 50%{{transform:translateY(-9px)}} }}

      .vlp-badge {{
        display:inline-block; margin-top: 26px; padding: 6px 18px; border-radius: 20px;
        border:1px solid #10b981; color:#10b981; font-size:0.72rem;
        letter-spacing:2.5px; font-weight:700;
      }}

      /* ── Scroll indicator: now a normal flow item with margin, no overlap ── */
      .vlp-scroll {{
        margin-top: 54px; display:flex; flex-direction:column; align-items:center; gap:2px;
        color:#94a3b8; font-size:0.72rem; letter-spacing:3px; text-transform:uppercase;
      }}
      .vlp-scroll .chev {{
        font-size:1.5rem; color:#ff4655; line-height:0.6;
        animation: vlp-bounce 1.6s ease-in-out infinite;
      }}
      @keyframes vlp-bounce {{ 0%,100%{{transform:translateY(0);opacity:.6}} 50%{{transform:translateY(7px);opacity:1}} }}

      /* ── Feature grid (responsive) ── */
      .vlp-features {{
        display:grid; gap:16px; padding: 52px 6vw 30px;
        grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
        background:#0f1923;
      }}
      .vlp-card {{
        border:1px solid rgba(255,70,85,0.22); border-radius:14px;
        padding: clamp(16px, 2.5vw, 26px); background:rgba(255,255,255,0.025);
        transition: transform .2s, border-color .2s, box-shadow .2s;
      }}
      .vlp-card:hover {{
        transform:translateY(-5px); border-color:#ff4655;
        box-shadow:0 12px 28px rgba(255,70,85,0.12);
      }}
      .vlp-card .ic {{ font-size: clamp(1.5rem, 3vw, 2.1rem); }}
      .vlp-card .nm {{ color:#ff4655; font-weight:800; letter-spacing:2.5px;
                       font-size: clamp(0.9rem, 1.8vw, 1.08rem); margin: 10px 0 6px; }}
      .vlp-card .ds {{ color:#94a3b8; font-size: clamp(0.74rem, 1.5vw, 0.86rem); line-height:1.5; }}

      /* ── CTA wrapper: breathing room top & bottom ── */
      .vlp-cta-zone {{ background:#0f1923; padding: 14px 6vw 60px; }}
      div[data-testid="stButton"] > button {{
        font-family:'Rajdhani','Segoe UI',sans-serif; font-weight:800; letter-spacing:2px;
        font-size:1.05rem; padding:14px 0; border-radius:12px;
      }}
    </style>

    <div class="vlp-hero">
        <h1 class="vlp-title"><span class="red">VALORANT</span><br>
            <span class="orange">COMP BUILDER</span></h1>
        <p class="vlp-sub">Create winning team compositions with VCT meta insights.
           Analyze agent picks and build the perfect team.</p>
        <div class="vlp-badge">🔓 NO LOGIN REQUIRED</div>
        <div class="vlp-scroll">
            <span>Scroll down</span>
            <span class="chev">⌄</span>
        </div>
    </div>

    <div class="vlp-features">
        <div class="vlp-card"><div class="ic">🎯</div><div class="nm">BUILD</div>
            <div class="ds">Pick 5 agents and get an instant comp score with grade and breakdown.</div></div>
        <div class="vlp-card"><div class="ic">📊</div><div class="nm">META</div>
            <div class="ds">Live tier lists per map — win rates and pick rates from real data.</div></div>
        <div class="vlp-card"><div class="ic">💾</div><div class="nm">SAVE</div>
            <div class="ds">Keep your best comps in your account and revisit them anytime.</div></div>
        <div class="vlp-card"><div class="ic">🔍</div><div class="nm">ANALYZE</div>
            <div class="ds">Strengths, weaknesses, warnings, and suggested picks for every comp.</div></div>
    </div>
    """, unsafe_allow_html=True)

    # CTA — wrapped with spacing above and below
    st.markdown('<div class="vlp-cta-zone">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.4, 1])
    with c2:
        if st.button("🎮 LET'S BUILD A COMP!", use_container_width=True, type="primary"):
            st.session_state.current_page = "builder"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
