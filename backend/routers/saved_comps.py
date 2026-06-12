"""
Saved comps — wraps app/services/database.py (data/db.json).

Trusts X-User-Email, which is set ONLY by the Next.js server after reading
the NextAuth session; the frontend proxy never forwards /api/saved* here.
Local-dev note: anyone who can reach port 8000 directly can forge the
header — acceptable on localhost. For deployment, set BACKEND_SHARED_SECRET
on both sides to additionally require X-Backend-Secret.
"""
import os
from typing import Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from app.services import database

router = APIRouter(prefix="/api/saved-comps", tags=["saved-comps"])

SHARED_SECRET = os.environ.get("BACKEND_SHARED_SECRET", "")


def _require_user(email: Optional[str], secret: Optional[str]) -> str:
    if SHARED_SECRET and secret != SHARED_SECRET:
        raise HTTPException(status_code=403, detail="Invalid backend secret")
    if not email:
        raise HTTPException(status_code=401, detail="Missing X-User-Email")
    return email


class SaveCompRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    map: str
    agents: list[str] = Field(..., min_length=5, max_length=5)
    code: Optional[str] = None
    score: Optional[float] = None
    grade: Optional[str] = None
    notes: str = ""
    user_name: str = ""  # session display name, kept in db.json users


@router.get("")
def list_comps(
    x_user_email: Optional[str] = Header(None),
    x_backend_secret: Optional[str] = Header(None),
) -> list:
    return database.get_user_comps(_require_user(x_user_email, x_backend_secret))


@router.post("")
def save_comp(
    req: SaveCompRequest,
    x_user_email: Optional[str] = Header(None),
    x_backend_secret: Optional[str] = Header(None),
) -> dict:
    email = _require_user(x_user_email, x_backend_secret)
    database.add_or_update_user(email, req.user_name)
    comp_id = database.save_comp(email, req.model_dump(exclude={"user_name"}))
    return {"id": comp_id}


@router.delete("/{comp_id}")
def delete_comp(
    comp_id: str,
    x_user_email: Optional[str] = Header(None),
    x_backend_secret: Optional[str] = Header(None),
) -> dict:
    database.delete_comp(_require_user(x_user_email, x_backend_secret), comp_id)
    return {"ok": True}
