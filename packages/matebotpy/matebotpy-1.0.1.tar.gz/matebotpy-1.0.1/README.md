# Python library for [Matebot](https://matebot.xyz)
The Python Library for Matebot is a simple and powerful library designed for retrieving and editing data from Matebot.

## Installation
```
pip install matebotpy
```

## ValorantClient Usage
Little console application to get weapon skins from Valorant using ValorantClient
`await client.init()` means wait for initializing aiohttp for the requests, `await setup("en")` will fetch the data from the API in English language and set up the websocket handler
`asyncio.create_task(client.run())` means: start the websocket in the background to handle updates
```py
from matebot import ValorantClient
from matebot.valorant import WeaponSkin
import asyncio

client = ValorantClient("YOUR_API_KEY")

async def setup():
    await client.init()
    await client.setup("en")
    asyncio.create_task(client.run())

asyncio.run(setup())

def print_skin_data(skin: WeaponSkin):
    print(f"\
        name: {skin.name}\n\
        icon: {skin.icon}\n\
        wallpaper: {skin.wallpaper}\n\
        ")

while True:
    data = client.data("en")
    print(f"{len(data.weapons)} weapons loaded;")

    weapns = [i.name for i in data.weapons]
    for i in weapns:
        print(i)
    key = input("Enter the weapon you want to get: ")
    
    selected_weapons = [obj for obj in data.weapons if obj.name.lower() == key.lower()]
    if len(selected_weapons) == 0:
        print("weapon not found")
        continue
    
    weapon = selected_weapons[0]
    skin = input("search skin: ")

    searched_skins = [value for value in weapon.skins.values() if skin.lower() in value.name.lower()]
    if len(searched_skins) == 0:
        print("skin not found")
        continue

    if len(searched_skins) == 1:
        print_skin_data(searched_skins[0], searched_skins[0])
    else:
        print(f"{len(searched_skins)} skins found:")
        for value in searched_skins:
            print(value.name)
        name = input("Enter the skin's name: ")

        selected_skins = [value for value in searched_skins if value.name.lower() == name.lower()]
        if len(selected_skins) == 0:
            print("skin not found")
            continue

        print_skin_data(selected_skins[0])
```

And what should I do if I don't want it to automatically refresh the data?
```py
from matebot import ValorantClient
import asyncio

client = ValorantClient("YOUR_API_KEY")

async def main():
    await client.init()

    weapons = await client.fetch_weapons()
    for weapon in weapons:
        print(weapon.name)

asyncio.run(main())
```

## FortniteClient Usage
Example of printing all character names in the console
```py
from matebot import FortniteClient
import asyncio

client = FortniteClient("YOUR_API_KEY")

async def setup():
    await client.init()
    await client.setup("en")
    asyncio.create_task(client.run())

asyncio.run(setup())

data = client.data("en")
for characterid, character in data.cosmetics.br.characters.items():
    print(character.name)
```

Example of fetching stats using the console:
```py
from matebot import FortniteClient, Notfound
import asyncio

client = FortniteClient("YOUR_API_KEY")

async def main():
    await client.init()
    while True:
        name = input("Enter your fortnite name: ")
        platform = input("Enter your platform (epic/xbl/psn): ")
        try:
            data = await client.fetch_stats(name, platform=platform) # You can use start_time and end_time parameter
        except Notfound:
            print('User not found.')
            continue
        except Exception as e:
            print(e)
            continue
        if not data.stats:
            print("User stats is private.")
            continue
        keyboardmouse_solo_kills = int(data.stats["br_kills_keyboardmouse_m0_playlist_defaultsolo"]) if "br_kills_keyboardmouse_m0_playlist_defaultsolo" in data.stats.keys() else 0
        print(f"Keyboardmouse solo kills: {keyboardmouse_solo_kills}")
        print("\nOther stats:")
        for name, value in data.stats.items():
            print(f"{name}: {value}")

asyncio.run(main())
```

## DashboardClient Usage
Example of listening to websocket events:

```py
from matebot import DashboardClient
import asyncio
from typing import Dict

client = DashboardClient("YOUR_AUTHORIZATION_TOKEN")

async def on_event(guildid: str, data: Dict[str, str]):
    print(guildid, data["message"])

client.add_guild_event_handler(on_event)

async def main():
    await client.init()
    await client.run_event_listener("GUILD_ID")

asyncio.run(main())
```

# Links
- [Discord Server](https://dc.matebot.xyz/)
- [Donate](https://www.paypal.com/donate/?hosted_button_id=A4G73GWEWSHLU)