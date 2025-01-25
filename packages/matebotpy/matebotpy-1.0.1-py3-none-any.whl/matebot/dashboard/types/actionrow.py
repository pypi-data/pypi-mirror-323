from dataclasses import dataclass
from typing import List
from matebot.dashboard.types.action import Action
from matebot.dashboard.types.permission import Permission

@dataclass
class Emoji:
    """
    Emoji types:

    ~~~~~~~~~~
    0: None
    1: Normal Emoji
    2: Discord Emoji
    ~~~~~~~~~~
    """
    type: int
    name: str
    id: str
    animated: bool

@dataclass
class Form:
    label: str
    placeholder: str
    long: bool
    required: bool
    min: str
    max: str
    value: str

@dataclass
class ActionStruct:
    actions: List[Action]

    def add_action(self, action: Action) -> None:
        self.actions.append(action)
    
    def set_actions(self, actions: List[Action]) -> None:
        self.actions = actions
    
    def set_action(self, index: int, action: Action) -> None:
        self.actions[index] = action
    
    def remove_action(self, index: int) -> None:
        del self.actions[index]

    title: str

    forms: List[Form]

    def add_form(self, form: Form) -> None:
        self.forms.append(form)
    
    def set_forms(self, forms: List[Form]) -> None:
        self.forms = forms

    def set_form(self, index: int, form: Form) -> None:
        self.forms[index] = form
    
    def remove_form(self, index: int) -> None:
        del self.forms[index]
    
    def __post_init__(self):
        self.forms = [Form(**form) if isinstance(form, dict) else form for form in self.forms]
        self.actions = [Action(**action) if isinstance(action, dict) else action for action in self.actions]

@dataclass
class Button:
    """
    Button styles:

    ~~~~~~~~~~
    1: Primary (blue)
    2: Secondary (grey)
    3: Success (green)
    4: Danger (red)
    5: Link (grey)
    ~~~~~~~~~~
    """
    style: int

    disabled: bool
    label: str
    url: str
    emoji: Emoji
    action: ActionStruct
    erractions: List[Action]
    permactions: List[Action]
    cooldownactions: List[Action]
    cooldown: int
    isglobal: bool
    shared: bool
    permission: Permission

    def add_error_action(self, action: Action) -> None:
        self.erractions.append(action)
    
    def set_error_actions(self, actions: List[Action]) -> None:
        self.erractions = actions
    
    def set_error_action(self, index: int, action: Action) -> None:
        self.erractions[index] = action
    
    def remove_error_action(self, index: int) -> None:
        del self.erractions[index]
    
    def add_permission_action(self, action: Action) -> None:
        self.permactions.append(action)
    
    def set_permission_actions(self, actions: List[Action]) -> None:
        self.permactions = actions
    
    def set_permission_action(self, index: int, action: Action) -> None:
        self.permactions[index] = action
    
    def remove_permission_action(self, index: int) -> None:
        del self.permactions[index]

    def add_cooldown_action(self, action: Action) -> None:
        self.cooldownactions.append(action)
    
    def set_cooldown_actions(self, actions: List[Action]) -> None:
        self.cooldownactions = actions
    
    def set_cooldown_action(self, index: int, action: Action) -> None:
        self.cooldownactions[index] = action
    
    def remove_cooldown_action(self, index: int) -> None:
        del self.cooldownactions[index]
    
    def set_permission(self, perm: Permission) -> None:
        self.permission = perm
    
    def set_emoji(self, emoji: Emoji) -> None:
        self.emoji = emoji

    def __post_init__(self):
        if isinstance(self.emoji, dict):
            self.emoji = Emoji(**self.emoji)
        if isinstance(self.action, dict):
            self.action = ActionStruct(**self.action)
        self.erractions = [Action(**action) if isinstance(action, dict) else action for action in self.erractions]
        self.permactions = [Action(**action) if isinstance(action, dict) else action for action in self.permactions]
        self.cooldownactions = [Action(**action) if isinstance(action, dict) else action for action in self.cooldownactions]

