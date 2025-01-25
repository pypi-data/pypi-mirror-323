from dataclasses import dataclass
from typing import Optional, List
from matebot.valorant.base import XYValue

@dataclass
class CharacterRole:
    uuid: str
    name: str
    description: str
    icon: str

@dataclass
class CharacterPortraitRenderTransformation:
    translation: XYValue
    scale: XYValue

@dataclass
class CharacterAbility:
    id: str
    name: str
    description: str
    icon: str

@dataclass
class Character:
    uuid: str
    id: str
    developerName: str
    shippingName: str
    name: str
    description: str
    icon: str
    portrait: str
    background: str
    killFeedIcon: str
    isPlayableCharacter: str
    role: Optional[CharacterRole]
    portraitRenderTransform: CharacterPortraitRenderTransformation
    abilities: List[CharacterAbility]

    def __post_init__(self):
        self.levels = [CharacterAbility(**ability) if isinstance(ability, dict) else ability for ability in self.abilities]
        self.role = CharacterRole(**self.role) if isinstance(self.role, dict) else self.role
        self.portraitRenderTransform = CharacterPortraitRenderTransformation(**self.portraitRenderTransform) if isinstance(self.portraitRenderTransform, dict) else self.portraitRenderTransform