from dataclasses import dataclass
from typing import List

@dataclass
class ImageBackground:
    """
    Element types:

    ~~~~~~~~~~
    0: None
    1: Image Upload
    2: Image URL
    3: Server Icon
    4: Profile Picture
    5: Color
    ~~~~~~~~~~
    """
    type: int

    color: str
    upload: str
    url: str
    opacity: str
    blur: str
    cover: bool
    width: str
    height: str

@dataclass
class ImageElement:
    """
    Element types:

    ~~~~~~~~~~
    1: Rectangle
    2: Text
    3: Image Upload
    4: Image URL
    5: Server Icon
    6: Profile Picture
    ~~~~~~~~~~
    """
    type: int
    
    """
    The url must be from cdn.matebot.xyz or cdn.discordapp.com
    """
    url: str
    
    upload: str
    positionx: str
    positiony: str
    alignx: float
    font: int
    fontsize: str
    fontweight: int
    content: str
    width: str
    height: str
    cover: bool
    radius: str
    opacity: float
    color: str
    blur: str
    progress: bool
    verticalprogress: bool

@dataclass
class Image:
    background: ImageBackground
    elements: List[ImageElement]

    def set_background(self, background: ImageBackground) -> None:
        self.background = background
    
    def add_element(self, element: ImageElement) -> None:
        self.elements.append(element)
    
    def set_elements(self, elements: List[ImageElement]) -> None:
        self.elements = elements
    
    def set_element(self, index: int, element: ImageElement) -> None:
        self.elements[index] = element
    
    def remove_element(self, index: int) -> None:
        del self.elements[index]
    
    def __post_init__(self):
        if isinstance(self.background, dict):
            self.background = ImageBackground(**self.background)
        self.elements = [ImageElement(**element) if isinstance(element, dict) else element for element in self.elements]