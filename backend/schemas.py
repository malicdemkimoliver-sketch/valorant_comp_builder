"""Request models for the comp endpoints."""
from pydantic import BaseModel, Field


class ScoreRequest(BaseModel):
    agents: list[str] = Field(..., min_length=1, max_length=5)
    map: str


class SuggestRequest(BaseModel):
    agents: list[str] = Field(..., min_length=1, max_length=4)
    map: str
    top_n: int = Field(default=3, ge=1, le=10)
