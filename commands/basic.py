from pyrogram import filters, enums
from core import app
from cfg import PREFIXES
import time
import os
from html import escape

@app.on_message(filters.me & filters.command("help", prefixes=PREFIXES))
async def help(client, message):

    text = """
<b>Все команды бота</b>

<code>help</code> - список команд
<code>ping</code> - пинг
<code>info</code> - информация пользователя
"""

    await message.edit(text, parse_mode = enums.ParseMode.HTML)

@app.on_message(filters.me & filters.command("ping", prefixes=PREFIXES))
async def ping(client, message):

    start = time.time()
    await message.edit("🏓 Считаю...")
    end = time.time()

    ping = round((end - start) * 1000)

    await message.edit(f"<b>🏓 ПОНГ \nВремя задержки: <code>{ping}</code> мс", parse_mode = enums.ParseMode.HTML)

@app.on_message(filters.me & filters.command("info", prefixes=PREFIXES))
async def info(client, message):

    reply = message.reply_to_message

    user = await client.get_me()

    if reply:
        user = reply.from_user

    user = await client.get_chat(user.id)

    username = f"@{user.username}" if user.username else "Нету"
    last_name = escape(user.last_name) if user.last_name else "Нету"
    bio = escape(user.bio) if user.bio else "Нету"
    first_name = escape(user.first_name) if user.first_name else "Нету"

    text = f"""
👤 Информация о <b>{first_name}</b>

Имя: <code>{first_name}</code>
Фамилия: <code>{last_name}</code>
Username: <code>{username}</code>
Id: <code>{user.id}</code>
Описание: <code>{bio}</code>
"""

    if user.photo:
        
        avatar = await client.download_media(user.photo.big_file_id, file_name=f"avatar_{user.id}.jpeg")

        try:
            await message.reply_photo(avatar, caption = text, parse_mode = enums.ParseMode.HTML)
            await message.delete()

        finally:
            if os.path.exists(avatar):
                os.remove(avatar)
                
    if not user.photo:
        await message.edit(text, parse_mode = enums.ParseMode.HTML)
