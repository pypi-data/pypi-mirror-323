from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ActionMessageDeleteChoice:
    """
    Channel types:

    ~~~~~~~~~~
    1: Current Channel
    2: Private Channel
    3: Custom Channel
    ~~~~~~~~~~
    """
    channel: int

    """
    This field is required if the channel type is 3.
    """
    channelid: str

    """
    The ID of the message to delete. 
    """
    messageid: str

    """
    The amount of messages you want to delete (if the message type is 5).
    """
    count: str

    """
    Bulk Delete Parameters
    """
    parameters: str

@dataclass
class ActionMessageChoice:
    """
    Channel types:

    ~~~~~~~~~~
    1: Current Channel
    2: Private Channel
    3: Custom Channel
    ~~~~~~~~~~
    """
    channel: int

    """
    This field is required if the channel type is 3.
    """
    channelid: str

    """
    This field is required if the message type is 2 (use 'interaction' for interaction replies).
    """
    messageid: str

    """
    The member for the message (e.g. view warnings)
    """
    member: str

    """
    The ID of the message to send (from the built-in section)
    """
    message: str

    """
    If true, the message will be visible only to the user who initiated the interaction.
    This is typically used for ephemeral responses to user interactions, ensuring 
    that only the user who interacted with the bot can see the message.
    """
    ephemeral: bool

    """
    If true, the bot will mention the user when replying to a message or interaction.
    This is useful when you want to notify or draw the user's attention to the response, 
    especially in cases where the bot is replying to a previous message or an interaction.
    """
    mention: bool

@dataclass
class ActionMessage:
    """
    Description of ActionMessage types:
    
    ~~~~~~~~~~
    1: Send - Sends a message.
    2: Reply - Replies to an existing message.
    3: Edit - Edits an existing message.
    4: Delete - Deletes a message.
    5: Bulk Delete - Deletes multiple messages.
    ~~~~~~~~~~
    """
    type: int

    """ 
    'choices' is used for action types 1, 2, and 3.
    A list of 'ActionMessageChoice' objects that represent the choices for the action (send, reply, edit).
    The bot will randomly select one of the available choices for the action.
    """
    choices: List[ActionMessageChoice]

    def add_choice(self, choice: ActionMessageChoice) -> None:
        self.choices.append(choice)

    def set_choices(self, choices: List[ActionMessageChoice]) -> None:
        self.choices = choices
    
    def set_choice(self, index: int, choice: ActionMessageChoice) -> None:
        self.choices[index] = choice
    
    def del_choice(self, index: int) -> None:
        del self.choices[index]

    """ 
    'delchoices' is used for action types 4 and 5.
    A list of 'ActionMessageDeleteChoice' objects that represent the choices for deleting messages.
    The bot will randomly select one of the available delete choices for the action.
    """
    delchoices: List[ActionMessageDeleteChoice]
    
    def add_delchoice(self, choice: ActionMessageDeleteChoice) -> None:
        self.delchoices.append(choice)
    
    def set_delchoices(self, choices: List[ActionMessageDeleteChoice]) -> None:
        self.delchoices = choices
    
    def set_delchoice(self, index: int, choice: ActionMessageDeleteChoice) -> None:
        self.delchoices[index] = choice
    
    def del_delchoice(self, index: int) -> None:
        del self.delchoices[index]

    def __post_init__(self):
        self.choices = [ActionMessageChoice(**choice) if isinstance(choice, dict) else choice for choice in self.choices]
        self.delchoices = [ActionMessageDeleteChoice(**delchoice) if isinstance(delchoice, dict) else delchoice for delchoice in self.delchoices]

@dataclass
class ActionRoleChoice:
    member: str
    roleid: str
    reason: str

@dataclass
class ActionRole:
    """
    Description of ActionRole types:
    
    ~~~~~~~~~~
    1: Add - Adds a role to a user.
    2: Remove - Removes a role from a user.
    3: Toggle - Toggles the role (adds if not present, removes if present).
    4: Create - Creates a new role.
    5: Delete - Deletes a role.
    ~~~~~~~~~~
    """
    type: int

    """ 
    'choices' is used for action types 1, 2, and 3.
    A list of 'ActionRoleChoice' objects that represent the choices for the action.
    The bot will randomly select one of the choices for the action.
    """
    choices: List[ActionRoleChoice]

    def add_choice(self, choice: ActionRoleChoice) -> None:
        self.choices.append(choice)

    def set_choices(self, choices: List[ActionRoleChoice]) -> None:
        self.choices = choices
    
    def set_choice(self, index: int, choice: ActionRoleChoice) -> None:
        self.choices[index] = choice
    
    def del_choice(self, index: int) -> None:
        del self.choices[index]

    """
    'roles' is used for action types 4 and 5.
    A list of role names or ids involved in the action.
    """
    roles: List[str]

    def add_manage_choice(self, choice: str) -> None:
        self.roles.append(choice)

    def set_manage_choices(self, choices: List[str]) -> None:
        self.roles = choices

    def set_manage_choice(self, index: int, choice: str) -> None:
        self.roles[index] = choice
    
    def del_manage_choice(self, index: int) -> None:
        del self.roles[index]

    def __post_init__(self):
        self.choices = [ActionRoleChoice(**choice) if isinstance(choice, dict) else choice for choice in self.choices]

