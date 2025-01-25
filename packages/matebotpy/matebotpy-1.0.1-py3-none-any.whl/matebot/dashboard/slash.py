from dataclasses import dataclass
from typing import List, Dict
from matebot.dashboard.types import DPermission, Action

@dataclass
class SlashCommandOptionChoice:
    name: str

    namelocalizations: Dict[str, str]

    def set_name_localization(self, lang: str, value: str) -> None:
        self.namelocalizations[lang] = value
    
    def remove_name_localization(self, lang: str) -> None:
        del self.namelocalizations[lang]

    value: str

@dataclass
class SlashCommandOption:
    """
    SlashCommandOption types:

    ~~~~~~~~~~
    1: Text
    2: Integer
    3: Float
    4: Boolean
    5: Time
    6: User
    7: User (not in the server)
    8: Member
    9: Member (with smaller roles)
    10: Role
    11: Role (smaller roles)
    12: Channel
    13: Role or User (mentionables)
    14: Attachment
    ~~~~~~~~~~
    """
    type: int

    name: str

    namelocalizations: Dict[str, str]

    def set_name_localization(self, lang: str, value: str) -> None:
        self.namelocalizations[lang] = value
    
    def remove_name_localization(self, lang: str) -> None:
        del self.namelocalizations[lang]

    description: str

    descriptionlocalizations: Dict[str, str]

    def set_description_localization(self, lang: str, value: str) -> None:
        self.descriptionlocalizations[lang] = value
    
    def remove_description_localization(self, lang: str) -> None:
        del self.descriptionlocalizations[lang]

    """
    Channel types:

    ~~~~~~~~~~
    1: Category
    2: Text
    3: Voice
    4: Announcements
    5: Forum
    6: Stage
    ~~~~~~~~~~
    """
    channeltypes: List[int]

    def add_channel_type(self, type: int) -> None:
        self.channeltypes.append(type)
    
    def set_channel_types(self, types: List[int]) -> None:
        self.channeltypes = types
    
    def set_channel_type(self, index: int, type: int) -> None:
        self.channeltypes[index] = type
    
    def remove_channel_type(self, index: int) -> None:
        del self.channeltypes[index]

    minlength: str
    maxlength: str
    regex: str
    min: str
    max: str

    choices: List[SlashCommandOptionChoice]
    
    def add_choice(self, choice: SlashCommandOptionChoice) -> None:
        self.choices.append(choice)
    
    def set_choices(self, choices: List[SlashCommandOptionChoice]) -> None:
        self.choices = choices
    
    def set_choice(self, index: int, choice: SlashCommandOptionChoice) -> None:
        self.choices[index] = choice
    
    def remove_choice(self, index: int) -> None:
        del self.choices[index]
        
    required: bool

    def __post_init__(self):
        self.choices = [SlashCommandOptionChoice(**choice) if isinstance(choice, dict) else choice for choice in self.choices]

@dataclass
class SlashCommand:
    name: str
    description: str

    descriptionlocalizations: Dict[str, str]

    def set_description_localization(self, lang: str, value: str) -> None:
        self.descriptionlocalizations[lang] = value
    
    def remove_description_localization(self, lang: str) -> None:
        del self.descriptionlocalizations[lang]

    subgroup: str
    subcommand: str

    subcommandlocalizations: Dict[str, str]

    def set_subcommand_localization(self, lang: str, value: str) -> None:
        self.subcommandlocalizations[lang] = value
    
    def remove_subcommand_localization(self, lang: str) -> None:
        del self.subcommandlocalizations[lang]

    options: List[SlashCommandOption]

    def add_option(self, option: SlashCommandOption) -> None:
        self.options.append(option)
    
    def set_options(self, options: List[SlashCommandOption]) -> None:
        self.options = options
    
    def set_option(self, index: int, option: SlashCommandOption) -> None:
        self.options[index] = option
    
    def remove_option(self, index: int) -> None:
        del self.options[index]

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

    erractions: List[Action]

    def add_error_action(self, action: Action) -> None:
        self.erractions.append(action)
    
    def set_error_actions(self, actions: List[Action]) -> None:
        self.erractions = actions
    
    def set_error_action(self, index: int, action: Action) -> None:
        self.erractions[index] = action
    
    def remove_error_action(self, index: int) -> None:
        del self.erractions[index]

    permactions: List[Action]

    def add_permission_action(self, action: Action) -> None:
        self.permactions.append(action)
    
    def set_permission_actions(self, actions: List[Action]) -> None:
        self.permactions = actions
    
    def set_permission_action(self, index: int, action: Action) -> None:
        self.permactions[index] = action
    
    def remove_permission_action(self, index: int) -> None:
        del self.permactions[index]

    cooldownactions: List[Action]

    def add_cooldown_action(self, action: Action) -> None:
        self.cooldownactions.append(action)
    
    def set_cooldown_actions(self, actions: List[Action]) -> None:
        self.cooldownactions = actions
    
    def set_cooldown_action(self, index: int, action: Action) -> None:
        self.cooldownactions[index] = action
    
    def remove_cooldown_action(self, index: int) -> None:
        del self.cooldownactions[index]

    cooldown: int
    shared: bool
    id: str

    def __post_init__(self):
        if isinstance(self.permission, dict):
            self.permission = DPermission(**self.permission)
        self.actions = [Action(**action) if isinstance(action, dict) else action for action in self.actions]
        self.erractions = [Action(**action) if isinstance(action, dict) else action for action in self.erractions]
        self.permactions = [Action(**action) if isinstance(action, dict) else action for action in self.permactions]
        self.cooldownactions = [Action(**action) if isinstance(action, dict) else action for action in self.cooldownactions]

@dataclass
class Localization:
    """
    Localization types:

    ~~~~~~~~~~
    1: Root Name (like /mycommand)
    2: SubGroup (like /mycommand [mysubgroup] [mysubcommand]) if the command have name with 3 word length
    ~~~~~~~~~~
    """
    type: int

    name: str

    namelocalizations: Dict[str, str]

    def set_name_localization(self, lang: str, value: str) -> None:
        self.namelocalizations[lang] = value
    
    def remove_name_localization(self, lang: str) -> None:
        del self.namelocalizations[lang]

@dataclass
class SlashCommands:
    commands: List[SlashCommand]
    localizations: List[Localization]

    def add_command(self, command: SlashCommand) -> None:
        self.commands.append(command)
    
    def set_commands(self, commands: List[SlashCommand]) -> None:
        self.commands = commands
    
    def set_command(self, index: int, command: SlashCommand) -> None:
        self.commands[index] = command
    
    def remove_command(self, index: int) -> None:
        del self.commands[index]
    
    def remove_command_by_id(self, id: str) -> None:
        self.commands = [cmd for cmd in self.commands if cmd.id != id]
    
    def add_localization(self, localization: Localization) -> None:
        self.localizations.append(localization)
    
    def set_localizations(self, localizations: List[Localization]) -> None:
        self.localizations = localizations
    
    def set_localization(self, index: int, localization: Localization) -> None:
        self.localizations[index] = localization
    
    def remove_localization(self, index: int) -> None:
        del self.localizations[index]

    def __post_init__(self):
        self.commands = [SlashCommand(**command) if isinstance(command, dict) else command for command in self.commands]
        self.localizations = [Localization(**localization) if isinstance(localization, dict) else localization for localization in self.localizations]