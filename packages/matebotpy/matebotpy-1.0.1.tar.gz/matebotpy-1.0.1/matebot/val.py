import aiohttp
from matebot.valorant import WebsocketEvent, Weapon, Buddy, Character, LevelBorder, PlayerCard, Spray, Theme, ContentTier, Bundle, Map
from matebot.websocket import WebsocketClient, WebsocketClosed
from matebot.base import Notfound, NotLoaded
from typing import Optional, List, Callable, Dict, Any
import asyncio

ValorantLanguages = [
    "en",
    "de",
    "es",
    "fr",
    "id",
    "it",
    "pt-BR",
    "ar",
    "pl",
    "ru",
    "tr",
    "ch-TW",
    "vi",
    "th",
    "ja",
    "ko"
]

class ValorantCache:
    def __init__(self):
        self.weapons: List[Weapon]
        self.melee: Weapon
        self.buddies: List[Buddy]
        self.characters: List[Character]
        self.levelborders: List[LevelBorder]
        self.playercards: List[PlayerCard]
        self.sprays: List[Spray]
        self.themes: Dict[str, Theme]
        self.contenttiers: Dict[str, ContentTier]
        self.bundles: List[Bundle]
        self.maps: List[Map]

class ValorantClient:
    def __init__(self, api_key: str, *, base_url: Optional[str] = None, log: bool = False):
        self._api_key = api_key
        self._base_url = "https://api.matebot.xyz/val/" if not base_url else base_url+"/"
        self._ws_listeners: List[Callable[[WebsocketEvent], None]] = []
        self._ws_connect: List[Callable[[], None]] = []
        self._ws_disconnect: List[Callable[[], None]] = []
        self._websocket_connection: WebsocketClient
        self.heartbeat_interval: int = 20
        self._log: bool = log
        self.max_retries: int = 10
        self.retry_delay: int = 180
        self.session: Optional[aiohttp.ClientSession] = None
        self._cache: Dict[str, ValorantCache] = {}
    
    async def init(self) -> None:
        self.session = aiohttp.ClientSession(self._base_url)

    def data(self, lang: str) -> ValorantCache:
        return self._cache[lang]
    
    def remove_data(self, lang: str) -> None:
        del self._cache[lang]
    
    async def setup(self, lang: str) -> None:
        if not any(l.lower() == lang.lower() for l in ValorantLanguages):
            raise Exception("Language not found.")
        newCache = ValorantCache()
        (
            newCache.weapons,
            newCache.melee,
            newCache.buddies,
            newCache.characters,
            newCache.levelborders,
            newCache.playercards,
            newCache.sprays,
            newCache.themes,
            newCache.contenttiers,
            newCache.bundles,
            newCache.maps,
        ) = await asyncio.gather(
            self.fetch_weapons(lang=lang),
            self.fetch_melee(lang=lang),
            self.fetch_buddies(lang=lang),
            self.fetch_characters(lang=lang),
            self.fetch_levelborders(lang=lang),
            self.fetch_playercards(lang=lang),
            self.fetch_sprays(lang=lang),
            self.fetch_themes(lang=lang),
            self.fetch_contenttiers(lang=lang),
            self.fetch_bundles(lang=lang),
            self.fetch_maps(lang=lang),
        )
        self._cache[lang] = newCache
        if self._on_change not in self._ws_listeners:
            self._ws_listeners.append(self._on_change)
        
    async def _on_change(self, event: WebsocketEvent) -> None:
        tasks = []
        task_info = []

        if event.type == "CHARACTERS":
            func = self.fetch_characters
        elif event.type == "WEAPONS":
            func = self.fetch_weapons
        elif event.type == "MEELE":
            func = self.fetch_melee
        elif event.type == "BUDDIES":
            func = self.fetch_buddies
        elif event.type == "LEVELBORDERS":
            func = self.fetch_levelborders
        elif event.type == "PLAYERCARDS":
            func = self.fetch_playercards
        elif event.type == "SPRAYS":
            func = self.fetch_sprays
        elif event.type == "THEMES":
            func = self.fetch_themes
        elif event.type == "CONTENTTIERS":
            func = self.fetch_contenttiers
        elif event.type == "BUNDLES":
            func = self.fetch_bundles
        else:
            return

        for lang in event.data.languages:
            if not self._cache[lang]:
                continue

            tasks.append(func(lang=lang))
            task_info.append(lang)
        
        results = await asyncio.gather(*tasks)

        for lang, result in zip(task_info, results):
            if event.type == "CHARACTERS":
                self._cache[lang].characters = result
            elif event.type == "WEAPONS":
                self._cache[lang].weapons = result
            elif event.type == "MELEE":
                self._cache[lang].melee = result
            elif event.type == "BUDDIES":
                self._cache[lang].buddies = result
            elif event.type == "LEVELBORDERS":
                self._cache[lang].levelborders = result
            elif event.type == "PLAYERCARDS":
                self._cache[lang].playercards = result
            elif event.type == "SPRAYS":
                self._cache[lang].sprays = result
            elif event.type == "THEMES":
                self._cache[lang].themes = result
            elif event.type == "CONTENTTIERS":
                self._cache[lang].contenttiers = result
            elif event.type == "BUNDLES":
                self._cache[lang].bundles = result

    def _get_headers(self):
        return {
            "X-API-KEY": self._api_key
        }
    
    async def _request(self, method: str, url: str, *, auth: Optional[bool]=True, lang:Optional[str]) -> Any:
        url = url[1:]
        if lang:
            url+="?lang="+lang
        async with self.session.request(method,url,headers=self._get_headers() if auth else None) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 404:
                raise Notfound()
            elif response.status == 503:
                raise NotLoaded()
            else:
                raise Exception(f"Request failed: {response.status} - {await response.text()}")

    def add_guild_update_handler(self, listener: Callable[[WebsocketEvent], None]) -> None:
        self._ws_listeners.append(listener)

    def add_guild_update_handler_connect(self, listener: Callable[[], None]) -> None:
        self._ws_connect.append(listener)

    def add_guild_update_handler_disconnect(self, listener: Callable[[], None]) -> None:
        self._ws_listeners.append(listener)
    
    async def _on_message(self, _, data: Any):
        for i in self._ws_listeners:
            asyncio.create_task(i(WebsocketEvent(**data)))

    async def _on_connect(self, _):
        for i in self._ws_connect:
            asyncio.create_task(i(id))

    async def _on_disconnect(self, _):
        for i in self._ws_disconnect:
            asyncio.create_task(i())

    async def run(self):
        retries = 0
        while True:
            try:
                ws = WebsocketClient(self._base_url.replace("https", "wss")+"ws?apikey="+self._api_key, log=self._log)
                self._websocket_connection = ws
                ws.on_message = self._on_message
                ws.onconnect = self._on_connect
                try:
                    await ws.connect()
                except WebsocketClosed:
                    if not self._websocket_connection:
                        return
                    retries = 0
                    self._websocket_connection = None
                    asyncio.create_task(self._on_disconnect())
                    raise WebsocketClosed()
                except Exception as e:
                    self._websocket_connection = None
                    raise e
            except Exception as e:
                if retries >= self.max_retries:
                    raise Exception("All connection attempts failed. Stopping retries.")
                retries+=1
                if self._log:
                    print(f"Connection failed. Retrying in {self.retry_delay} seconds... ({retries}/{self.max_retries})\nError: {e}")
                await asyncio.sleep(self.retry_delay)

    async def close(self):
        await self._websocket_connection.close()
        self._websocket_connection = None

    async def ping(self) -> int:
        ws = self._websocket_connection
        return await ws.ping()
    
    async def fetch_weapons(self, lang: Optional[str]=None) -> List[Weapon]:
        return [Weapon(**weapon) for weapon in await self._request("get", "/weapons", lang=lang)]
    
    async def fetch_melee(self, lang: Optional[str]=None) -> Weapon:
        return Weapon(**await self._request("get", "/melee", lang=lang))
    
    async def fetch_buddies(self, lang: Optional[str]=None) -> List[Buddy]:
        return [Buddy(**buddy) for buddy in await self._request("get", "/buddies", lang=lang)]
    
    async def fetch_characters(self, lang: Optional[str]=None) -> List[Character]:
        return [Character(**character) for character in await self._request("get", "/characters", lang=lang)]
    
    async def fetch_levelborders(self, lang: Optional[str]=None) -> List[LevelBorder]:
        return [LevelBorder(**levelborder) for levelborder in await self._request("get", "/levelborders", lang=lang)]
    
    async def fetch_playercards(self, lang: Optional[str]=None) -> List[PlayerCard]:
        return [PlayerCard(**playercard) for playercard in await self._request("get", "/playercards", lang=lang)]
    
    async def fetch_sprays(self, lang: Optional[str]=None) -> List[Spray]:
        return [Spray(**spray) for spray in await self._request("get", "/sprays", lang=lang)]
    
    async def fetch_themes(self, lang: Optional[str]=None) -> Dict[str, Theme]:
        resp = await self._request("get", "/themes", lang=lang)
        return {
            key: Theme(**data)
            for key, data in resp.items()
        }

    async def fetch_contenttiers(self, lang: Optional[str]=None) -> Dict[str, ContentTier]:
        resp = await self._request("get", "/contenttiers", lang=lang)
        return {
            key: ContentTier(**data)
            for key, data in resp.items()
        }
    
    async def fetch_bundles(self, lang: Optional[str]=None) -> List[Bundle]:
        return [Bundle(**bundle) for bundle in await self._request("get", "/bundles", lang=lang)]
    
    async def fetch_maps(self, lang: Optional[str]=None) -> List[Map]:
        return [Map(**mapdata) for mapdata in await self._request("get", "/maps", lang=lang)]