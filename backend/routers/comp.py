from fastapi import APIRouter, HTTPException

from app.services import meta_service
from app.services.scoring import get_score_grade, get_score_label, score_comp
from app.services.suggestion_service import suggest_agents
from backend import catalog
from backend.schemas import ScoreRequest, SuggestRequest

router = APIRouter(prefix="/api", tags=["comp"])


def _resolve_agents(names: list[str]) -> list[dict]:
    by_name = {a["name"].lower(): a for a in catalog.get_agents()}
    resolved = []
    for name in names:
        agent = by_name.get(name.strip().lower())
        if agent is None:
            raise HTTPException(status_code=404, detail=f"Unknown agent '{name}'")
        resolved.append(agent)
    if len({a["name"] for a in resolved}) != len(resolved):
        raise HTTPException(status_code=400, detail="Duplicate agents in comp")
    return resolved


def _resolve_map(name: str) -> str:
    map_data = catalog.get_map(name)
    if map_data is None:
        raise HTTPException(status_code=404, detail=f"Unknown map '{name}'")
    return map_data["name"]


@router.post("/score")
def score(req: ScoreRequest) -> dict:
    agents = _resolve_agents(req.agents)
    map_name = _resolve_map(req.map)

    total, breakdown = score_comp(agents, map_name, {})
    grade, grade_color = get_score_grade(total)

    return {
        "map": map_name,
        "score": total,
        "grade": grade,
        "grade_color": grade_color,
        "label": get_score_label(total),
        "breakdown": breakdown,
        "agents": [
            {
                "name": a["name"],
                "role": a["role"],
                "on_meta": meta_service.is_meta_pick(a["name"], map_name),
                "tier": meta_service.get_agent_tier(a["name"], map_name),
            }
            for a in agents
        ],
    }


@router.post("/suggest")
def suggest(req: SuggestRequest) -> dict:
    agents = _resolve_agents(req.agents)
    map_name = _resolve_map(req.map)
    suggestions = suggest_agents([a["name"] for a in agents], map_name, req.top_n)
    return {"map": map_name, "suggestions": suggestions}
