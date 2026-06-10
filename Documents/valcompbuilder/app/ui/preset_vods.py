"""
Preset VOD Component — expandable detail under each preset comp.

Shows: comp win rate, a comp tier derived from that win rate, and links to
find VODs of the team running the comp (YouTube/Twitch/VLR searches built
from the team + event + map, so they always resolve to real results).

Usage in builder_page.py — right below where each preset is displayed:

    from app.ui.preset_vods import render_preset_vods
    render_preset_vods(preset, map_name)   # preset = the dict with name/agents/source
"""
import re
from urllib.parse import quote_plus
from typing import Optional

import streamlit as st

# WR → comp tier (this is the preset tier list ranking)
COMP_TIERS = [
    (75, "S", "#ff4655", "Dominant comp"),
    (65, "A", "#ff8c42", "Strong comp"),
    (55, "B", "#ffd700", "Solid comp"),
    (0,  "C", "#64748b", "Situational comp"),
]

# Official team channels where known (fallback = search)
TEAM_CHANNELS = {
    "G2 Esports": {"twitch": "https://www.twitch.tv/g2esports"},
    "FNATIC": {"twitch": "https://www.twitch.tv/fnatic"},
    "Paper Rex": {"twitch": "https://www.twitch.tv/pprxteam"},
    "Sentinels": {"twitch": "https://www.twitch.tv/sentinels"},
    "Cloud9": {"twitch": "https://www.twitch.tv/cloud9"},
    "Team Liquid": {"twitch": "https://www.twitch.tv/teamliquid"},
    "100T": {"twitch": "https://www.twitch.tv/100thieves"},
}


def _parse_source(source: str) -> dict:
    """'G2 Esports · VCT Americas 2025 · 83% WR' → team/event/wr"""
    parts = [p.strip() for p in source.split("·")]
    team = parts[0] if parts else ""
    event = parts[1] if len(parts) > 1 else ""
    wr = None
    m = re.search(r"(\d+)\s*%\s*WR", source)
    if m:
        wr = int(m.group(1))
    return {"team": team, "event": event, "wr": wr}


def _comp_tier(wr: Optional[int]):
    if wr is None:
        return None, "#64748b", "Unranked"
    for threshold, tier, color, label in COMP_TIERS:
        if wr >= threshold:
            return tier, color, label
    return "C", "#64748b", "Situational comp"


def render_preset_vods(preset: dict, map_name: str):
    """
    Expandable VOD/details section for one preset comp.
    preset: {"name": ..., "agents": [...], "description": ..., "source": ...}
    """
    info = _parse_source(preset.get("source", ""))
    team, event, wr = info["team"], info["event"], info["wr"]
    tier, color, tier_label = _comp_tier(wr)

    title = f"📺 VODs & details — {team or preset.get('name','')}"
    if wr is not None:
        title += f" ({wr}% WR"
        if tier:
            title += f" · {tier} Tier"
        title += ")"

    with st.expander(title):
        # ── Comp tier banner ──
        if wr is not None:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                <div style="background:{color};color:#0b0f1a;font-weight:800;
                            padding:3px 14px;border-radius:6px;font-size:1rem;">
                    {tier} TIER COMP
                </div>
                <span style="color:#94a3b8;font-size:0.85rem;">
                    {tier_label} · {wr}% win rate · {event}
                </span>
            </div>
            """, unsafe_allow_html=True)

        agents_line = " · ".join(preset.get("agents", []))
        st.markdown(f"**Composition:** {agents_line}")
        if preset.get("description"):
            st.markdown(f"*{preset['description']}*")

        # ── VOD links (search-based: always resolve to real results) ──
        st.markdown("**Watch this comp in action:**")
        q_yt = quote_plus(f"{team} {map_name} {event} highlights")
        q_yt_full = quote_plus(f"{team} {map_name} {event} full match VOD")
        q_vlr = quote_plus(team)

        links = [
            f"- ▶️ [YouTube — {team} {map_name} highlights](https://www.youtube.com/results?search_query={q_yt})",
            f"- 🎬 [YouTube — full match VODs](https://www.youtube.com/results?search_query={q_yt_full})",
            f"- 📊 [VLR.gg — {team} match history & stats](https://www.vlr.gg/search/?q={q_vlr})",
        ]
        ch = TEAM_CHANNELS.get(team)
        if ch and ch.get("twitch"):
            links.append(f"- 🟣 [Twitch — {team} channel]({ch['twitch']})")
        else:
            q_tw = quote_plus(f"{team} valorant")
            links.append(f"- 🟣 [Twitch — search {team}](https://www.twitch.tv/search?term={q_tw})")

        st.markdown("\n".join(links))
        st.caption("Links open search results for this team and map — pick the most recent match to see the comp played.")
