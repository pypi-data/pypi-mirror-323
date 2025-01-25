from dataclasses import dataclass
from typing import Any, List, Optional, Union
from matebot.fortnite.base import Definition
from matebot.fortnite.newdisplayassets import NewDisplayAsset

@dataclass
class ItemShopEntryBundleItemInfo:
    templateId: str
    quantity: float

@dataclass
class ItemShopEntryBundleItem:
    bCanOwnMultiple: bool
    regularPrice: float
    discountedPrice: float
    alreadyOwnedPriceReduction: float
    item: Optional[ItemShopEntryBundleItemInfo]

@dataclass
class ItemShopEntryBundle:
    name: str
    discountedBasePrice: float
    regularBasePrice: float
    floorPrice: float
    currencyType: str
    currencySubType: str
    displayType: str
    bundleItems: List[ItemShopEntryBundleItem]

@dataclass
class ItemShopEntryColors:
    color1: str
    color2: str
    color3: str
    textBackground: str

@dataclass
class ItemShopEntryItem:
    templateId: str
    quantity: str
    definition: Optional[Definition]

    def __post_init__(self):
        if self.definition:
            self.definition = Definition(**self.definition)

@dataclass
class ItemShopEntryPrice:
    basePrice: float
    currencySubType: float
    currencyType: str
    dynamicRegularPrice: float
    finalPrice: float
    regularPrice: float
    saleExpiration: str

@dataclass
class ItemShopEntryGrant:
    templateId: str
    quantity: float

@dataclass
class ItemShopEntry:
    size: str
    sortPriority: float
    catalogGroupPriority: float
    devName: str
    offerId: str
    offerTag: str
    baseItem: Optional[Definition]
    images: List[NewDisplayAsset]
    prices: List[ItemShopEntryPrice]
    bundleInfo: Optional[ItemShopEntryBundleItemInfo]
    newDisplayAssetPath: str
    displayAssetPath: str
    templateId: str
    giftable: bool
    colors: ItemShopEntryColors
    refundable: bool
    inDate: str
    outDate: str
    requirements: List[ItemShopEntryGrant]
    items: List[ItemShopEntryItem]
    additionalGrants: List[Any]

    def __post_init__(self):
        if isinstance(self.bundleInfo, dict):
            self.bundleInfo = ItemShopEntryBundleItemInfo(**self.bundleInfo)

        self.prices = [ItemShopEntryPrice(**price) for price in self.prices]
        self.items = [ItemShopEntryItem(**item) for item in self.items]
        self.requirements = [ItemShopEntryGrant(**grant) for grant in self.requirements]

        if self.baseItem:
            self.baseItem = Definition(**self.baseItem)

@dataclass
class ItemShopRow:
    layoutId: str
    entries: List[ItemShopEntry]

    def __post_init__(self):
        self.entries = [ItemShopEntry(**entry) for entry in self.entries]

@dataclass
class ItemShopSection:
    metadata: Any
    displayName: str
    sectionId: str
    rows: List[ItemShopRow]

    def __post_init__(self):
        self.rows = [ItemShopRow(**row) for row in self.rows]

@dataclass
class ItemShopCategory:
    name: str
    sections: List[ItemShopSection]

    def __post_init__(self):
        self.sections = [ItemShopSection(**section) for section in self.sections]

@dataclass
class ItemShop:
    refreshIntervalHours: float
    dailyPurchaseHours: float
    expiration: str
    categories: List[ItemShopCategory]
    
    def __post_init__(self):
        self.categories = [ItemShopCategory(**category) for category in self.categories]