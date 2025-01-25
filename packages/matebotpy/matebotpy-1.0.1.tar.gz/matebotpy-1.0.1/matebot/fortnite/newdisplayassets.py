from dataclasses import dataclass
from typing import Dict, List

@dataclass
class MaterialParameter:
    name: str
    index: int
    value: float

@dataclass
class Material: 
    colors: Dict[str, str]
    parameters: List[MaterialParameter]
    image: str

    def __post_init__(self):
        self.parameters = [MaterialParameter(**param) if isinstance(param, dict) else param for param in self.parameters]

@dataclass
class NewDisplayAsset:
    tag: str
    material: Material
    render: str

    def __post_init__(self):
        if isinstance(self.material, dict):
            self.material = Material(**self.material)