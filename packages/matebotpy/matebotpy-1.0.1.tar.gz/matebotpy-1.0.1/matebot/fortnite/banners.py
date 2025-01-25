from dataclasses import dataclass
from matebot.fortnite.items import CosmeticIcon
from matebot.fortnite.base import PrimarySecondaryColor
from typing import List, Dict

@dataclass
class Banner:
    name: str
    description: str
    shortDescription: str
    rarity: str
    tags: List[str]
    icon: CosmeticIcon

    def __post_init__(self):
        if isinstance(self.icon, dict):
            self.icon = CosmeticIcon(**self.icon)

@dataclass
class BannerCategory:
    name: str
    sortPriority: int
    banners: Dict[str, Banner]

    def __post_init__(self):
        self.banners = {banner_name: Banner(**banner_data) for banner_name, banner_data in self.banners.items()}

@dataclass
class Banners:
    colors: Dict[str, PrimarySecondaryColor]
    categories: List[BannerCategory]

    def __post_init__(self):
        self.categories = [BannerCategory(**category_data) if isinstance(category_data, dict) else category_data for category_data in self.categories]
        self.colors = {color_name: PrimarySecondaryColor(**color_data) if isinstance(color_data, dict) else color_data for color_name, color_data in self.colors.items()}