from dataclasses import dataclass
from typing import List
from matebot.dashboard.types import Embed, ActionRow, Image

@dataclass
class WelcomeMessage:
    message: bool
    channelid: str
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

    image: bool

    imagedata: Image
    
    def set_image(self, image: Image) -> None:
        self.image = image

    def __post_init__(self):
        self.embeds = [Embed(**embed) if isinstance(embed, dict) else embed for embed in self.embeds]
        self.actionrows = [ActionRow(**row) if isinstance(row, dict) else row for row in self.actionrows]
        if isinstance(self.imagedata, dict):
            self.imagedata = Image(**self.imagedata)

@dataclass
class GoodbyeMessage:
    message: bool
    channelid: str
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

    image: bool

    imagedata: Image
    
    def set_image(self, image: Image) -> None:
        self.image = image

    def __post_init__(self):
        self.embeds = [Embed(**embed) if isinstance(embed, dict) else embed for embed in self.embeds]
        self.actionrows = [ActionRow(**row) if isinstance(row, dict) else row for row in self.actionrows]
        if isinstance(self.imagedata, dict):
            self.imagedata = Image(**self.imagedata)

@dataclass
class WelcomePrivateMessage:
    message: bool
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

    image: bool

    imagedata: Image
    
    def set_image(self, image: Image) -> None:
        self.image = image

    def __post_init__(self):
        self.embeds = [Embed(**embed) if isinstance(embed, dict) else embed for embed in self.embeds]
        self.actionrows = [ActionRow(**row) if isinstance(row, dict) else row for row in self.actionrows]
        if isinstance(self.imagedata, dict):
            self.imagedata = Image(**self.imagedata)

@dataclass
class Welcome:
    welcome: WelcomeMessage

    def set_welcome(self, welcome: WelcomeMessage) -> None:
        self.welcome = welcome

    goodbye: GoodbyeMessage
    
    def set_goodbye(self, goodbye: GoodbyeMessage) -> None:
        self.goodbye = goodbye
        
    private: WelcomePrivateMessage
    
    def set_private(self, private: WelcomePrivateMessage) -> None:
        self.private = private

    def __post_init__(self):
        if isinstance(self.welcome, dict):
            self.welcome = WelcomeMessage(**self.welcome)
        if isinstance(self.goodbye, dict):
            self.goodbye = GoodbyeMessage(**self.goodbye)
        if isinstance(self.welcome, dict):
            self.private = WelcomePrivateMessage(**self.private)