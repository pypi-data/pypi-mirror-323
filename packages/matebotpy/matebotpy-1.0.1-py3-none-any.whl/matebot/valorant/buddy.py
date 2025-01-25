from dataclasses import dataclass
from typing import List

@dataclass
class BuddyLevel:
    uuid: str
    name: str
    icon: str

@dataclass
class Buddy:
    uuid: str
    name: str
    icon: str
    levels: List[BuddyLevel]