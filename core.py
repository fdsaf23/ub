from pyrogram import Client

from cfg import API_HASH, API_ID, STRING_SESSION, required_env


app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION or required_env("STRING_SESSION"),
)
