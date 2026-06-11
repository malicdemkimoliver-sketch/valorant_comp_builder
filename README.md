# GYDRENZIN Valorant Comp Builder v2.0

**Professional team composition builder with VCT meta analytics**

![Status](https://img.shields.io/badge/status-production-green)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-blue)

---

## ✨ Features

### 🎯 Build Composition
- Select map and 5 agents
- **Encode compositions into short codes** (e.g., `VAL-2-AC-JT-OM-KJ-SK-SG`)
- **Copy codes to share via Discord** - fully client-side, no server needed
- **Load comps from codes** - paste a code to instantly load agents and map
- Role visualization (Duelist, Controller, Initiator, Sentinel)
- Save compositions for later

### 💾 Saved Compositions
- Store all your built comps locally
- View, copy, and delete saved compositions
- Export as JSON backup
- Access from any session

### 📊 Meta Tracker
- **VCT Masters London 2026 + Kick Off statistics**
- **Interactive heatmap**: Agents (rows) × Maps (columns) with pick rates
- Color-coded tiers: S (80%+) → A (50-80%) → B (20-50%) → C (<20%)
- Agent statistics across all maps
- **Meta Fit Score**: Compare your comp against pro meta on each map
- See how closely you align with VCT strategies

### 👤 Account Settings
- Google login integration (placeholder for OAuth)
- Profile management
- Saved data overview
- Privacy-focused design

---

## 🚀 Quick Start

### Installation

```bash
# Clone or download the project
cd valorant_comp_builder_v2

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

**Access:** Open browser to `http://localhost:8501`

---

## 📁 Project Structure

```
valorant_comp_builder_v2/
├── app.py                          # Main application
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── builder_page.py        # Build & encode comps
│   │   ├── saved_comps_page.py    # View saved comps
│   │   ├── meta_tracker_page.py   # VCT stats & heatmap
│   │   └── account_page.py        # User settings
│   └── services/
│       ├── __init__.py
│       └── comp_encoder.py        # Encode/decode comps
└── data/
    └── vct_meta.json              # VCT statistics
```

---

## 🔑 Key Features Explained

### Comp Encoding System

**Example:**
- **Map:** Ascent
- **Agents:** Jett, Omen, Killjoy, Skye, Sage
- **Code:** `VAL-2-AC-JT-OM-KJ-SK-SG`

**Format:** `VAL-VERSION-MAP-AGENT1-AGENT2-AGENT3-AGENT4-AGENT5`

**Agent Codes:**
```
Jett (JT), Omen (OM), Killjoy (KJ), Skye (SK), Sage (SG),
Astra (AT), Breach (BR), Brimstone (BM), Chamber (CH), 
Cypher (CY), Fade (FD), Gekko (GK), Harbor (HB), Phoenix (PX),
Raze (RZ), Reyna (RN), Viper (VP), Yoru (YR), KAY/O (KO),
Neon (NE), Rift (RF), Twitch (TW), Iso (IS), Clove (CL), Vyse (VY)
```

**Map Codes:**
```
Ascent (AC), Bind (BD), Breeze (BZ), Fracture (FR), Haven (HV),
Icebox (IB), Lotus (LT), Pearl (PL), Split (SP)
```

### Meta Tracker Data

**VCT Statistics Include:**
- **Pick Rates:** How often each agent is picked in pro matches
- **Win Rates:** Average win rate with that agent
- **Tier Classification:** S/A/B/C based on meta strength
- **Map-Specific Data:** Different agents dominate different maps

**Example - Ascent Meta:**
- **S Tier:** Jett (92%), Omen (88%)
- **A Tier:** Killjoy (78%), Skye (72%), Sage (68%)
- **B Tier:** Astra (45%), Breach (38%)
- **C Tier:** Cypher (22%), Chamber (15%), Raze (12%)

### Meta Fit Score

**How It Works:**
1. Select map and 5 agents
2. App calculates average pick rate
3. Displays score: S/A/B/C tier
4. Shows how each agent aligns with meta

**Example:**
```
Your Comp: Ascent with Jett, Omen, Killjoy, Skye, Sage
Average Pick Rate: 82%
Meta Fit: S - Pro Meta (closely aligned with pro play)
```

---

## 🎮 Usage Examples

### Share a Comp on Discord

```
1. Build: Ascent → Jett, Omen, Killjoy, Skye, Sage
2. Copy code: VAL-2-AC-JT-OM-KJ-SK-SG
3. Share: "VAL-2-AC-JT-OM-KJ-SK-SG"
4. Teammate pastes code → Loads instantly
```

### Check Meta Alignment

```
1. Go to Meta Tracker
2. Select: Breeze map
3. View heatmap: See Jett is #1 (98% pick rate)
4. Compare your comp's fit score
5. Decide: Stick with meta or counter-pick
```

### Save Your Best Comp

```
1. Build composition
2. Click "Save Composition"
3. View in "Saved Comps"
4. Export as JSON backup
```

---

## 🔧 Configuration

### Customize VCT Data

Edit `data/vct_meta.json` to:
- Update pick rates per patch
- Add new agents
- Modify tier classifications
- Change map-specific meta

**Format:**
```json
{
  "last_updated": "2026-06-09",
  "series": "VCT Masters London 2026 + Kick Off",
  "meta_by_map": {
    "Ascent": {
      "Jett": {
        "pick_rate": 92,
        "win_rate": 55,
        "tier": "S"
      }
    }
  }
}
```

---

## 🔐 Data Privacy

- **Client-Side Only:** All comp encoding/decoding happens in browser
- **No Server Required:** Share codes via Discord/text without backend
- **Local Storage:** Comps saved to session (optional: implement DB)
- **No Tracking:** No analytics or telemetry

---

## 🚀 Future Features

- [ ] Google OAuth integration (currently placeholder)
- [ ] Cloud database for comp storage
- [ ] Real-time VCT data syncing
- [ ] Comp rating/voting system
- [ ] Team composition history
- [ ] Advanced analytics (counter-picks, ability combos)
- [ ] Mobile app
- [ ] Community comp sharing

---

## 🛠️ Development

### Add New Agents

1. Add to `comp_encoder.py`:
   ```python
   AGENT_CODES = {
       "NewAgent": "NA",
   }
   ```

2. Update `vct_meta.json` with meta data

3. Update `builder_page.py` agent roles

### Update VCT Meta

Edit `data/vct_meta.json` after each VCT patch:
- Update pick rates
- Adjust tier classifications
- Add new agents if released

### Add Comp Analysis

Extend `builder_page.py` analysis tab:
- Role balance checker
- Ability coverage validator
- Synergy analyzer

---

## 📊 VCT Data Source

- **VCT Masters London 2026** - Latest international championship
- **Kick Off Statistics** - Regional circuit data
- Data is manually curated per patch
- Updated every 2 weeks (patch cycle)

---

## 🐛 Troubleshooting

### "Comp code won't load"
- Check code format: `VAL-2-AC-JT-OM-KJ-SK-SG`
- Verify all agent codes are 2 letters
- Ensure map code is valid

### "Comps not saving"
- Reload page or clear cache
- Check browser storage (Streamlit session)
- Comps are stored locally only (implement DB for persistence)

### "Meta data not showing"
- Verify `data/vct_meta.json` exists
- Check JSON syntax is valid
- Ensure all required fields are present

---

## 📞 Support

**Common Questions:**

**Q: Can I export my comps?**
A: Yes! Go to "Saved Comps" and download as JSON

**Q: How often is VCT data updated?**
A: After each VCT patch (typically bi-weekly). Edit `vct_meta.json` to update.

**Q: Do I need a database?**
A: Not required! Everything works client-side. Add a database when you implement Google login.

**Q: Can I share codes offline?**
A: Yes! Codes are fully client-side. Share via Discord, email, text - no server needed.

---

## 📄 License

Built with 🎮 by GYDRENZIN

---

## Version History

### v2.0 (Current)
- ✅ Sidebar navigation (left side)
- ✅ Comp encoding/decoding system
- ✅ Copy/paste comp codes
- ✅ VCT meta tracker with heatmap
- ✅ Meta fit score calculator
- ✅ Saved comps management
- ✅ Account settings structure
- ✅ Clean, professional UI

### v1.0
- Original comp builder
- Basic features

---

**Ready to build? Run `streamlit run app.py` 🎯⚔️**
