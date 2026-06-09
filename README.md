# 🎯 Gyd's Comp Helper

A premium Valorant team composition builder and analyzer.

[[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://malicdemkimoliver-sketch-valorant-comp-builder-app-XXXXX.streamlit.app)](https://gyd-comp-maker.streamlit.app/)

## Features

- 🗺️ **Map-first 3-step builder** — select map → pick agents → analyze
- 🖼️ **Agent avatars** — locally generated SVG portraits, no external API
- 📊 **Live comp scoring** — 0–100 score with role balance, map fit, synergy
- 🎯 **Pro presets** — 5 per map, tiered S→F by real VCT 2025 win rates
- 🔗 **Synergy finder** — suggests agents that complete your comp
- ⚠️ **Similarity alert** — warns when you're building a known pro comp
- 💾 **Save & export** — JSON download + PNG image with pros/cons analysis
- 📌 **Sticky team bar** — selected agents freeze while you scroll

## Deploy on Streamlit Community Cloud (free)

1. Fork or push this repo to your GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"Create app"** → **"Yup, I have an app"**
4. Set **Repository** to `malicdemkimoliver-sketch/valorant_comp_builder`
5. Set **Branch** to `main`
6. Set **Main file path** to `app.py`
7. Click **Deploy** — live in ~2 minutes ✅

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project structure

```
valorant_comp_builder/
  app.py                    ← Streamlit entrypoint
  requirements.txt
  .streamlit/
    config.toml             ← Theme + server config
  data/
    agents.json             ← 27 agents with roles, maps, synergy tags
    maps.json               ← 11 maps with features and bias
    rules.json              ← Scoring weights and penalties
    saved_comps.json        ← Your saved compositions
  assets/
    agent_portraits.py      ← Local SVG portrait generator (offline)
  app/
    models/                 ← Agent and Comp dataclasses
    services/               ← Scoring, validator, recommender, data loader
    ui/                     ← Builder, database, saved comps, rules editor
```

## Scoring system

| Category | Max | Description |
|---|---|---|
| Role Balance | 25 | Controller + Initiator + Sentinel + 1-2 Duelists |
| Map Fit | 20 | Agents on their good_maps list |
| Agent Synergy | 20 | Shared synergy tags between agents |
| Utility Coverage | 15 | Smokes, recon, flash, post-plant |
| Attack Strength | 10 | Entry fraggers + aggressive utility |
| Defense Strength | 10 | Anchors + flank control |

*Made with 🎮 by GYDRENZIN*
