"""
Comp model — represents a 5-agent team composition.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from app.models.agent import Agent


@dataclass
class Comp:
    agents: List[Agent] = field(default_factory=list)
    map_name: str = ""
    score: int = 0
    warnings: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    notes: str = ""
    name: str = ""

    def is_complete(self) -> bool:
        return len(self.agents) == 5

    def role_counts(self) -> dict:
        counts = {"Duelist": 0, "Controller": 0, "Initiator": 0, "Sentinel": 0}
        for agent in self.agents:
            if agent.role in counts:
                counts[agent.role] += 1
        return counts

    def agent_names(self) -> List[str]:
        return [a.name for a in self.agents]

    def all_synergy_tags(self) -> List[str]:
        tags = []
        for agent in self.agents:
            tags.extend(agent.synergy_tags)
        return tags

    def all_utility(self) -> List[str]:
        util = []
        for agent in self.agents:
            util.extend(agent.utility)
        return util

    def has_role(self, role: str) -> bool:
        return any(a.role == role for a in self.agents)

    def get_agents_by_role(self, role: str) -> List[Agent]:
        return [a for a in self.agents if a.role == role]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "map_name": self.map_name,
            "agents": [a.to_dict() for a in self.agents],
            "score": self.score,
            "warnings": self.warnings,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Comp":
        agents = [Agent.from_dict(a) for a in data.get("agents", [])]
        return cls(
            agents=agents,
            map_name=data.get("map_name", ""),
            score=data.get("score", 0),
            warnings=data.get("warnings", []),
            strengths=data.get("strengths", []),
            weaknesses=data.get("weaknesses", []),
            notes=data.get("notes", ""),
            name=data.get("name", ""),
        )
