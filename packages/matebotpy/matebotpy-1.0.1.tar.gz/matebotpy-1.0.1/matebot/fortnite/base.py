from dataclasses import dataclass
from typing import List, Optional, Any, Dict, Union
from matebot.fortnite.items import Character, Cosmetic, CarCosmetic, Instrument, CosmeticVariantToken, CosmeticVehicleVariant, Juno

@dataclass
class PrimarySecondaryColor:
    primary: str
    secondary: str

@dataclass
class WebsocketEventData:
    languages: List[str]
    build: str
    hash: str
    platform: str

@dataclass
class WebsocketEvent:
    type: str
    data: WebsocketEventData
    timestamp: int

    def __post_init__(self):
        if isinstance(self.data, dict):
            self.data = WebsocketEventData(**self.data)

@dataclass
class StatsTrack:
    gameId: str
    trackguid: str
    accountId: str
    rankingType: str
    lastUpdated: str
    currentDivision: float
    highestDivision: float
    promotionProgress: float
    currentPlayerRanking: Optional[float]

@dataclass
class Stats:
    accountId: str
    stats: Dict[str, Any]
    ranks: List[StatsTrack]

    def __post_init__(self):
        self.ranks = [StatsTrack(**track) if isinstance(track, dict) else track for track in self.ranks]

Definition = Union[Character, Cosmetic, CarCosmetic, Instrument, CosmeticVariantToken, CosmeticVehicleVariant, Juno]