from dataclasses import dataclass
from typing import List, Dict, Optional
from matebot.fortnite.items import CosmeticIcon

@dataclass
class QuestsBundleItem:
    id: str
    name: str
    description: str
    shortDescription: str
    completion: str
    rewards: List[str]
    sortPriority: int
    rarity: str
    category: str
    tags: List[str]
    count: int

@dataclass
class QuestsBundle:
    id: str
    name: str
    description: str
    shortDescription: str
    goal: str
    tags: List[str]
    icon: CosmeticIcon
    items: List[QuestsBundleItem]

    def __post_init__(self):
        self.items = [QuestsBundleItem(**item) if isinstance(item, dict) else item for item in self.items]
        if isinstance(self.icon, dict):
            self.icon = CosmeticIcon(**self.icon)

@dataclass
class QuestsReward:
    reward: str
    quantity: int
    visible: bool

@dataclass
class QuestsDef:
    name: str
    description: str
    shortDescription: str
    searchTags: str
    tags: List[str]
    icon: CosmeticIcon

    def __post_init__(self):
        if isinstance(self.icon, dict):
            self.icon = CosmeticIcon(**self.icon)

@dataclass
class Quests:
    athenaSeasonalXP: Optional[QuestsDef]
    athenaLevelUp: Optional[QuestsDef]
    rewards: Dict[str, QuestsReward]
    folders: Dict[str, List[QuestsBundle]]

    def __post_init__(self):
        if isinstance(self.athenaSeasonalXP, dict):
            self.athenaSeasonalXP = QuestsDef(**self.athenaSeasonalXP)
        if isinstance(self.athenaLevelUp, dict):
            self.athenaLevelUp = QuestsDef(**self.athenaLevelUp)
        
        self.rewards = {key: QuestsReward(**reward) for key, reward in self.rewards.items()}
        
        self.folders = {
            key: [QuestsBundle(**bundle) for bundle in bundles] if isinstance(bundles, list) else bundles
            for key, bundles in self.folders.items()
        }