"""
Local agent image assets — fully offline SVG portraits embedded as base64 data URIs.
Generated once at import time and cached — no external API calls ever needed.

Portrait design: role-colored radial gradient background, large emoji icon,
name pill, decorative ring. Loads instantly from memory.
"""
import base64

# ── Role color palette ─────────────────────────────────────────────────────────
_RC = {
    "Duelist":    "#ff4d6d",
    "Controller": "#7c3aed",
    "Initiator":  "#0ea5e9",
    "Sentinel":   "#10b981",
}

def _agent_svg(name: str, icon: str, color: str) -> str:
    short = name if len(name) <= 8 else name[:7] + "…"
    # Lighter accent for the glow
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
  <defs>
    <radialGradient id="g" cx="50%" cy="38%" r="62%">
      <stop offset="0%" stop-color="{color}" stop-opacity="0.45"/>
      <stop offset="100%" stop-color="#020817" stop-opacity="1"/>
    </radialGradient>
  </defs>
  <circle cx="64" cy="64" r="64" fill="#0a1628"/>
  <circle cx="64" cy="64" r="64" fill="url(#g)"/>
  <circle cx="64" cy="64" r="62" fill="none" stroke="{color}" stroke-width="2.5" stroke-opacity="0.55"/>
  <circle cx="64" cy="64" r="52" fill="none" stroke="{color}" stroke-width="1" stroke-opacity="0.18"/>
  <path d="M18 100 A52 52 0 0 1 110 100" fill="none" stroke="{color}" stroke-width="3" stroke-opacity="0.4" stroke-linecap="round"/>
  <text x="64" y="68" font-size="44" text-anchor="middle" dominant-baseline="middle"
        font-family="Segoe UI Emoji,Apple Color Emoji,Noto Color Emoji,sans-serif">{icon}</text>
  <rect x="12" y="92" width="104" height="22" rx="11" fill="{color}" fill-opacity="0.2"/>
  <rect x="12" y="92" width="104" height="22" rx="11" fill="none" stroke="{color}" stroke-width="1" stroke-opacity="0.5"/>
  <text x="64" y="107" font-size="11.5" font-weight="700" text-anchor="middle"
        font-family="Segoe UI,Arial,sans-serif" fill="#e2e8f0" letter-spacing="0.8">{short}</text>
  <circle cx="18" cy="18" r="2.5" fill="{color}" opacity="0.5"/>
  <circle cx="110" cy="18" r="2.5" fill="{color}" opacity="0.5"/>
</svg>'''
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def _map_svg(name: str, icon: str, bias: str, color: str) -> str:
    bc = {"attack": "#ff4d6d", "defense": "#10b981", "balanced": "#0ea5e9"}.get(bias, "#0ea5e9")
    bias_label = {"attack": "ATK", "defense": "DEF", "balanced": "BAL"}.get(bias, "BAL")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="320" height="90" viewBox="0 0 320 90">
  <defs>
    <linearGradient id="mg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{color}" stop-opacity="0.3"/>
      <stop offset="55%" stop-color="#0a1628" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="#020817" stop-opacity="1"/>
    </linearGradient>
  </defs>
  <rect width="320" height="90" rx="10" fill="#0a1628"/>
  <rect width="320" height="90" rx="10" fill="url(#mg)"/>
  <line x1="0" y1="30" x2="320" y2="30" stroke="{color}" stroke-opacity="0.06" stroke-width="1"/>
  <line x1="0" y1="60" x2="320" y2="60" stroke="{color}" stroke-opacity="0.06" stroke-width="1"/>
  <line x1="107" y1="0" x2="107" y2="90" stroke="{color}" stroke-opacity="0.06" stroke-width="1"/>
  <line x1="213" y1="0" x2="213" y2="90" stroke="{color}" stroke-opacity="0.06" stroke-width="1"/>
  <text x="160" y="46" font-size="34" text-anchor="middle" dominant-baseline="middle"
        font-family="Segoe UI Emoji,Apple Color Emoji,Noto Color Emoji,sans-serif" opacity="0.6">{icon}</text>
  <text x="160" y="74" font-size="12" font-weight="700" text-anchor="middle"
        font-family="Segoe UI,Arial,sans-serif" fill="{color}" opacity="0.28" letter-spacing="3.5">{name.upper()}</text>
  <rect x="6" y="6" width="36" height="18" rx="9" fill="{bc}" fill-opacity="0.25"/>
  <rect x="6" y="6" width="36" height="18" rx="9" fill="none" stroke="{bc}" stroke-width="1" stroke-opacity="0.6"/>
  <text x="24" y="17" font-size="9" font-weight="700" text-anchor="middle"
        font-family="Segoe UI,Arial,sans-serif" fill="{bc}">{bias_label}</text>
  <line x1="0" y1="0" x2="28" y2="0" stroke="{color}" stroke-width="2" opacity="0.6" stroke-linecap="round"/>
  <line x1="0" y1="0" x2="0" y2="18" stroke="{color}" stroke-width="2" opacity="0.6" stroke-linecap="round"/>
  <line x1="320" y1="90" x2="292" y2="90" stroke="{color}" stroke-width="1.5" opacity="0.35" stroke-linecap="round"/>
  <line x1="320" y1="90" x2="320" y2="72" stroke="{color}" stroke-width="1.5" opacity="0.35" stroke-linecap="round"/>
</svg>'''
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