@dataclass
class ActionChannelChoice:
    """
    The channel types
    
    ~~~~~~~~~~
    1: Category
    2: Text
    3: Voice
    4: Announcement
    5: Forum
    6: Stage
    ~~~~~~~~~~
    """
    type: int
    category: str
    name: str

    """
    Grants permission to the interaction user.
    """
    permission: bool

@dataclass
class ActionChannelEditChoice:
    channelid: str
    name: str

@dataclass
class ActionChannel:
    """
    Description of ActionChannel types:
    
    ~~~~~~~~~~
    1: Create - Create a new channel in the server.
    2: Delete - Delete a channel from the server.
    3: Edit - Update the name if a channel.
    ~~~~~~~~~~
    """
    type: int

    """
    For ActionChannel type 1: 
    The bot will select an ActionChannelChoice from the list and create a channel based on the selected choice.
    """
    choices: List[ActionChannelChoice]

    def add_create_choice(self, choice: ActionChannelChoice) -> None:
        self.choices.append(choice)

    def set_create_choices(self, choices: List[ActionChannelChoice]) -> None:
        self.choices = choices

    def set_create_choice(self, index: int, choice: ActionChannelChoice) -> None:
        self.choices[index] = choice
    
    def del_create_choice(self, index: int) -> None:
        del self.choices[index]

    """
    For ActionChannel type 2: 
    The bot will select an ID from the list and delete the corresponding channel.
    """
    channelids: List[str]

    def add_delete_choice(self, choice: str) -> None:
        self.channelids.append(choice)

    def set_delete_choices(self, choices: List[str]) -> None:
        self.channelids = choices

    def set_delete_choice(self, index: int, choice: str) -> None:
        self.channelids[index] = choice
    
    def del_delete_choice(self, index: int) -> None:
        del self.channelids[index]

    """
    For ActionChannel type 3: 
    The bot will select an ActionChannelEditChoice from the list and edit the channel based on the selected choice.
    """
    editchoices: List[ActionChannelEditChoice]

    def add_edit_choice(self, choice: ActionChannelEditChoice) -> None:
        self.editchoices.append(choice)

    def set_edit_choices(self, choices: List[ActionChannelEditChoice]) -> None:
        self.editchoices = choices
    
    def set_edit_choice(self, index: int, choice: ActionChannelEditChoice) -> None:
        self.editchoices[index] = choice
    
    def del_edit_choice(self, index: int) -> None:
        del self.editchoices[index]

    def __post_init__(self):
        self.choices = [ActionChannelChoice(**choice) if isinstance(choice, dict) else choice for choice in self.choices]
        self.editchoices = [ActionChannelEditChoice(**choice) if isinstance(choice, dict) else choice for choice in self.editchoices]

@dataclass
class ActionBan:
    user: str

    """
    The time range, in seconds, within which messages will be deleted. 
    This is used to remove messages sent by the user within the specified time when they are banned.
    """
    delete: str

    reason: str

@dataclass
class ActionUnban:
    user: str
    reason: str

@dataclass
class ActionKick:
    member: str
    reason: str

@dataclass
class ActionMute:
    member: str

    """
    The duration in seconds for the mute.
    """
    time: str

    reason: str

@dataclass
class ActionGiveaway:
    """
    Description of ActionGiveaway types:
    
    ~~~~~~~~~~
    1: Join - Adds the user to the giveaway.
    2: Leave - Removes the user from the giveaway.
    3: Toggle - Toggles the user's participation.
    4: End - Ends the giveaway and selects a winner.
    5: Reroll - Selects new winner(s) for the giveaway.
    6: Delete - Deletes the giveaway and removes all data.
    ~~~~~~~~~~
    """
    type: int

    channelid: str
    messageid: str
    member: str

@dataclass
class ActionWebsocketField:
    key: str
    value: str

