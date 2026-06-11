from fastapi import APIRouter, HTTPException

from backend import catalog

router = APIRouter(prefix="/api/maps", tags=["maps"])


@router.get("")
def list_maps() -> list[dict]:
    return catalog.get_maps()


@router.get("/{name}")
def get_map(name: str) -> dict:
    map_data = catalog.get_map(name)
    if map_data is None:
        raise HTTPException(status_code=404, detail=f"Unknown map '{name}'")
    return map_data
