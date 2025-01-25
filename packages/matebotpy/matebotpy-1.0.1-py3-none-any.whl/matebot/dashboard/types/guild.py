from dataclasses import dataclass
from typing import List

@dataclass
class Channel:
    id: str
    position: int
    parentid: str
    name: str

@dataclass
class Role:
    id: str
    position: int
    color: str
    name: str

@dataclass
class Guild:
    owner: bool
    name: str
    membercount: int
    channels: List[Channel]
    categories: List[Channel]
    voices: List[Channel]
    roles: List[Role]
    premium: bool

    def __post_init__(self):
        self.channels = [Channel(**channel) if isinstance(channel, dict) else channel for channel in self.channels]
        self.categories = [Channel(**channel) if isinstance(channel, dict) else channel for channel in self.categories]
        self.voices = [Channel(**channel) if isinstance(channel, dict) else channel for channel in self.voices]
        self.roles = [Role(**role) if isinstance(role, dict) else role for role in self.roles]