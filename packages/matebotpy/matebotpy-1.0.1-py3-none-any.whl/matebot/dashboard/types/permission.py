from dataclasses import dataclass
from typing import List

@dataclass
class Permission:
    """
    Permission types:

    ~~~~~~~~~~
    1: Who have these roles
    2: Who doesn't have these roles
    ~~~~~~~~~~
    """
    type: int

    member: bool
    roles: List[str]

    def add_role(self, role: str) -> None:
        self.roles.append(role)
    
    def set_roles(self, roles: List[str]) -> None:
        self.roles = roles
    
    def set_role(self, index: int, role: str) -> None:
        self.roles[index] = role
    
    def remove_role(self, index: int) -> None:
        del self.roles[index]
    
    def remove_role_by_id(self, role: str) -> None:
        self.roles = [r for r in self.roles if r != role]

@dataclass
class DPermission:
    """
    Permission types:

    ~~~~~~~~~~
    1: Who have these roles
    2: Who doesn't have these roles
    ~~~~~~~~~~
    """
    type: int

    roles: List[str]

    def add_role(self, role: str) -> None:
        self.roles.append(role)
    
    def set_roles(self, roles: List[str]) -> None:
        self.roles = roles
    
    def set_role(self, index: int, role: str) -> None:
        self.roles[index] = role
    
    def remove_role(self, index: int) -> None:
        del self.roles[index]
    
    def remove_role_by_id(self, role: str) -> None:
        self.roles = [r for r in self.roles if r != role]

@dataclass
class Channels:
    """
    Channels types:

    ~~~~~~~~~~
    1: Only in these channels
    2: All, except these channels
    ~~~~~~~~~~
    """
    type: int

    channels: List[str]

    def add_channel(self, channel: str) -> None:
        if channel not in self.channels:
            self.channels.append(channel)
    
    def set_channels(self, channels: List[str]) -> None:
        self.channels = channels
    
    def set_channel(self, index: int, channel: str) -> None:
        self.channels[index] = channel
    
    def remove_channel(self, index: int) -> None:
        del self.channels[index]
    
    def remove_channel_by_id(self, channel: str) -> None:
        self.channels = [ch for ch in self.channels if ch != channel]