@dataclass
class Option:
    label: str
    description: str
    emoji: Emoji
    permission: Permission
    action: ActionStruct
    erractions: List[Action]
    permactions: List[Action]
    cooldownactions: List[Action]
    cooldown: int
    isglobal: bool
    shared: bool
    
    def remove_error_action(self, index: int) -> None:
        del self.erractions[index]
    
    def add_permission_action(self, action: Action) -> None:
        self.permactions.append(action)
    
    def set_permission_actions(self, actions: List[Action]) -> None:
        self.permactions = actions
    
    def set_permission_action(self, index: int, action: Action) -> None:
        self.permactions[index] = action
    
    def remove_permission_action(self, index: int) -> None:
        del self.permactions[index]

    def add_cooldown_action(self, action: Action) -> None:
        self.cooldownactions.append(action)
    
    def set_cooldown_actions(self, actions: List[Action]) -> None:
        self.cooldownactions = actions
    
    def set_cooldown_action(self, index: int, action: Action) -> None:
        self.cooldownactions[index] = action
    
    def remove_cooldown_action(self, index: int) -> None:
        del self.cooldownactions[index]
    
    def set_permission(self, perm: Permission) -> None:
        self.permission = perm
    
    def set_emoji(self, emoji: Emoji) -> None:
        self.emoji = emoji

    def __post_init__(self):
        if isinstance(self.emoji, dict):
            self.emoji = Emoji(**self.emoji)
        if isinstance(self.action, dict):
            self.action = ActionStruct(**self.action)
        self.erractions = [Action(**action) if isinstance(action, dict) else action for action in self.erractions]
        self.permactions = [Action(**action) if isinstance(action, dict) else action for action in self.permactions]
        self.cooldownactions = [Action(**action) if isinstance(action, dict) else action for action in self.cooldownactions]

@dataclass
class SelectMenu:
    """
    SelectMenu types:

    ~~~~~~~~~~
    1: Normal
    2: Users
    3: Roles
    4: Mentionables
    5: Channels
    ~~~~~~~~~~
    """
    type: int

    placeholder: str
    disabled: bool
    options: List[Option]

    def add_option(self, option: Option) -> None:
        self.options.append(option)
    
    def set_options(self, options: List[Option]) -> None:
        self.options = options
    
    def set_option(self, index: int, option: Option) -> None:
        self.options[index] = option
    
    def remove_option(self, index: int) -> None:
        del self.options[index]

    def __post_init__(self):
        self.options = [Option(**option) if isinstance(option, dict) else option for option in self.options]

@dataclass
class ActionRow:
    """
    ActionRow types:

    ~~~~~~~~~~
    1: Buttons
    2: SelectMenu
    ~~~~~~~~~~
    """
    type: int
    buttons: List[Button]
    selectmenu: SelectMenu

    def add_button(self, button: Button) -> None:
        self.buttons.append(button)
    
    def set_buttons(self, buttons: List[Button]) -> None:
        self.buttons = buttons
    
    def set_button(self, index: int, button: Button) -> None:
        self.buttons[index] = button
    
    def remove_button(self, index: Button) -> None:
        del self.buttons[index]

    def __post_init__(self):
        self.buttons = [Button(**button) if isinstance(button, dict) else button for button in self.buttons]
        if isinstance(self.selectmenu, dict):
            self.selectmenu = SelectMenu(**self.selectmenu)

@dataclass
class PageButton:
    """
    PageButton types:

    ~~~~~~~~~~
    0: Normal
    1: Next
    2: Previous
    3: Set
    ~~~~~~~~~~
    """
    type: int
    
    count: str
    button: Button

    def __post_init__(self):
        if isinstance(self.button, dict):
            self.button = Button(**self.button)

@dataclass
class PageOption:
    """
    PageButton types:

    ~~~~~~~~~~
    0: Normal
    1: Next
    2: Previous
    3: Set
    ~~~~~~~~~~
    """
    type: int
    
    count: str
    option: Option

    def __post_init__(self):
        if isinstance(self.option, dict):
            self.option = Option(**self.option)

@dataclass
class PageSelectMenu:
    type: int

    placeholder: str
    disabled: bool
    options: List[PageOption]

    def add_option(self, option: PageOption) -> None:
        self.options.append(option)
    
    def set_options(self, options: List[PageOption]) -> None:
        self.options = options
    
    def set_option(self, index: int, option: PageOption) -> None:
        self.options[index] = option
    
    def remove_option(self, index: PageOption) -> None:
        del self.options[index]

    def __post_init__(self):
        self.options = [PageOption(**option) if isinstance(option, dict) else option for option in self.options]

@dataclass
class PageActionRow:
    type: int

    buttons: List[PageButton]
    selectmenu: PageSelectMenu

    def add_button(self, button: PageButton) -> None:
        self.buttons.append(button)
    
    def set_buttons(self, buttons: List[PageButton]) -> None:
        self.buttons = buttons
    
    def set_button(self, index: int, button: PageButton) -> None:
        self.buttons[index] = button
    
    def remove_button(self, index: PageButton) -> None:
        del self.buttons[index]

    def __post_init__(self):
        self.buttons = [PageButton(**button) if isinstance(button, dict) else button for button in self.buttons]
        if isinstance(self.selectmenu, dict):
            self.selectmenu = PageSelectMenu(**self.selectmenu)