# Gyd's VLR Comp Builder

**Official documentation** — a Valorant team-composition builder with live scoring, VCT pro-meta analytics, shareable comp codes, and Google-account comp saving. Branded **GYDRENZIN**.

The app is a **Next.js frontend + FastAPI backend**. (The original Streamlit app is still in the repo as a legacy fallback — see [Legacy Streamlit app](#legacy-streamlit-app).)

---

## Table of contents

1. [Tech stack](#tech-stack)
2. [Architecture](#architecture)
3. [User guide — how to use the app](#user-guide)
4. [Getting started (run it locally)](#getting-started)
5. [Configuration](#configuration)
6. [API reference](#api-reference)
7. [Data & meta refresh](#data--meta-refresh)
8. [Authentication & security model](#authentication--security-model)
9. [Comp code format](#comp-code-format)
10. [Deployment](#deployment)
11. [Legacy Streamlit app](#legacy-streamlit-app)

---

## Tech stack

### Frontend (`frontend/`)

| Technology | Version | Used for |
|---|---|---|
| [Next.js](https://nextjs.org) (App Router) | 16.2 | Framework — server components, route handlers, API proxy rewrites |
| [React](https://react.dev) | 19.2 | UI |
| [TypeScript](https://www.typescriptlang.org) | 5 | Type safety |
| [Tailwind CSS](https://tailwindcss.com) | 4 | Styling (custom navy/crimson Valorant theme in `globals.css`) |
| [NextAuth.js](https://authjs.dev) | v5 (beta) | Google sign-in, JWT sessions |
| [html-to-image](https://github.com/bubkoo/html-to-image) | 1.11 | PNG export of comp cards |
| clsx + tailwind-merge + class-variance-authority | — | Class composition utilities |
| ESLint 9 + eslint-config-next | — | Linting |

### Backend (`backend/`, `app/services/`)

| Technology | Version | Used for |
|---|---|---|
| [Python](https://www.python.org) | 3.14 | Runtime |
| [FastAPI](https://fastapi.tiangolo.com) | 0.136 | REST API (`backend/main.py` + routers) |
| [Uvicorn](https://www.uvicorn.org) | 0.49 | ASGI server |
| [Pydantic](https://docs.pydantic.dev) | 2 | Request/response validation |
| requests + BeautifulSoup4 | — | Meta scraping (MetaBot / vstats) |

### Data sources

| Source | Used for |
|---|---|
| [valorant-api.com](https://valorant-api.com) | Canonical agent roster, portraits, abilities, map art (`backend/valorant_api.py`, 24 h disk cache in `data/cache/`, offline fallback) |
| `data/agents.json` | Curated overlay — synergy tags, map affinity, utility classes powering the scoring engine |
| `data/vct_meta.json` | VCT pick-rate / win-rate meta (scraped from MetaBot via `app/services/meta_scraper.py`) |
| `data/team_comps.json` | **Hand-curated** pro team comps from VCT Masters London 2026 (vlr.gg research, validated VOD links) — never touched by generators |
| `data/presets.json` | Archetype presets, **data-derived** per map by `tools/generate_presets.py` |
| `data/db.json` | Saved comps + users (gitignored — contains user emails) |

---

## Architecture

```
Browser
  │
  ▼
Next.js (port 3000) ──────────────────────────────┐
  ├─ /, /builder, /meta, /saved   (pages)          │
  ├─ /api/auth/*    NextAuth (Google OAuth)        │
  ├─ /api/saved*    session-checked route handlers ─┼─► X-User-Email ─► FastAPI /api/saved-comps
  └─ /api/*         rewrite proxy (everything else) ┴───────────────► FastAPI (port 8000)
                                                                        │
                                                          app/services/ (scoring, suggestions,
                                                          meta, database)  +  data/*.json
                                                                        │
                                                          valorant-api.com / MetaBot (cached)
```

Repo layout:

```
backend/        FastAPI app: main.py, routers/, catalog.py, valorant_api.py, meta_refresh.py
frontend/       Next.js app: src/app (pages + API routes), src/components, src/lib
app/services/   Python domain logic shared with the legacy Streamlit app
                (scoring, suggestion_service, meta_service, meta_scraper, database, comp_encoder)
data/           All JSON data + cache (db.json and cache/ are gitignored)
tools/          Data maintenance scripts (generate_presets, update_meta_from_metabot, …)
app.py          Legacy Streamlit entry point
```

---

## User guide

### Home (`/`)

Landing page with the GYDRENZIN branding and a call-to-action into the builder.

### Builder (`/builder`)

The core single-screen experience. Everything updates live as you click.

1. **Pick a map** from the map strip at the top. The header shows the selected map (and "NO META DATA" for maps without VCT stats).
2. **Pick 5 agents** from the agent grid. Agents carry **meta tier badges** (S/A/B/C) for the selected map. Selected agents are highlighted in green and appear in the comp slots; click again (or use the slot ✕) to remove. **Reset** clears the comp.
3. **Pro team comps** — a tier list of the best-performing real VCT comps for the selected map (S ≥ 75 % / A ≥ 65 % / B ≥ 55 % win rate, Masters London 2026 Swiss Stage). Expand a comp for the **VOD link**, or click **load** to put it straight into your slots.
4. **Presets** — data-derived archetype comps for the map, one click to load.
5. **Score panel** (sidebar) — your comp is scored live (0–100 with a letter grade) across six categories: Role Balance (25), Map Fit (20), Agent Synergy (20), Utility Coverage (15), Attack Strength (10), Defense Strength (10) — scoring engine V4 in `app/services/scoring.py`. With fewer than 5 agents, the **Suggestions** panel recommends who to add next — click a suggestion to add them.
6. **Share** — with 5 agents picked you get a compact comp code (see [format](#comp-code-format)). **COPY CODE** / **COPY LINK** share it; paste any code into the input and **LOAD** to restore that comp. The page URL also stays shareable at all times (`/builder?map=…&agents=…`).
7. **Save** — when signed in, name the comp (notes optional) and hit **SAVE COMP** to store it to your account. Signed out, the panel tells you to sign in first.
8. **Export** — download your comp as a branded PNG image (great for Discord).

### Meta tracker (`/meta`)

Per-map VCT meta tier list. Pick a map and browse agents grouped into **S / A / B / C / NR** tiers; each entry shows **win rate** and **pick rate** (color-coded). Tiers blend win rate, pick rate, and curation. A **refresh** button re-scrapes the latest MetaBot stats (the backend also auto-refreshes stale data on startup). Filter/search to find specific agents.

### Saved comps (`/saved`)

- **Signed out:** a sign-in prompt.
- **Signed in:** all your saved comps as cards — name, map, agent list, grade/score, notes, comp code, and save date. Each card has **LOAD IN BUILDER** (restores the comp on the right map) and **Delete**.

### Signing in

Click **Sign in** in the top-right nav → Google OAuth → you're back with your avatar and name in the nav. Your email is the account key; comps are stored server-side in `data/db.json`. **Sign out** from the same spot.

---

## Getting started

### Prerequisites

- **Node.js** 20+ and npm
- **Python** 3.12+ (project venv uses 3.14)
- A **Google OAuth client** (only needed for sign-in/saved comps — see [Configuration](#configuration))

### 1. Backend

```powershell
# from the repo root
python -m venv .venv
.venv\Scripts\pip install -r backend\requirements.txt
.venv\Scripts\python -m uvicorn backend.main:app --reload --port 8000
```

On first start the backend warms its valorant-api.com cache and auto-refreshes meta data if stale. Check it's alive: `http://localhost:8000/api/health` (interactive API docs at `http://localhost:8000/docs`).

### 2. Frontend

```powershell
cd frontend
npm install
# create .env.local first — see Configuration below
npm run dev
```

Open **http://localhost:3000**.

### Useful commands

| Command | Where | What |
|---|---|---|
| `npm run dev` / `build` / `start` | `frontend/` | Dev server / production build / serve build |
| `npm run lint`, `npx tsc --noEmit` | `frontend/` | Lint and type-check |
| `.venv\Scripts\python -m uvicorn backend.main:app --reload --port 8000` | repo root | Backend dev server |
| `.venv\Scripts\python tools\generate_presets.py` | repo root | Regenerate archetype presets (also runs on meta refresh) |

---

## Configuration

`frontend/.env.local`:

```ini
# FastAPI base URL (used by the server-side proxy and route handlers)
API_URL=http://localhost:8000

# NextAuth — generate with: npx auth secret
AUTH_SECRET=<random 32+ byte secret>

# Google OAuth (Google Cloud Console → APIs & Services → Credentials)
AUTH_GOOGLE_ID=<client id>.apps.googleusercontent.com
AUTH_GOOGLE_SECRET=<client secret>

# Optional, deployment only — must match the backend env var of the same name
# BACKEND_SHARED_SECRET=<random secret>
```

**Google OAuth setup (one time):** in [Google Cloud Console](https://console.cloud.google.com) create an OAuth 2.0 Client ID (type: Web application) and add
`http://localhost:3000/api/auth/callback/google` to **Authorized redirect URIs** (plus your production URL later). Paste the ID/secret into `.env.local`. Without these, the whole app works except sign-in and saved comps.

Backend env (both optional locally, required in production):

- `BACKEND_SHARED_SECRET` — when set, FastAPI rejects saved-comps requests that don't carry the matching `X-Backend-Secret` header (see [security model](#authentication--security-model)).
- `DB_PATH` — absolute path for the saved-comps database (default `data/db.json`). Point it at a persistent volume in production, e.g. `/data/db.json`.

---

## API reference

FastAPI on port 8000. The Next.js dev/prod server proxies `/api/*` to it **except** `/api/auth/*` (NextAuth) and `/api/saved*` (session-checked Next route handlers).

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/agents` | Full agent roster (merged valorant-api.com + curated overlay) |
| GET | `/api/agents/{name}` | One agent |
| GET | `/api/maps` | Maps with art, active-pool and has-meta-data flags |
| GET | `/api/maps/{name}` | One map |
| POST | `/api/score` | Score a comp — body `{ agents: string[], map: string }` → score, grade, breakdown |
| POST | `/api/suggest` | Suggest next agents for a partial comp |
| GET | `/api/presets` | Data-derived archetype presets per map |
| GET | `/api/team-comps` | Hand-curated VCT pro comps per map (with VOD links) |
| GET | `/api/meta/status` | Meta data freshness / refresh state |
| POST | `/api/meta/refresh` | Re-scrape MetaBot stats (async; poll status) |
| GET | `/api/meta/{map}` | Tiered meta (S/A/B/C with win/pick rates) for one map |
| GET | `/api/saved-comps` | List the user's saved comps † |
| POST | `/api/saved-comps` | Save a comp † |
| DELETE | `/api/saved-comps/{id}` | Delete a saved comp † |

† Requires the `X-User-Email` header — only ever set server-side by the Next.js route handlers (`/api/saved`, `/api/saved/[id]`) after verifying the NextAuth session. Browsers cannot reach these through the proxy.

---

## Data & meta refresh

- **Meta stats** (`data/vct_meta.json`) are scraped from MetaBot. The backend auto-refreshes them **on startup when stale** and on demand via `POST /api/meta/refresh` (also exposed as the refresh button on the Meta page). A refresh also regenerates `data/presets.json`.
- **`data/team_comps.json` is hand-curated** — best win-rate comps per map from VCT Masters London 2026 (patch 12.10), VOD links validated. Update it manually after major events; generators never write to it.
- **`data/agents.json`** is the curated scoring overlay (synergy tags, map affinity, utility). New agents are judged primarily by pick/win rate from the meta data, not curation.
- **`data/cache/`** holds the 24 h valorant-api.com disk cache; safe to delete (re-fetched on demand, offline fallback included).
- **`data/db.json`** stores users and saved comps; it is **gitignored** because it contains user emails.

---

## Authentication & security model

- **NextAuth v5** with the Google provider and **JWT sessions** (no database adapter). The user's **email is the identity key**.
- The trust boundary is the **`X-User-Email` header**: only the Next.js server sets it, after reading the session ([frontend/src/lib/backend.ts](frontend/src/lib/backend.ts)). The `/api/saved*` paths are excluded from the proxy rewrite, so browsers can never hit FastAPI's saved-comps endpoints through the app.
- **Local dev:** anything that can reach port 8000 directly can forge the header — acceptable on localhost.
- **Production:** set `BACKEND_SHARED_SECRET` on both the frontend and backend; FastAPI then additionally requires the matching `X-Backend-Secret` header. Keep the backend off the public internet where possible.

---

## Comp code format

```
VAL-2-<MAP>-<A1>-<A2>-<A3>-<A4>-<A5>
e.g. VAL-2-AC-JT-OM-SV-KJ-KO   (Ascent: Jett, Omen, Sova, Killjoy, KAY/O)
```

Implemented client-side in [frontend/src/lib/comp-code.ts](frontend/src/lib/comp-code.ts) (`encodeComp` / `decodeComp`) — fully offline, no server round-trip. Backward compatible with codes from the legacy Streamlit app; the roster table includes the 2026 agents (Miks `MK`, Veto `VT`, …). Codes load via the Share panel or `/builder?code=…` links.

---

## Deployment

**Live:** [vlrcompbuilder.vercel.app](https://vlrcompbuilder.vercel.app) (Vercel frontend) → [valorantcompbuilder-production.up.railway.app](https://valorantcompbuilder-production.up.railway.app) (Railway backend). Both auto-deploy on push to `main`.

Deploy config lives in the repo:

- `railway.json` — start command (`uvicorn backend.main:app --host 0.0.0.0 --port $PORT`), `/api/health` healthcheck, restart policy
- `.python-version` — pins Python 3.13 for the Railway build
- root `requirements.txt` — combined manifest installed by Railway (FastAPI set) and the legacy Streamlit app

### Backend → Railway

1. New project → deploy from the GitHub repo (repo root, no subdirectory).
2. Mount a **volume** at `/data` (saved comps must survive redeploys — the container filesystem is ephemeral).
3. Env vars: `DB_PATH=/data/db.json`, `BACKEND_SHARED_SECRET=<random secret>`.
4. Verify `https://<railway-url>/api/health` → `{"status":"ok"}`. The first boot auto-refreshes meta stats in a background thread, so the healthcheck passes immediately.

### Frontend → Vercel

1. New project from the repo with **Root Directory = `frontend/`**.
2. Env vars: `API_URL` (the Railway URL, no trailing slash), `AUTH_SECRET` (fresh: `npx auth secret`), `AUTH_GOOGLE_ID`, `AUTH_GOOGLE_SECRET`, `BACKEND_SHARED_SECRET` (same value as Railway).
3. Add `https://<vercel-domain>/api/auth/callback/google` to the Google OAuth client's authorized redirect URIs.

### Post-deploy smoke test

Sign in → build a comp → save → check `/saved` → load in builder → delete; confirm signed-out requests to `/api/saved` return 401; redeploy the backend and confirm saved comps survive (volume works).

> Older docs in the repo root (`DEPLOYMENT.md`, `GOOGLE_OAUTH_SETUP.md`, `README_PRODUCTION.md`, `COMPLETE_OVERHAUL.md`, `UPDATE_GUIDE_V3.md`) describe the **legacy Streamlit deployment** and are superseded by this document.

---

## Legacy Streamlit app

The original Streamlit implementation remains runnable during the transition:

```powershell
pip install -r requirements.txt   # streamlit, requests, bs4, google-auth
streamlit run app.py              # http://localhost:8501
```

It shares `app/services/` and `data/` with the new stack but receives no new features.

---

*Game data courtesy of [valorant-api.com](https://valorant-api.com). Meta statistics from VCT via MetaBot. Community project — not affiliated with Riot Games.*
