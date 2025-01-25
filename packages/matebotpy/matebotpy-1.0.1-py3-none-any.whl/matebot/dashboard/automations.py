from dataclasses import dataclass
from typing import List
from matebot.dashboard.types import Action, DPermission, Channels

@dataclass
class MessageAutomation:
    """
    MessageAutomation types:

    ~~~~~~~~~~
    1: Message Startswith
    2: Message Endswith
    3: Message Contain
    4: Message Regex
    5: Message Equal
    ~~~~~~~~~~
    """
    type: int

    content: str

    actions: List[Action]

    def add_action(self, action: Action) -> None:
        self.actions.append(action)

    def set_actions(self, actions: List[Action]) -> None:
        self.actions = actions
    
    def set_action(self, index: int, action: Action) -> None:
        self.actions[index] = action
    
    def remove_action(self, index: int) -> None:
        del self.actions[index]

    permission: DPermission

    def set_permission(self, permission: DPermission) -> None:
        self.permission = permission

    channels: Channels
    
    def set_channels(self, channels: Channels) -> None:
        self.channels = channels

    cooldown: int
    isglobal: bool
    shared: bool

    def __post_init__(self):
        self.actions = [Action(**action) if isinstance(action, dict) else action for action in self.actions]
        
        if isinstance(self.permission, dict):
            self.permission = DPermission(**self.permission)
        
        if isinstance(self.channels, dict):
            self.channels = Channels(**self.channels)

@dataclass
class Automation:
    """
    Automation types:

    ~~~~~~~~~~
    1: Message Create
    2: Message Update (content)
    3: Message Delete
    4: Message Delete Bulk
    5: Message Reaction Add
    6: Message Reaction Remove
    7: Message Reaction Remove All
    8: Role Create
    9: Role Update
    10: Role Delete
    11: Channel Create
    12: Channel Update
    13: Channel Delete
    14: Invite Create
    15: Invite Delete
    16: Ban Add
    17: Ban Remove
    18: Member Join
    19: Member Remove
    20: Member Kick
    21: Member Update
    22: User Update
    23: Guild Update
    24: Guild Update (emojis)
    ~~~~~~~~~~
    """
    type: int

    actions: List[Action]
    cooldown: int

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
class AutomationsData:
    message: List[MessageAutomation]

    def add_message_automation(self, automation: MessageAutomation) -> None:
        self.message.append(automation)
    
    def set_message_automations(self, automations: List[MessageAutomation]) -> None:
        self.message = automations
    
    def set_message_automation(self, index: int, automation: MessageAutomation) -> None:
        self.message[index] = automation

    normal: List[Automation]

    def add_automation(self, automation: Automation) -> None:
        self.normal.append(automation)
    
    def set_automations(self, automations: List[Automation]) -> None:
        self.normal = automations
    
    def set_automation(self, index: int, automation: Automation) -> None:
        self.normal[index] = automation
    
    def remove_automation(self, index: int) -> None:
        del self.normal[index]

    def __post_init__(self):
        self.message = [MessageAutomation(**msg) if isinstance(msg, dict) else msg for msg in self.message]
        self.normal = [Automation(**auto) if isinstance(auto, dict) else auto for auto in self.normal]