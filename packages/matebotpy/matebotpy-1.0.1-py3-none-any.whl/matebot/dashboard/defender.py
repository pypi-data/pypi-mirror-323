from dataclasses import dataclass
from typing import List
from matebot.dashboard.types import Action, DPermission, Channels

@dataclass
class DefenderDefault:
    value: bool
    time: int
    max: str
    permission: DPermission
    actions: List[Action]

    def add_action(self, action: Action) -> None:
        self.actions.append(action)
    
    def set_actions(self, actions: List[Action]) -> None:
        self.actions = actions
    
    def set_action(self, index: int, action: Action) -> None:
        self.actions[index] = action

    def remove_action(self, index: int) -> None:
        del self.actions[index]

    def set_permission(self, permission: DPermission) -> None:
        self.permission = permission
    
    def __post_init__(self):
        if isinstance(self.permission, dict):
            self.permission = DPermission(**self.permission)
        self.actions = [Action(**action) if isinstance(action, dict) else action for action in self.actions]

@dataclass
class DefenderMessage:
    value: bool
    time: int
    max: str
    permission: DPermission
    channels: Channels
    actions: List[Action]

    def add_action(self, action: Action) -> None:
        self.actions.append(action)
    
    def set_actions(self, actions: List[Action]) -> None:
        self.actions = actions
    
    def set_action(self, index: int, action: Action) -> None:
        self.actions[index] = action

    def remove_action(self, index: int) -> None:
        del self.actions[index]

    def set_permission(self, permission: DPermission) -> None:
        self.permission = permission

    def set_channels(self, channels: Channels) -> None:
        self.channels = channels

    def __post_init__(self):
        if isinstance(self.permission, dict):
            self.permission = DPermission(**self.permission)
        if isinstance(self.channels, dict):
            self.channels = Channels(**self.channels)
        self.actions = [Action(**action) if isinstance(action, dict) else action for action in self.actions]

@dataclass
class Defender:
    ban: DefenderDefault
    kick: DefenderDefault
    invite: DefenderMessage

    def __post_init__(self):
        if isinstance(self.ban, dict):
            self.ban = DefenderDefault(**self.ban)
        if isinstance(self.kick, dict):
            self.kick = DefenderDefault(**self.kick)
        if isinstance(self.invite, dict):
            self.invite = DefenderMessage(**self.invite)