# ── Agent roster ───────────────────────────────────────────────────────────────
_ROSTER = [
    # (name, icon, role)
    ("Jett",      "🌪️", "Duelist"),
    ("Raze",      "💥", "Duelist"),
    ("Neon",      "⚡", "Duelist"),
    ("Reyna",     "👁️", "Duelist"),
    ("Phoenix",   "🔥", "Duelist"),
    ("Yoru",      "👺", "Duelist"),
    ("Iso",       "🔵", "Duelist"),
    ("Waylay",    "🌀", "Duelist"),
    ("Omen",      "👻", "Controller"),
    ("Brimstone", "🪖", "Controller"),
    ("Viper",     "☠️", "Controller"),
    ("Astra",     "🌟", "Controller"),
    ("Clove",     "🍀", "Controller"),
    ("Harbor",    "🌊", "Controller"),
    ("Sova",      "🏹", "Initiator"),
    ("Fade",      "🌑", "Initiator"),
    ("Breach",    "🤜", "Initiator"),
    ("Skye",      "🦅", "Initiator"),
    ("Gekko",     "🦎", "Initiator"),
    ("KAY/O",     "🤖", "Initiator"),
    ("Tejo",      "🎖️", "Initiator"),
    ("Killjoy",   "🔧", "Sentinel"),
    ("Cypher",    "🕵️", "Sentinel"),
    ("Sage",      "💚", "Sentinel"),
    ("Deadlock",  "🔒", "Sentinel"),
    ("Chamber",   "🎯", "Sentinel"),
    ("Vyse",      "🌿", "Sentinel"),
]

# ── Map roster ─────────────────────────────────────────────────────────────────
_MAPS = [
    ("Ascent",   "🏛️", "balanced", "#0ea5e9"),
    ("Breeze",   "🌊", "balanced", "#06b6d4"),
    ("Fracture", "⚡", "attack",   "#ff4d6d"),
    ("Haven",    "🌿", "attack",   "#10b981"),
    ("Lotus",    "🌸", "balanced", "#ec4899"),
    ("Pearl",    "🦪", "defense",  "#8b5cf6"),
    ("Split",    "🏙️", "defense",  "#f59e0b"),
    ("Bind",     "🏜️", "attack",   "#f97316"),
    ("Icebox",   "🧊", "defense",  "#60a5fa"),
    ("Sunset",   "🌅", "balanced", "#fb923c"),
    ("Abyss",    "🌌", "balanced", "#a78bfa"),
]

# ── Pre-generate everything at import time (cached in memory) ──────────────────
AGENT_PORTRAITS: dict = {
    name: _agent_svg(name, icon, _RC[role])
    for name, icon, role in _ROSTER
}

MAP_SPLASHES: dict = {
    name: _map_svg(name, icon, bias, color)
    for name, icon, bias, color in _MAPS
}

# Quick lookup: agent name → role color
AGENT_ROLE_COLORS: dict = {
    name: _RC[role] for name, icon, role in _ROSTER
}

# Quick lookup: agent name → emoji icon
AGENT_ICONS: dict = {
    name: icon for name, icon, role in _ROSTER
}
