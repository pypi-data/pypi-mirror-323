from dataclasses import dataclass
from typing import List
from matebot.dashboard.types import Action

@dataclass 
class TempChannel:
    channelid: str
    category: str
    name: str
    limit: int

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
        self.actions = [Action(**action) if isinstance(action, dict) else action for action in self.actions]
    
@dataclass
class TempChannelSettings:
    value: bool

    channels: List[TempChannel]

    def add_channel(self, channel: TempChannel) -> None:
        self.channels.append(channel)
    
    def set_channels(self, channels: List[TempChannel]) -> None:
        self.channels = channels
    
    def set_channel(self, index: int, channel: TempChannel) -> None:
        self.channels[index] = channel
    
    def remove_channel(self, index: int) -> None:
        del self.channels[index]
    
    def remove_channel_by_id(self, id: str) -> None:
        self.channels = [ch for ch in self.channels if ch.channelid != id]

    def __post_init__(self):
        self.channels = [TempChannel(**channel) if isinstance(channel, dict) else channel for channel in self.channels]