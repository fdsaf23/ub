"""Local userbot configuration read from environment variables."""

import os

from dotenv import load_dotenv


load_dotenv()


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing {name}. Copy .env.example to .env and fill in its values."
        )
    return value


API_ID = int(required_env("API_ID"))
API_HASH = required_env("API_HASH")
# The generator script creates this value, so it must not be required while
# importing the configuration.
STRING_SESSION = os.getenv("STRING_SESSION")

PREFIXES = [".", "/"]
