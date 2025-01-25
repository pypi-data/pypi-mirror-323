from dataclasses import dataclass

@dataclass
class Bundle:
    uuid: str
    name: str
    customNameSubtext: str
    description: str
    promoDescription: str
    bundleDescription: str
    icon: str
    icon2: str
    verticalImage: str
    logo: str
    useAdditionalContext: bool