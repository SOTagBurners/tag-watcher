import builtins
import io
from typing import Optional, TypedDict

import chatexchange
import yaml


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

def main():
    """
    Bot startup
    """

    config = load_config("./config.yml")

    if validate_config(config) is False:
        print("[fatal] missing required config")
        return

    try:
        host = config["host"] or "stackoverflow.com"
        email = config["credentials"]["email"]
        pwd = config["credentials"]["password"]

        client = chatexchange.Client(host)
        client.login(email, pwd)
    except Exception as e:
        print(f"[fatal] failed to log in\n{e}")

if __name__ == '__main__':
    main()
