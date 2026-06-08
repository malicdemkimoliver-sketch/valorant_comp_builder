"""
Agent model — represents a Valorant agent with all their attributes.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class Agent:
    name: str
    role: str
    icon: str = ""
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    good_maps: List[str] = field(default_factory=list)
    synergy_tags: List[str] = field(default_factory=list)
    utility: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "Agent":
        return cls(
            name=data.get("name", ""),
            role=data.get("role", ""),
            icon=data.get("icon", ""),
            strengths=data.get("strengths", []),
            weaknesses=data.get("weaknesses", []),
            good_maps=data.get("good_maps", []),
            synergy_tags=data.get("synergy_tags", []),
            utility=data.get("utility", []),
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "role": self.role,
            "icon": self.icon,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "good_maps": self.good_maps,
            "synergy_tags": self.synergy_tags,
            "utility": self.utility,
        }

    def fits_map(self, map_name: str) -> bool:
        return map_name in self.good_maps

    def has_tag(self, tag: str) -> bool:
        return tag in self.synergy_tags

    def has_utility(self, util: str) -> bool:
        return util in self.utility
