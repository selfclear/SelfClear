import os
import aiohttp
import asyncio
import time
import random
from dotenv import load_dotenv

title = "Romania Self Clear"
os.system(f"title {title}")

load_dotenv()
token = os.getenv("TOKEN")
delay = int(os.getenv("DELAY", 0))

y_color = f"\x1b[38;2;{random.randint(0,255)};{random.randint(0,255)};{random.randint(0,255)}m"

color = lambda n: {
    "z": "\x1b[0m",
    "g": "\x1b[38;2;56;72;83m",
    "y": y_color,
}.get(n, "\x1b[0m")

timestamp = lambda: f"{color('y')}[{color('g')}{time.strftime('%H:%M:%S')}{color('y')}] {color('g')}[{color('y')}●{color('g')}] {color('z')}"

def clear_cmd():
    os.system("cls" if os.name == "nt" else "clear")

logo = """
                                 ██████╗  █████╗ ███╗   ███╗ █████╗ ███╗  ██╗██╗ █████╗ 
                                 ██╔══██╗██╔══██╗████╗ ████║██╔══██╗████╗ ██║██║██╔══██╗
                                 ██████╔╝██║  ██║██╔████╔██║███████║██╔██╗██║██║███████║
                                 ██╔══██╗██║  ██║██║╚██╔╝██║██╔══██║██║╚████║██║██╔══██║
                                 ██║  ██║╚█████╔╝██║ ╚═╝ ██║██║  ██║██║ ╚███║██║██║  ██║
                                 ╚═╝  ╚═╝ ╚════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚══╝╚═╝╚═╝  ╚═╝
""".replace(
    "█", color("y") + "█" + color("g")
)

semaphore = asyncio.Semaphore(5)


def system_message(m):
    return m.get("author", {}).get("id") == user_id and m.get("type", 0) not in [
        3, 4, 6, 12, 13, 24, 25
    ]


async def delete_message(session, channel_id, message_id):
    async with semaphore:
        while True:
            async with session.delete(
                f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}",
                headers={"Authorization": token},
            ) as resp:

                if resp.status == 204:
                    print(f"{timestamp()} » Deleted → {color('y')}[{color('g')}{message_id}{color('y')}]")
                    await asyncio.sleep(delay)
                    return

                elif resp.status == 429:
                    await asyncio.sleep(1)

                else:
                    return


async def listing_clear(session, channel_id):
    before = None

    while True:
        params = {"limit": 100}
        if before:
            params["before"] = before

        async with session.get(
            f"https://discord.com/api/v9/channels/{channel_id}/messages",
            headers={"Authorization": token},
            params=params,
        ) as resp:

            if resp.status != 200:
                break

            messages = await resp.json()

        if not messages:
            break

        tasks = []

        for message in messages:
            before = message["id"]

            if not system_message(message):
                continue

            tasks.append(
                asyncio.create_task(
                    delete_message(session, channel_id, message["id"])
                )
            )

        if tasks:
            await asyncio.gather(*tasks)


async def search_clear(session, url):
    off = 0

    while True:
        async with session.get(
            f"{url}&offset={off}",
            headers={"Authorization": token},
        ) as resp:

            if resp.status != 200:
                break

            data = await resp.json()

        groups = data.get("messages", [])
        if not groups:
            break

        tasks = []
        found = False

        for group in groups:
            for message in group:

                if not system_message(message):
                    continue

                tasks.append(
                    asyncio.create_task(
                        delete_message(
                            session,
                            message["channel_id"],
                            message["id"],
                        )
                    )
                )

                found = True

        if tasks:
            await asyncio.gather(*tasks)

        if not found:
            break

        off += 25


async def clear_dm(session):
    print(logo)

    async with session.get(
        "https://discord.com/api/v9/users/@me/channels",
        headers={"Authorization": token},
    ) as resp:
        channels = await resp.json()

    channels = [d for d in channels if d.get("type") in (1, 3)]
    random.shuffle(channels)

    for d in channels:

        channel_id = d["id"]

        name = (
            d.get("recipients", [{}])[0].get("username")
            if d["type"] == 1
            else d.get("name", "Unnamed Group")
        )

        print(f"{timestamp()} » Clearing → {color('y')}[{color('g')}{name}{color('y')}]")

        await listing_clear(session, channel_id)

    await asyncio.sleep(2)
    clear_cmd()


async def listing_clear_chat(session):
    print(logo)

    channel_id = input(f"{timestamp()} » Channel ID → ").strip()

    clear_cmd()
    print(logo)

    await listing_clear(session, channel_id)

    await asyncio.sleep(2)
    clear_cmd()


async def search_clear_chat(session):
    print(logo)

    channel_id = input(f"{timestamp()} » Channel ID → ").strip()

    async with session.get(
        f"https://discord.com/api/v9/channels/{channel_id}",
        headers={"Authorization": token},
    ) as resp:
        data = await resp.json()

    guild = data.get("guild_id")

    url = f"https://discord.com/api/v9/{'guilds/' + guild if guild else 'channels/' + channel_id}/messages/search?author_id={user_id}"

    if guild:
        url += f"&channel_id={channel_id}"

    clear_cmd()
    print(logo)

    await search_clear(session, url)

    await asyncio.sleep(2)
    clear_cmd()


async def guild_clear(session):
    print(logo)

    guild_id = input(f"{timestamp()} » Guild ID → ").strip()

    clear_cmd()
    print(logo)

    await search_clear(
        session,
        f"https://discord.com/api/v9/guilds/{guild_id}/messages/search?author_id={user_id}",
    )

    await asyncio.sleep(2)
    clear_cmd()


async def main():

    global user_id, username

    async with aiohttp.ClientSession() as session:

        async with session.get(
            "https://discord.com/api/v9/users/@me",
            headers={"Authorization": token},
        ) as resp:
            client = await resp.json()

        user_id = client["id"]
        username = client["username"]

        while True:

            clear_cmd()
            print(logo)

            print(
                f"{timestamp()} » Welcome → {color('y')}[{color('g')}{username}{color('y')}]\n"
                f"{timestamp()} » {color('y')}[{color('g')}1{color('y')}] {color('z')}DM Clear → {color('y')}[{color('g')}Listing{color('y')}]\n"
                f"{timestamp()} » {color('y')}[{color('g')}2{color('y')}] {color('z')}Chat Clear → {color('y')}[{color('g')}Listing{color('y')}]\n"
                f"{timestamp()} » {color('y')}[{color('g')}3{color('y')}] {color('z')}Chat Clear → {color('y')}[{color('g')}Search{color('y')}]\n"
                f"{timestamp()} » {color('y')}[{color('g')}4{color('y')}] {color('z')}Guild Clear → {color('y')}[{color('g')}Search{color('y')}]"
            )

            ch = input(f"{timestamp()} » Choose → ").strip()

            clear_cmd()

            if ch == "1":
                await clear_dm(session)

            elif ch == "2":
                await listing_clear_chat(session)

            elif ch == "3":
                await search_clear_chat(session)

            elif ch == "4":
                await guild_clear(session)


asyncio.run(main())
