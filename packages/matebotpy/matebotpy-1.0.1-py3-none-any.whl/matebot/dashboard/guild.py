from matebot.dashboard.types import Channel, Role, Guild as GuildData
from matebot.dashboard.welcome import Welcome
from matebot.dashboard.defender import Defender
from matebot.dashboard.automations import AutomationsData
from matebot.dashboard.moderation import WarnAutomation, Warn
from matebot.dashboard.builtin import Builtin
from matebot.dashboard.slash import SlashCommands
from matebot.dashboard.levels import LevelSettings
from matebot.dashboard.giveaway import Giveaway
from matebot.dashboard.tempchannels import TempChannelSettings
from typing import List, Any

class Guild:
    def __init__(self, id: str, *, client: Any, auto_update: bool=False):
        self.id: str = id
        self.owner: bool
        self.name: str
        self.membercount: int
        self.channels: List[Channel]
        self.categories: List[Channel]
        self.voices: List[Channel]
        self.roles: List[Role]
        self.premium: bool
        self._auto_update: bool = auto_update
        self._client = client
        self._client.add_guild_update_handler(self.id, self._handle_updates)

    async def fetch(self) -> None:
        g = await self._client._fetch_guild(self.id)
        await self.parse(g)

    async def parse(self, g: GuildData) -> None:
        self.owner = g.owner
        self.name = g.name
        self.membercount = g.membercount
        self.categories = g.categories
        self.channels = g.channels
        self.voices = g.voices
        self.roles = g.roles
        self.premium = g.premium

    async def _handle_updates(self, id, g: GuildData):
        if id == self.id and self._auto_update:
            await self.parse(g)
    
    async def fetch_welcome(self) -> Welcome:
        return Welcome(**await self._client._request("get", f"/dashboard/{self.id}/welcome"))

    async def set_welcome(self, data: Welcome) -> None:
        await self._client._request("post", f"/dashboard/{self.id}/welcome", data=data)
    
    async def fetch_defender(self) -> Defender:
        return Defender(**await self._client._request("get", f"/dashboard/{self.id}/defender"))
    
    async def set_defender(self, data: Defender) -> None:
        await self._client._request("post", f"/dashboard/{self.id}/defender", data=data)
    
    async def fetch_automations(self) -> AutomationsData:
        return [AutomationsData(**automation) for automation in await self._client._request("get", f"/dashboard/{self.id}/automations")]
    
    async def set_automations(self, data: AutomationsData) -> None:
        await self._client._request("post", f"/dashboard/{self.id}/automations", data=data)

    async def fetch_warn_automations(self) -> List[WarnAutomation]:
        return [WarnAutomation(**item) for item in await self._client._request("get", f"/dashboard/{self.id}/warns")]

    async def set_warn_automations(self, automations: List[WarnAutomation]) -> None:
        await self._client._request("post", f"/dashboard/{self.id}/warns", data=automations)
    
    async def check_user_warnings(self, userid: str) -> List[Warn]:
        return [Warn(**item) for item in await self._client._request("get", f"/dashboard/{self.id}/warns/{userid}")]
    
    async def del_user_warn(self, userid: str, time: int) -> None:
        await self._client._request("delete", f"/dashboard/{self.id}/warns/{userid}/{time}")
    
    async def fetch_builtin(self) -> Builtin:
        return Builtin(**await self._client._request("get", f"/dashboard/{self.id}/builtin"))

    async def set_builtin(self, builtin: Builtin) -> None:
        await self._client._request("post", f"/dashboard/{self.id}/builtin", data=builtin)
    
    async def get_slashcommands(self) -> SlashCommands:
        return SlashCommands(**await self._client._request("get", f"/dashboard/{self.id}/slash"))

    async def set_slashcommands(self, commands: SlashCommands) -> None:
        await self._client._request("post", f"/dashboard/{self.id}/slash", data=commands)

    async def get_level_settings(self) -> LevelSettings:
        return LevelSettings(**await self._client._request("get", f"/dashboard/{self.id}/levels"))
    
    async def set_level_settings(self, settings: LevelSettings) -> None:
        await self._client._request("post", f"/dashboard/{self.id}/levels", data=settings)
        
    async def get_giveaways(self) -> List[Giveaway]:
        return [Giveaway(**gw) for gw in await self._client._request("get", f"/dashboard/{self.id}/giveaways")]

    async def set_giveaway(self, giveaway: Giveaway) -> None:
        await self._client._request("post", f"/dashboard/{self.id}/giveaways", data=giveaway)
    
    async def delete_giveaway(self, channelid: str, messageid: str) -> None:
        await self._client._request("delete", f"/dashboard/{self.id}/giveaways?channelid={channelid}&messageid={messageid}")

    async def get_tempchannels(self) -> TempChannelSettings:
        return TempChannelSettings(**await self._client._request("get", f"/dashboard/{self.id}/tempchannels"))
    
    async def set_tempchannels(self, channels: TempChannelSettings) -> None:
        await self._client._request("post", f"/dashboard/{self.id}/tempchannels", data=channels)
    
    async def send_message(self, type: int, channelid: str, messageid: str, message: str) -> None:
        await self._client._request("post", f"/dashboard/{self.id}/message", data={"type": type, "channelid": channelid, "messageid": messageid, "message": message})