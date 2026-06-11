"""
FastAPI backend — HTTP layer over the existing comp builder services.
Run from the repo root so the `app` package is importable:
    python -m uvicorn backend.main:app --reload --port 8000
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend import meta_refresh
from backend.routers import agents, comp, maps, meta, presets, team_comps


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Auto-refresh the meta stats in the background when they're outdated
    meta_refresh.refresh_if_stale()
    yield


app = FastAPI(title="Gyd's VLR Comp Builder API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents.router)
app.include_router(maps.router)
app.include_router(meta.router)
app.include_router(comp.router)
app.include_router(presets.router)
app.include_router(team_comps.router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}
