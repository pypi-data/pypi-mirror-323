from dataclasses import dataclass

@dataclass
class XYValue:
    x: float
    y: float

@dataclass
class Position:
    x: float
    y: float
    z: float

@dataclass
class Theme:
    name: str
    icon: str

@dataclass
class ContentTier:
    rank: int
    juiceValue: int
    juiceCost: int
    color: str
    name: str
    nameAbbreviated: str
    icon: str

@dataclass
class LevelBorder:
    uuid: str
    name: str
    start: int
    numberAppearance: str
    playerCardAppearance: str