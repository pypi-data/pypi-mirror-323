from dataclasses import dataclass
from typing import List
from matebot.dashboard.types import ActionRow, PageActionRow, Embed

@dataclass
class Message:
    content: str
    embeds: List[Embed]

    def add_embed(self, embed: Embed) -> None:
        self.embeds.append(embed)
    
    def set_embeds(self, embeds: List[Embed]) -> None:
        self.embeds = embeds
    
    def set_embed(self, index: int, embed: Embed) -> None:
        self.embeds[index] = embed
    
    def remove_embed(self, index: int) -> None:
        del self.embeds[index]

    actionrows: List[ActionRow]

    def add_actionrow(self, actionrow: ActionRow) -> None:
        self.actionrows.append(actionrow)
    
    def set_actionrows(self, actionrows: List[ActionRow]) -> None:
        self.actionrows = actionrows
    
    def set_actionrow(self, index: int, actionrow: ActionRow) -> None:
        self.actionrows[index] = actionrow
    
    def remove_actionrow(self, index: int) -> None:
        del self.actionrows[index]

    def __post_init__(self):
        self.embeds = [Embed(**embed) if isinstance(embed, dict) else embed for embed in self.embeds]
        self.actionrows = [ActionRow(**actionrow) if isinstance(actionrow, dict) else actionrow for actionrow in self.actionrows]

@dataclass
class BuiltinMessage:
    content: str

    embeds: List[Embed]

    def add_embed(self, embed: Embed) -> None:
        self.embeds.append(embed)
    
    def set_embeds(self, embeds: List[Embed]) -> None:
        self.embeds = embeds
    
    def set_embed(self, index: int, embed: Embed) -> None:
        self.embeds[index] = embed
    
    def remove_embed(self, index: int) -> None:
        del self.embeds[index]

    actionrows: List[ActionRow]

    def add_actionrow(self, actionrow: ActionRow) -> None:
        self.actionrows.append(actionrow)
    
    def set_actionrows(self, actionrows: List[ActionRow]) -> None:
        self.actionrows = actionrows
    
    def set_actionrow(self, index: int, actionrow: ActionRow) -> None:
        self.actionrows[index] = actionrow
    
    def remove_actionrow(self, index: int) -> None:
        del self.actionrows[index]

    id: str

    def __post_init__(self):
        self.embeds = [Embed(**embed) if isinstance(embed, dict) else embed for embed in self.embeds]
        self.actionrows = [ActionRow(**actionrow) if isinstance(actionrow, dict) else actionrow for actionrow in self.actionrows]

@dataclass
class BuiltinPageBasic:
    max: str
    count: str
    content: str

    embeds: List[Embed]

    def add_embed(self, embed: Embed) -> None:
        self.embeds.append(embed)
    
    def set_embeds(self, embeds: List[Embed]) -> None:
        self.embeds = embeds
    
    def set_embed(self, index: int, embed: Embed) -> None:
        self.embeds[index] = embed
    
    def remove_embed(self, index: int) -> None:
        del self.embeds[index]

    actionrows: List[PageActionRow]

    def add_actionrow(self, actionrow: PageActionRow) -> None:
        self.actionrows.append(actionrow)
    
    def set_actionrows(self, actionrows: List[PageActionRow]) -> None:
        self.actionrows = actionrows
    
    def set_actionrow(self, index: int, actionrow: PageActionRow) -> None:
        self.actionrows[index] = actionrow
    
    def remove_actionrow(self, index: int) -> None:
        del self.actionrows[index]

    def __post_init__(self):
        self.embeds = [Embed(**embed) if isinstance(embed, dict) else embed for embed in self.embeds]
        self.actionrows = [PageActionRow(**actionrow) if isinstance(actionrow, dict) else actionrow for actionrow in self.actionrows]

    
@dataclass
class BuiltinWithErr:
    success: Message
    error: Message

    def __post_init__(self):
        if isinstance(self.success, dict):
            self.success = Message(**self.success)

        if isinstance(self.success, dict):
            self.error = Message(**self.error)

@dataclass
class BuiltinPageWithErr:
    success: BuiltinPageBasic
    error: Message

    def __post_init__(self):
        if isinstance(self.success, dict):
            self.success = BuiltinPageBasic(**self.success)

        if isinstance(self.error, dict):
            self.error = Message(**self.error)

@dataclass
class Builtin:
    clear: Message
    warning: BuiltinWithErr
    warnings: BuiltinPageWithErr
    delwarning: BuiltinWithErr
    clearwarnings: Message
    mute: BuiltinWithErr
    rankcard: Message
    xpleaderboard: BuiltinPageBasic
    balance: Message
    ecoleaderboard: BuiltinPageBasic
    giveaway: Message
    giveawayend: Message
    giveawayreroll: Message
    messages: List[BuiltinMessage]

    def add_message(self, message: BuiltinMessage) -> None:
        self.messages.append(message)
    
    def set_messages(self, messages: List[BuiltinMessage]) -> None:
        self.messages = messages
    
    def set_message(self, index: int, message: BuiltinMessage) -> None:
        self.messages[index] = message
    
    def remove_message(self, index: int) -> None:
        del self.messages[index]
    
    def remove_message_by_id(self, id: str) -> None:
        self.messages = [message for message in self.messages if message.id != id]

    def __post_init__(self):
        self.clear = Message(**self.clear) if isinstance(self.clear, dict) else self.clear
        self.warning = BuiltinWithErr(**self.warning) if isinstance(self.warning, dict) else self.warning
        self.warnings = BuiltinPageWithErr(**self.warnings) if isinstance(self.warnings, dict) else self.warnings
        self.delwarning = BuiltinWithErr(**self.delwarning) if isinstance(self.delwarning, dict) else self.delwarning
        self.clearwarnings = Message(**self.clearwarnings) if isinstance(self.clearwarnings, dict) else self.clearwarnings
        self.mute = BuiltinWithErr(**self.mute) if isinstance(self.mute, dict) else self.mute
        self.rankcard = Message(**self.rankcard) if isinstance(self.rankcard, dict) else self.rankcard
        self.xpleaderboard = BuiltinPageBasic(**self.xpleaderboard) if isinstance(self.xpleaderboard, dict) else self.xpleaderboard
        self.balance = Message(**self.balance) if isinstance(self.balance, dict) else self.balance
        self.ecoleaderboard = BuiltinPageBasic(**self.ecoleaderboard) if isinstance(self.ecoleaderboard, dict) else self.ecoleaderboard
        self.giveaway = Message(**self.giveaway) if isinstance(self.giveaway, dict) else self.giveaway
        self.giveawayend = Message(**self.giveawayend) if isinstance(self.giveawayend, dict) else self.giveawayend
        self.giveawayreroll = Message(**self.giveawayreroll) if isinstance(self.giveawayreroll, dict) else self.giveawayreroll
        self.messages = [BuiltinMessage(**msg) if isinstance(msg, dict) else msg for msg in self.messages]