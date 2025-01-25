from dataclasses import dataclass
from typing import List
from matebot.dashboard.types import Image, Channels, DPermission, Action
from matebot.dashboard.builtin import Message

@dataclass
class LevelMultiplier:
    channels: Channels

    def set_channels(self, channels: Channels) -> None:
        self.channels = channels

    permission: DPermission

    def set_permission(self, permission: DPermission) -> None:
        self.permission = permission

    amount: float

    def __post_init__(self):
        if isinstance(self.channels, dict):
            self.channels = Channels(**self.channels) 
        if isinstance(self.permission, dict):
            self.permission = DPermission(**self.permission) 

@dataclass
class LevelAutomation:
    level: str

    permission: DPermission

    def set_permission(self, permission: DPermission) -> None:
        self.permission = permission

    actions: List[Action]

    def add_action(self, action: Action) -> None:
        self.actions.append(action)
    
    def set_actions(self, actions: List[Action]) -> None:
        self.actions = actions
    
    def set_action(self, index: int, action: Action) -> None:
        self.actions[index] = action

    def remove_action(self, index: int) -> None:
        del self.actions[index]
    
    def __post_init__(self):
        if isinstance(self.permission, dict):
            self.permission = DPermission(**self.permission) 
        self.actions = [Action(**action) if isinstance(action, dict) else action for action in self.actions]

@dataclass
class LevelSettings:
    """
    Levelup message types:

    ~~~~~~~~~~
    0: None
    1: Current Channel
    2: Private Channel
    3: Channel
    ~~~~~~~~~~
    """
    type: int

    channelid: str
    message: Message
    image: bool
    imagedata: Image
    multipliers: List[LevelMultiplier]
    automations: List[LevelAutomation]

    def __post_init__(self):
        self.multipliers = [LevelMultiplier(**multiplier) if isinstance(multiplier, dict) else multiplier for multiplier in self.multipliers]
        self.automations = [LevelAutomation(**automation) if isinstance(automation, dict) else automation for automation in self.automations]
        if isinstance(self.message, dict):
            self.message = Message(**self.message)
        if isinstance(self.imagedata, dict):
            self.imagedata = Image(**self.imagedata)