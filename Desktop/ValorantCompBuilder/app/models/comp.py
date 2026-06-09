"""Comp model"""
class Comp:
    def __init__(self, agents=None, map_name="", score=0, warnings=None, strengths=None, weaknesses=None, notes="", name=""):
        self.agents = agents or []
        self.map_name = map_name
        self.score = score
        self.warnings = warnings or []
        self.strengths = strengths or []
        self.weaknesses = weaknesses or []
        self.notes = notes
        self.name = name
    def to_dict(self):
        return {"agents": [a.name if hasattr(a, 'name') else a for a in self.agents], "map_name": self.map_name, "score": self.score, "warnings": self.warnings, "strengths": self.strengths, "weaknesses": self.weaknesses, "notes": self.notes, "name": self.name}
