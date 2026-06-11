"""
FastAPI backend — HTTP layer over the existing comp builder services.
Run from the repo root so the `app` package is importable:
    python -m uvicorn backend.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import agents, comp, maps, meta

app = FastAPI(title="Valorant Comp Builder API")

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


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}
