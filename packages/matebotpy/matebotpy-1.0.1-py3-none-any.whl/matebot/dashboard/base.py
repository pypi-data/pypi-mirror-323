from dataclasses import dataclass
from typing import List

@dataclass
class Stats:
    guilds: int
    shards: int
    users: int
    premium_servers: int
    api_subscribers: int

@dataclass
class User:
    username: str
    userid: str
    globalname: str
    avatar: str
    apikey: str
    subscription: int
    expire: int

@dataclass
class Guild:
    id: str
    name: str
    icon: str
    banner: str

@dataclass
class GuildResponse:
    guilds: List[Guild]
    guildsnot: List[Guild]

    def __post_init__(self):
        self.guilds = [Guild(**g) if isinstance(g, dict) else g for g in self.guilds]
        self.guildsnot = [Guild(**g) if isinstance(g, dict) else g for g in self.guildsnot]