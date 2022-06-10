import builtins
import io
import os
from typing import Optional, TypedDict

import yaml
from chatexchange.client import Client
from chatexchange.events import UserMentioned
from chatexchange.messages import Message
from chatexchange.rooms import Room
from chatexchange.users import User


class Credentials(TypedDict):
    api_key: str
    email: str
    password: str


class Modes(TypedDict):
    debug: Optional[bool]
    verbose: Optional[bool]


class Config(TypedDict):
    credentials: Credentials
    host: Optional[str]
    modes: Modes
    room_id: Optional[int]


def log_recursive(obj: dict, level=0):
    """
    Recursively logs an object
    """

    for key, val in obj.items():
        match type(val):
            case builtins.dict:
                print(f"\"{key}\"")
                log_recursive(val, level + 1)
            case _:
                print(f"{level * 4 * ' '}\"{key}\" -> \"{val}\"")


def load_config(config_path: str) -> Config:
    """
    Load Bot configuration
    """

    try:
        with io.open(config_path, "r", encoding="utf-8") as stream:
            config: Config = yaml.safe_load(stream)

            print("[config]")
            log_recursive(config)
            print()

            return config
    except FileNotFoundError:
        print(f"[fatal] missing configuration ({config_path})")


def validate_config(config: Config) -> bool:
    return all(list(config["credentials"].values()))


def handle_message(message: Message, client: Client) -> None:
    """
    Room message event handler
    """

    if not isinstance(message, UserMentioned):
        # ignoring everything except replies
        return

    me: User = client.get_me()

    replied_to_id = message.target_user_id

    if replied_to_id != me.id:
        # ignoring everything except replies to bot
        return

    content: str = message.content

    print(content)


def main():
    """
    Bot startup
    """

    config = load_config("./config.yml")

    if validate_config(config) is False:
        print("[fatal] missing required config")
        return

    credentials = config["credentials"]
    modes = config["modes"]
    debug = modes["debug"] is True

    try:
        host = config["host"] or "stackoverflow.com"
        email = credentials["email"]
        pwd = credentials["password"]
        room_id = config["room_id"] or 244740

        client = Client(host)
        client.login(email, pwd)
        me: User = client.get_me()
        print(f"logged in as {me.name}")

        room: Room = client.get_room(room_id)
        room.join()
        print(f"joined room {room_id} ({host})")

        room.watch_socket(handle_message)

        if debug:
            room.send_message(f"[{me.name}] reporting for duty")

        while True:
            pass

    except KeyboardInterrupt:
        os._exit(0)

    except Exception as e:
        print(f"[fatal] failed to log in\n{e}")


if __name__ == '__main__':
    main()
