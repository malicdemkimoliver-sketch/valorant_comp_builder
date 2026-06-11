"""
Agent Suggestion Service — recommends agents that complete the current comp.

Reads agents.json directly (bypasses any hardcoded loader data) and uses
meta_service V3 tiers. For each candidate it builds bulleted PROS and CONS
explaining why it would (or wouldn't) finish the composition.

Usage in builder_page.py — after the user has selected 1-4 agents:

    from app.services.suggestion_service import render_agent_suggestions
    render_agent_suggestions(selected_agent_names, selected_map)
"""
import json
import os
from typing import Dict, List

try:
    import streamlit as st
except ImportError:
    st = None  # suggest_agents() works headless; render needs streamlit

try:
    from app.services.meta_service import get_agent_tier, get_agent_meta_for_map, is_meta_loaded
    _META = True
except Exception:
    _META = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AGENTS_PATH = os.path.join(BASE_DIR, "data", "agents.json")

RECON_UTIL = {"recon-bolt", "drone", "haunt", "camera", "tripwire", "trademark",
              "prowler", "trailblazer", "sonic-sensor", "alarmbot"}
FLASH_UTIL = {"flash", "paranoia", "blind"}
POST_PLANT_UTIL = {"nanoswarm", "snake-bite", "shock-dart", "orbital", "molotov",
                   "grenades", "razorvine", "guided-salvo"}
VISION_BLOCK = {"smokes", "wall", "orb", "cove", "cascade"}
ANCHOR_TAGS = {"anchor", "site-control"}
FLANK_TAGS = {"flank-control"}

_profiles = None


def _load_profiles() -> Dict[str, dict]:
    global _profiles
    if _profiles is None:
        try:
            with open(AGENTS_PATH, "r", encoding="utf-8") as f:
                raw = json.load(f)
            _profiles = {a["name"]: a for a in raw}
        except Exception:
            _profiles = {}
    return _profiles


def _team_state(selected: List[dict]) -> dict:
    """What the current selection already covers."""
    roles = [a.get("role", "") for a in selected]
    tags, util = set(), set()
    for a in selected:
        tags.update(a.get("synergy_tags", []))
        util.update(a.get("utility", []))
    return {
        "roles": roles,
        "duelists": roles.count("Duelist"),
        "has_controller": "Controller" in roles,
        "has_initiator": "Initiator" in roles,
        "has_sentinel": "Sentinel" in roles,
        "has_smokes": any(a.get("role") == "Controller"
                          and set(a.get("utility", [])) & VISION_BLOCK
                          for a in selected),
        "has_recon": bool(util & RECON_UTIL),
        "has_flash": bool(util & FLASH_UTIL),
        "has_post_plant": bool(util & POST_PLANT_UTIL),
        "has_entry": "entry" in tags,
        "has_anchor": bool(tags & ANCHOR_TAGS),
        "has_flank": bool(tags & FLANK_TAGS),
        "tags": tags,
    }


