from dataclasses import dataclass

@dataclass
class Map:
    uuid: str
    id: str
    url: str
    splashScreen: str
    name: str
    icon: str
    listViewIcon: str
    listViewIconTall: str
    stylizedBackgroundImage: str
    premierBackgroundImage: str
    tacticalDescription: str
    coordinates: str
    xScalarToAdd: float
    yScalarToAdd: float
    xMultiplier: float
    yMultiplier: float