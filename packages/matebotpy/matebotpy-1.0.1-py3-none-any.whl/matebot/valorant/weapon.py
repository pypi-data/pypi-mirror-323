from dataclasses import dataclass
from typing import Optional, List, Dict
from matebot.valorant.base import Position

@dataclass
class DamageRange:
    rangeStartMeters: float
    rangeEndMeters: float
    head: float
    body: float
    leg: float

@dataclass
class WeaponsStatsAltShotgunStats:
    shotgunPelletCount: int
    burstRate: float

@dataclass
class WeaponStatsAirBurst:
    burstDistance: float
    shotgunPelletCount: int

@dataclass
class WeaponStatsADSStats:
    zoomMultiplier: float
    fireRate: float
    runSpeedMultiplier: float
    burstCount: int
    firstBulletAccuracy: float

@dataclass
class WeaponStats:
    fireMode: str
    fireRate: float
    magazineSize: int
    runSpeedMultiplier: float
    equipTimeSeconds: float
    reloadTimeSeconds: float
    firstBulletAccuracy: float
    shotgunPelletCount: int
    wallPenetration: str
    damageRanges: List[DamageRange]
    altFireType: str
    ads: Optional[WeaponStatsADSStats]
    airBurst: Optional[WeaponStatsAirBurst]
    altShotgunStats: Optional[WeaponsStatsAltShotgunStats]
    feature: str

@dataclass
class WeaponLevel:
    uuid: str
    name: str
    icon: str

@dataclass
class WeaponChroma:
    uuid: str
    name: str
    render: str
    swatch: str
    icon: str

@dataclass
class WeaponSkin:
    name: str
    icon: str
    wallpaper: str
    defaultChroma: str
    theme: str
    contentTier: str
    levels: List[WeaponLevel]
    chromas: List[WeaponChroma]

    def __post_init__(self):
        self.levels = [WeaponLevel(**level) if isinstance(level, dict) else level for level in self.levels]
        self.chromas = [WeaponChroma(**chroma) if isinstance(chroma, dict) else chroma for chroma in self.chromas]

@dataclass
class WeaponShopDataGrid:
    column: int
    row: int

@dataclass
class WeaponShopData:
    price: int
    category: str
    categoryText: str
    image: str
    grid: WeaponShopDataGrid

    def __post_init__(self):
        if isinstance(self.grid, dict):
            self.grid = WeaponShopDataGrid(**self.grid)

@dataclass
class Weapon:
    uuid: str
    defaultSkin: str
    name: str
    category: str
    icon: str
    killIcon: str
    cameraPosition: Optional[Position]
    pivotPoint: Optional[Position]
    minFov: float
    maxFov: float
    defaultFov: float
    buddyCameraPosition: Optional[Position]
    buddyDefaultFov: float
    buddyMaxFov: float
    buddyMinFov: float
    stats: Optional[WeaponStats]
    shopData: Optional[WeaponShopData]
    skins: Dict[str, WeaponSkin]

    def __post_init__(self):
        self.cameraPosition = self._parse_position(self.cameraPosition)
        self.pivotPoint = self._parse_position(self.pivotPoint)
        self.buddyCameraPosition = self._parse_position(self.buddyCameraPosition)
        
        if self.stats:
            self.stats = self._parse_weapon_stats(self.stats)

        if isinstance(self.skins, dict):
            self.skins = {
                skin_name: WeaponSkin(**skin_data) for skin_name, skin_data in self.skins.items()
            }

        if isinstance(self.shopData, dict):
            self.shopData = WeaponShopData(**self.shopData)

    def _parse_position(self, position_data: Optional[Dict[str, float]]) -> Optional[Position]:
        if position_data:
            return Position(**position_data)
        return None

    def _parse_weapon_stats(self, stats_data: Dict) -> WeaponStats:
        ads = WeaponStatsADSStats(**stats_data['ads']) if stats_data.get('ads') else None
        airBurst = WeaponStatsAirBurst(**stats_data['airBurst']) if stats_data.get('airBurst') else None
        altShotgunStats = WeaponsStatsAltShotgunStats(**stats_data['altShotgunStats']) if stats_data.get('altShotgunStats') else None
        
        return WeaponStats(
            fireMode=stats_data['fireMode'],
            fireRate=stats_data['fireRate'],
            magazineSize=stats_data['magazineSize'],
            runSpeedMultiplier=stats_data['runSpeedMultiplier'],
            equipTimeSeconds=stats_data['equipTimeSeconds'],
            reloadTimeSeconds=stats_data['reloadTimeSeconds'],
            firstBulletAccuracy=stats_data['firstBulletAccuracy'],
            shotgunPelletCount=stats_data['shotgunPelletCount'],
            wallPenetration=stats_data['wallPenetration'],
            damageRanges=[DamageRange(**range_data) for range_data in stats_data['damageRanges']],
            altFireType=stats_data['altFireType'],
            ads=ads,
            airBurst=airBurst,
            altShotgunStats=altShotgunStats,
            feature=stats_data['feature']
        )

    def _parse_weapon_shop_grid(self, grid_data: Optional[Dict]) -> Optional[WeaponShopDataGrid]:
        if grid_data:
            return WeaponShopDataGrid(**grid_data)
        return None