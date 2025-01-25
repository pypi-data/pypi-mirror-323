from dataclasses import dataclass
from typing import Dict, List
from matebot.fortnite.items import Cosmetic, CarCosmetic, CosmeticVehicleVariant, Character, CosmeticVariantToken, Instrument, Juno

@dataclass
class Help:
    display: str
    help: str

@dataclass
class CosmeticsBattleRoyale:
    characters: Dict[str, Character]
    backpacks: Dict[str, Cosmetic]
    gliders: Dict[str, Cosmetic]
    petcarriers: Dict[str, Cosmetic]
    contrails: Dict[str, Cosmetic]
    pickaxes: Dict[str, Cosmetic]
    dances: Dict[str, Cosmetic]
    emojis: Dict[str, Cosmetic]
    toys: Dict[str, Cosmetic]
    sprays: Dict[str, Cosmetic]
    wraps: Dict[str, Cosmetic]
    loadingScreens: Dict[str, Cosmetic]
    musicPacks: Dict[str, Cosmetic]
    variants: Dict[str, CosmeticVariantToken]

    def __post_init__(self):
        self.characters = {key: Character(**value) for key, value in self.characters.items()}
        self.backpacks = {key: Cosmetic(**value) for key, value in self.backpacks.items()}
        self.gliders = {key: Cosmetic(**value) for key, value in self.gliders.items()}
        self.petcarriers = {key: Cosmetic(**value) for key, value in self.petcarriers.items()}
        self.contrails = {key: Cosmetic(**value) for key, value in self.contrails.items()}
        self.pickaxes = {key: Cosmetic(**value) for key, value in self.pickaxes.items()}
        self.dances = {key: Cosmetic(**value) for key, value in self.dances.items()}
        self.emojis = {key: Cosmetic(**value) for key, value in self.emojis.items()}
        self.toys = {key: Cosmetic(**value) for key, value in self.toys.items()}
        self.sprays = {key: Cosmetic(**value) for key, value in self.sprays.items()}
        self.wraps = {key: Cosmetic(**value) for key, value in self.wraps.items()}
        self.loadingScreens = {key: Cosmetic(**value) for key, value in self.loadingScreens.items()}
        self.musicPacks = {key: Cosmetic(**value) for key, value in self.musicPacks.items()}
        self.variants = {key: CosmeticVariantToken(**value) for key, value in self.variants.items()}

@dataclass
class CosmeticsCars:
    bodies: Dict[str, CarCosmetic]
    wheels: Dict[str, CarCosmetic]
    boosters: Dict[str, CarCosmetic]
    driftTrails: Dict[str, CarCosmetic]
    skins: Dict[str, CarCosmetic]
    variants: Dict[str, CosmeticVehicleVariant]

    def __post_init__(self):
        self.bodies = {key: CarCosmetic(**value) for key, value in self.bodies.items()}
        self.wheels = {key: CarCosmetic(**value) for key, value in self.wheels.items()}
        self.boosters = {key: CarCosmetic(**value) for key, value in self.boosters.items()}
        self.driftTrails = {key: CarCosmetic(**value) for key, value in self.driftTrails.items()}
        self.skins = {key: CarCosmetic(**value) for key, value in self.skins.items()}
        self.variants = {key: CosmeticVehicleVariant(**value) for key, value in self.variants.items()}

@dataclass
class CosmeticsInstrument:
    aura: Dict[str, Instrument]
    bass: Dict[str, Instrument]
    drum: Dict[str, Instrument]
    guitar: Dict[str, Instrument]
    keytar: Dict[str, Instrument]
    mic: Dict[str, Instrument]
    variants: Dict[str, CosmeticVariantToken]

    def __post_init__(self):
        self.aura = {key: Instrument(**value) for key, value in self.aura.items()}
        self.bass = {key: Instrument(**value) for key, value in self.bass.items()}
        self.drum = {key: Instrument(**value) for key, value in self.drum.items()}
        self.guitar = {key: Instrument(**value) for key, value in self.guitar.items()}
        self.keytar = {key: Instrument(**value) for key, value in self.keytar.items()}
        self.mic = {key: Instrument(**value) for key, value in self.mic.items()}
        self.variants = {key: CosmeticVariantToken(**value) for key, value in self.variants.items()}

@dataclass
class CosmeticsLego:
    buildingSets: Dict[str, Juno]
    buildingProps: Dict[str, Juno]
    
    def __post_init__(self):
        self.buildingSets = {key: Juno(**value) for key, value in self.buildingSets.items()}
        self.buildingProps = {key: Juno(**value) for key, value in self.buildingProps.items()}

@dataclass
class Cosmetics:
    sets: Dict[str, str]
    filters: Dict[str, List[str]]
    texts: Dict[str, Help]
    br: CosmeticsBattleRoyale
    cars: CosmeticsCars
    instruments: CosmeticsInstrument
    legos: CosmeticsLego

    def __post_init__(self):
        self.texts = {key: Help(**value) for key, value in self.texts.items()}
        self.br = CosmeticsBattleRoyale(**self.br)
        self.cars = CosmeticsCars(**self.cars)
        self.instruments = CosmeticsInstrument(**self.instruments)
        self.legos = CosmeticsLego(**self.legos)