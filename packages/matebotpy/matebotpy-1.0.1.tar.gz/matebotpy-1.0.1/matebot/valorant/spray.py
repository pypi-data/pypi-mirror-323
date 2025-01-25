from dataclasses import dataclass
from typing import List

@dataclass
class SprayLevel:
    uuid: str
    level: int
    name: str

@dataclass
class Spray:
    uuid: str
    category: str
    theme: str
    name: str
    icon: str
    levels: List[SprayLevel]

    def __post_init__(self):
        self.levels = [SprayLevel(**level) if isinstance(level, dict) else level for level in self.levels]