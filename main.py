import os
import requests
import time
import random
from dotenv import load_dotenv

title = "Romania Self Clear"
os.system(f"title {title}")

load_dotenv()
token = os.getenv("TOKEN")
delay = int(os.getenv("DELAY", 0))

timestamp = (lambda: f"{color('y')}[{color('g')}{time.strftime('%H:%M:%S')}{color('y')}] {color('g')}[{color('y')}●{color('g')}]" + color("z"))
y_color = f"\x1b[38;2;{random.randint(0,255)};{random.randint(0,255)};{random.randint(0,255)}m"

def clear_cmd():
    os.system("cls" if os.name == "nt" else "clear")

client = requests.get("https://discord.com/api/v9/users/@me", headers={"Authorization": token}).json()

user_id = client["id"]
username = client["username"]

color = lambda n: {
    "z": "\x1b[0m",
    "g": "\x1b[38;2;56;72;83m",
    "y": y_color,
}.get(n, "\x1b[0m")


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


def system_message(m):
    return m.get("author", {}).get("id") == user_id and m.get("type", 0) not in [
        3,
        4,
        6,
        12,
        13,
        24,
        25,
    ]


def listing_clear(channel_id, name=None):
    before = None
    while True:
        params = {"limit": 100}
        if before:
            params["before"] = before
        request = requests.get(
            f"https://discord.com/api/v9/channels/{channel_id}/messages",
            headers={"Authorization": token},
            params=params,
        )
        messages = request.json() if request.status_code == 200 else []
        if not isinstance(messages, list) or not messages:
            break
        for message in messages:
            before = message["id"]
            if not system_message(message):
                continue
            while True:
                delete = requests.delete(
                    f"https://discord.com/api/v9/channels/{channel_id}/messages/{message['id']}",
                    headers={"Authorization": token},
                )
                if delete.status_code == 204:
                    print(
                        f"{timestamp()} » Deleted → {color('y')}[{color('g')}{message['id']}{color('y')}]"
                    )
                    time.sleep(delay)
                    break
                elif delete.status_code == 429:
                    time.sleep(1)
                else:
                    break


def search_clear(url):
    off = 0
    while True:
        request = requests.get(f"{url}&offset={off}", headers={"Authorization": token})
        groups = (
            request.json().get("messages", []) if request.status_code == 200 else []
        )
        if not groups:
            break
        found = False
        for group in groups:
            for message in group:
                if not system_message(message):
                    continue
                while True:
                    delete = requests.delete(
                        f"https://discord.com/api/v9/channels/{message['channel_id']}/messages/{message['id']}",
                        headers={"Authorization": token},
                    )
                    if delete.status_code == 204:
                        print(
                            f"{timestamp()} » Deleted → {color('y')}[{color('g')}{message['id']}{color('y')}]"
                        )
                        time.sleep(delay)
                        found = True
                        break
                    elif delete.status_code == 429:
                        time.sleep(1)
                    else:
                        break
        if not found:
            break
        off += 25


def clear_dm():
    print(logo)
    channels = [
        d
        for d in requests.get(
            "https://discord.com/api/v9/users/@me/channels",
            headers={"Authorization": token},
        ).json()
        if d.get("type") in (1, 3)
    ]
    random.shuffle(channels)
    for d in channels:
        channel_id = d["id"]
        name = (
            d.get("recipients", [{}])[0].get("username")
            if d["type"] == 1
            else d.get("name", "Unnamed Group")
        )
        print(
            f"{timestamp()} » Clearing → {color('y')}[{color('g')}{name}{color('y')}]"
        )
        listing_clear(channel_id, name)
    time.sleep(2)
    clear_cmd()
    main()


def listing_clear_chat():
    print(logo)
    channel_id = input(f"{timestamp()} » Channel ID → ").strip()
    clear_cmd()
    print(logo)
    listing_clear(channel_id)
    time.sleep(2)
    clear_cmd()
    main()


def search_clear_chat():
    print(logo)
    channel_id = input(f"{timestamp()} » Channel ID → ").strip()
    guild = (
        requests.get(
            f"https://discord.com/api/v9/channels/{channel_id}",
            headers={"Authorization": token},
        )
        .json()
        .get("guild_id")
    )
    url = f"https://discord.com/api/v9/{'guilds/' + guild if guild else 'channels/' + channel_id}/messages/search?author_id={user_id}"
    if guild:
        url += f"&channel_id={channel_id}"
    clear_cmd()
    print(logo)
    search_clear(url)
    time.sleep(2)
    clear_cmd()
    main()


def guild_clear():
    print(logo)
    guild_id = input(f"{timestamp()} » Guild ID → ").strip()
    clear_cmd()
    print(logo)
    search_clear(
        f"https://discord.com/api/v9/guilds/{guild_id}/messages/search?author_id={user_id}"
    )
    time.sleep(2)
    clear_cmd()
    main()


def main():
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
    {
        "1": clear_dm,
        "2": listing_clear_chat,
        "3": search_clear_chat,
        "4": guild_clear,
    }.get(ch, main)()


main()