@dataclass
class ActionWebsocket:
    fields: List[ActionWebsocketField]

    def add_field(self, key: str, value: str) -> None:
        self.fields.append(ActionWebsocketField(key, value))
    
    def set_fields(self, fields: List[ActionWebsocketField]) -> None:
        self.fields = fields
    
    def set_field(self, index: int, field: ActionWebsocketField) -> None:
        self.fields[index] = field
    
    def remove_field(self, index: int) -> None:
        del self.fields[index]

    def __post_init__(self):
        self.fields = [ActionWebsocketField(**field) if isinstance(field, dict) else field for field in self.fields]

@dataclass
class ActionWarning:
    """
    Types of ActionWarning:
    
    ~~~~~~~~~~
    1: Add
    2: Remove
    3: Clear
    ~~~~~~~~~~
    """
    type: int

    author: str
    userid: str
    reason: str
    number: str

@dataclass
class ActionReactionChoice:
    channelid: str
    messageid: str
    userid: str
    emoji: str

@dataclass
class ActionReaction:
    """
    Types of ActionReaction:
    
    ~~~~~~~~~~
    1: Add 
    2: Remove
    3: Remove All (emoji)
    4: Remove All (reactions)
    ~~~~~~~~~~
    """
    type: int
    choices: List[ActionReactionChoice]

    def add_choice(self, choice: ActionReactionChoice) -> None:
        self.choices.append(choice)
    
    def set_choices(self, choices: List[ActionReactionChoice]) -> None:
        self.choices = choices
    
    def set_choice(self, index: int, choice: ActionReactionChoice) -> None:
        self.choices[index] = choice
    
    def remove_choice(self, index: int) -> None:
        del self.choices[index]
    
    def __post_init__(self):
        self.choices = [ActionReactionChoice(**choice) if isinstance(choice, dict) else choice for choice in self.choices]

@dataclass
class ActionXP:
    """
    Types of ActionXP:
    
    ~~~~~~~~~~
    1: Add 
    2: Remove
    3: Set
    ~~~~~~~~~~
    """
    type: int

    userid: str
    amount: str

@dataclass
class ActionEconomy:
    """
    Types of ActionEconomy:
    
    ~~~~~~~~~~
    1: Remove Cash
    2: Remove Bank
    3: Add Cash
    4: Add Bank]
    5: Withdrawal
    6: Deposit
    ~~~~~~~~~~
    """
    type: int

    userid: str
    amount: str

@dataclass
class Action:
    """
    Action types:

    ~~~~~~~~~~
    1: Message
    2: Role
    3: Channel
    4: Ban
    5: Unban
    6: Kick
    7: Mute
    8: Giveaway
    9: Websocket
    10: Warning
    11: Reaction
    12: XP
    13: Economy
    14: Interaction Response (Message Update with no data)
    15: Interaction Response (Deferred Channel Message)
    16: Interaction Response (Deferred Message Update)
    ~~~~~~~~~~
    """
    type: int

    message: Optional[ActionMessage]
    role: Optional[ActionRole]
    channel: Optional[ActionChannel]
    ban: Optional[ActionBan]
    unban: Optional[ActionUnban]
    kick: Optional[ActionKick]
    mute: Optional[ActionMute]
    giveaway: Optional[ActionGiveaway]
    websocket: Optional[ActionWebsocket]
    warning: Optional[ActionWarning]
    reaction: Optional[ActionReaction]
    xp: Optional[ActionXP]
    economy: Optional[ActionEconomy]

    def __post_init__(self):
        if isinstance(self.message, dict):
            self.message = ActionMessage(**self.message)
        if isinstance(self.role, dict):
            self.role = ActionRole(**self.role)
        if isinstance(self.channel, dict):
            self.channel = ActionChannel(**self.channel)
        if isinstance(self.ban, dict):
            self.ban = ActionBan(**self.ban)
        if isinstance(self.unban, dict):
            self.unban = ActionUnban(**self.unban)
        if isinstance(self.kick, dict):
            self.kick = ActionKick(**self.kick)
        if isinstance(self.mute, dict):
            self.mute = ActionMute(**self.mute)
        if isinstance(self.giveaway, dict):
            self.giveaway = ActionGiveaway(**self.giveaway)
        if isinstance(self.websocket, dict):
            self.websocket = ActionWebsocket(**self.websocket)
        if isinstance(self.warning, dict):
            self.warning = ActionWarning(**self.warning)
        if isinstance(self.reaction, dict):
            self.reaction = ActionReaction(**self.reaction)
        if isinstance(self.xp, dict):
            self.xp = ActionXP(**self.xp)
        if isinstance(self.economy, dict):
            self.economy = ActionEconomy(**self.economy)