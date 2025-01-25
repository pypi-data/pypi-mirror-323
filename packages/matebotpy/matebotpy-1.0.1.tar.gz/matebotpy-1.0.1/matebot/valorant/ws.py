from dataclasses import dataclass
from typing import List

@dataclass
class WebsocketEventData:
    """
    Valorant Languages:

    ~~~~~~~~~~
    "en": English
    "de": German
    "es": Spanish
    "fr": French
    "id": Indonesian
    "it": Italian
    "pt-BR": Portuguese (Brazil)
    "ar": Arabic
    "pl": Polish
    "ru": Russian
    "tr": Turkish
    "zh-TW": Chinese (Traditional, Taiwan)
    "vi": Vietnamese
    "th": Thai
    "ja": Japanese
    "ko": Korean
    ~~~~~~~~~~
    """
    languages: List[str]

@dataclass
class WebsocketEvent:
    type: str
    data: WebsocketEventData
    timestamp: int

    def __post_init__(self):
        if isinstance(self.data, dict):
            self.data = WebsocketEventData(**self.data)