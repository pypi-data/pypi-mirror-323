from dataclasses import dataclass

@dataclass
class PlayerCard:
    uuid: str
    name: str
    small: str
    large: str
    wide: str