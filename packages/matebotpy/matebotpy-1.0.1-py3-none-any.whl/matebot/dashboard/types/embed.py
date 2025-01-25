from dataclasses import dataclass
from typing import List

@dataclass
class EmbedImage:
    """
    Image types:

    ~~~~~~~~~~
    1: Upload or None
    2: URL
    3: Guild Icon
    4: Profile Picture
    ~~~~~~~~~~
    """
    type: int

    url: str
    upload: str

@dataclass
class EmbedAuthor:
    name: str
    url: str
    icon: EmbedImage

    def set_icon(self, icon: EmbedImage) -> None:
        self.icon = icon

    def __post_init__(self):
        if isinstance(self.icon, dict):
            self.icon = EmbedImage(**self.icon)

@dataclass
class EmbedFooter:
    text: str
    icon: EmbedImage

    def set_icon(self, icon: EmbedImage) -> None:
        self.icon = icon

    def __post_init__(self):
        if isinstance(self.icon, dict):
            self.icon = EmbedImage(**self.icon)

@dataclass
class EmbedField:
    name: str
    value: str
    inline: bool

@dataclass
class Embed:
    title: str
    description: str
    url: str
    color: str
    timestamp: bool
    footer: EmbedFooter
    author: EmbedAuthor
    image: EmbedImage
    thumbnail: EmbedImage
    fields: List[EmbedField]

    def add_field(self, key: str, value: str, *, inline: bool=False) -> None:
        self.fields.append(EmbedField(key, value, inline))

    def set_fields(self, fields: List[EmbedField]) -> None:
        self.fields = fields
    
    def set_field(self, index: int, field: EmbedField) -> None:
        self.fields[index] = field
    
    def remove_field(self, index: int) -> None:
        del self.fields[index]
    
    def __post_init__(self):
        if isinstance(self.footer, dict):
            self.footer = EmbedFooter(**self.footer)
        if isinstance(self.author, dict):
            self.author = EmbedAuthor(**self.author)
        if isinstance(self.image, dict):
            self.image = EmbedImage(**self.image)
        if isinstance(self.thumbnail, dict):
            self.thumbnail = EmbedImage(**self.thumbnail)
        self.fields = [
            EmbedField(**field) if isinstance(field, dict) else field
            for field in self.fields
        ]