def suggest_agents(selected_names: List[str], map_name: str, top_n: int = 3) -> List[dict]:
    """
    Returns top_n suggestions: [{name, role, tier, wr, pr, score, pros, cons}]
    """
    profiles = _load_profiles()
    selected = [profiles[n] for n in selected_names if n in profiles]
    if not selected or len(selected) >= 5:
        return []

    state = _team_state(selected)
    results = []

    for name, agent in profiles.items():
        if name in selected_names:
            continue

        role = agent.get("role", "")
        a_tags = set(agent.get("synergy_tags", []))
        a_util = set(agent.get("utility", []))
        pros, cons, score = [], [], 0.0

        # ── Role need ──
        if role == "Controller" and not state["has_controller"]:
            score += 25; pros.append("Fills your missing **Controller** slot — smokes enable site executes")
        elif role == "Initiator" and not state["has_initiator"]:
            score += 20; pros.append("Fills your missing **Initiator** slot — opening utility and info")
        elif role == "Sentinel" and not state["has_sentinel"]:
            score += 20; pros.append("Fills your missing **Sentinel** slot — site anchor and flank watch")
        elif role == "Duelist" and state["duelists"] == 0:
            score += 18; pros.append("Adds your first **Duelist** — someone to take opening duels")
        elif role == "Duelist" and state["duelists"] >= 2:
            score -= 15; cons.append(f"Would be your **{state['duelists']+1}rd Duelist** — comp loses utility")
        elif role in [a.get("role") for a in selected]:
            cons.append(f"Role overlap — you already have a {role}")

        # ── Utility gaps it fills ──
        if not state["has_smokes"] and role == "Controller" and (a_util & VISION_BLOCK):
            score += 10; pros.append("Brings **smokes/vision-block** — currently missing")
        if not state["has_recon"] and (a_util & RECON_UTIL):
            score += 8; pros.append("Adds **recon** — your comp is playing blind right now")
        if not state["has_flash"] and (a_util & FLASH_UTIL):
            score += 7; pros.append("Adds **flashes** — enables entries and retakes")
        if not state["has_post_plant"] and (a_util & POST_PLANT_UTIL):
            score += 5; pros.append("Adds **post-plant utility** — helps close out rounds")
        if not state["has_entry"] and "entry" in a_tags:
            score += 6; pros.append("Adds an **entry threat** — someone has to open sites")
        if not state["has_flank"] and (a_tags & FLANK_TAGS):
            score += 4; pros.append("Adds **flank control** — protects your team's back")
        if not state["has_anchor"] and (a_tags & ANCHOR_TAGS):
            score += 4; pros.append("Adds a **site anchor** for defense")

        # ── Map fit & meta ──
        tier, wr, pr = None, None, None
        if map_name in agent.get("good_maps", []):
            score += 8; pros.append(f"**{map_name}** is one of {name}'s best maps")
        else:
            cons.append(f"{map_name} isn't in {name}'s strongest map pool")

        if _META and is_meta_loaded():
            tier = get_agent_tier(name, map_name)
            stats = get_agent_meta_for_map(name, map_name) or {}
            wr, pr = stats.get("win_rate"), stats.get("pick_rate")
            if tier == "S":
                score += 12; pros.append(f"**S-tier meta pick** on {map_name} ({wr}% WR · {pr}% PR in pro play)")
            elif tier == "A":
                score += 8; pros.append(f"**A-tier meta pick** on {map_name} ({wr}% WR · {pr}% PR)")
            elif tier == "C":
                score -= 4; cons.append(f"Off-meta on {map_name} in current pro play ({pr}% pick rate)")

        # ── Synergy with selected agents ──
        shared = a_tags & state["tags"]
        if shared:
            score += min(len(shared) * 1.5, 5)
            pros.append(f"Playstyle synergy with your picks: *{', '.join(sorted(shared)[:3])}*")

        if not pros:
            cons.append("Doesn't address any current gap in this comp")

        results.append({
            "name": name, "role": role, "tier": tier, "wr": wr, "pr": pr,
            "score": round(score, 1), "pros": pros[:4], "cons": cons[:2],
        })

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top_n]


# ── Streamlit UI component ───────────────────────────────────────────────────
ROLE_COLORS = {"Duelist": "#ff4d6d", "Controller": "#7c3aed",
               "Initiator": "#0ea5e9", "Sentinel": "#10b981"}


def render_agent_suggestions(selected_names: List[str], map_name: str):
    """Drop-in UI: call from builder_page after the agent selection grid."""
    if not selected_names or len(selected_names) >= 5:
        return

    suggestions = suggest_agents(selected_names, map_name, top_n=3)
    if not suggestions:
        return

    st.markdown("### 💡 Suggested next picks")
    st.caption(f"Based on your {len(selected_names)} selected agent(s) and the {map_name} meta")

    cols = st.columns(len(suggestions))
    for col, s in zip(cols, suggestions):
        rc = ROLE_COLORS.get(s["role"], "#94a3b8")
        tier_badge = f" · {s['tier']} tier" if s["tier"] else ""
        with col:
            st.markdown(f"""
            <div style="border:1px solid {rc}55;border-top:3px solid {rc};
                        border-radius:10px;padding:12px 14px;background:rgba(255,255,255,0.02);">
                <div style="font-weight:800;font-size:1.05rem;">{s['name']}</div>
                <div style="color:{rc};font-size:0.75rem;margin-bottom:6px;">
                    {s['role']}{tier_badge}
                </div>
            </div>
            """, unsafe_allow_html=True)
            for p in s["pros"]:
                st.markdown(f"- ✅ {p}")
            for c in s["cons"]:
                st.markdown(f"- ⚠️ {c}")
