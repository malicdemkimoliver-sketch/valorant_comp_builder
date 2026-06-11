from fastapi import APIRouter, HTTPException

from backend import catalog

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("")
def list_agents() -> list[dict]:
    return catalog.get_agents()


@router.get("/{name}")
def get_agent(name: str) -> dict:
    agent = catalog.get_agent(name)
    if agent is None:
        raise HTTPException(status_code=404, detail=f"Unknown agent '{name}'")
    return agent
