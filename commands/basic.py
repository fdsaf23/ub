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
<code>cinfo</code> - инфомация о чате
<code>set</code> - изменить параметр профиля
<code>backup</code> - бэкап профиля
<code>restore</code> - вернуть профиль бэкапа
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

    if reply:
        user = reply.from_user

    user = await client.get_me()

    user = await client.get_users(user.id)

    username = f"@{user.username}" if user.username else "Нету"
    last_name = escape(user.last_name) if user.last_name else "Нету"
    bio = escape(user.bio) if user.bio else "Нету"
    first_name = escape(user.fist_name) if user.first_name else "Нету"

    text = f"""
👤 Информация о <b>{first_name}</b>

Имя: <code>{first_name}</code>
Фамилия: <code>{last_name}</code>
Username: {username}
Id: <code>{user.id}</code>
Описание: <code>{bio}</code>
"""

    if user.photo:
        avatar = await client.download_media(user.photo.big_file_id, file_name=f"avatar_{user.id}.jpg")

        try:
            await message.reply_photo(avatar, caption = text, parse_mode = enums.ParseMode.HTML)

        finally:
            if os.path.exists(avatar):
                os.remove(avatar)

    await message.edit(text, parse_mode = enums.ParseMode.HTML)

@app.on_message(filters.me & filters.command("cinfo", prefixes=PREFIXES))
async def chatinfo(client, message):

    chat = await client.get_chat(message.chat.id)

    username = f"https://t.me/{chat.username}" if chat.username else "Нету"

    text = f"""
ℹ Информация о <b>{chat.title}</b>

Название: <code>{chat.title}</code>
Ссылка: {username}
Id: <code>{message.chat.id}</code>
Кол-во участников: <code>{chat.members_count}</code>
"""

    if chat.photo:

        avatar = await client.download_media(chat.photo.big_file_id, file_name = f"chatavatar_{chat.id}.jpeg")

        try:
            await message.reply_photo(avatar, caption = text, parse_mode = enums.ParseMode.HTML)

            await message.delete()

        finally:

            if os.path.exists(avatar):
                os.remove(avatar)

    if not chat.photo:
        await message.edit(text)

@app.on_message(filters.me & filters.command("set", prefixes=PREFIXES))
async def set(client, message):

    args = message.text.split(maxsplit = 2)

    if len(args) < 3:
        return await message.edit("Используй: .set name|user|bio значение")
    
    field = args[1].lower()
    value = args[2].strip()

    try:
        if field == "name":
            await client.update_profile(first_name=value)
            return await message.edit(f"Имя изменено на <b>{value}</b>", parse_mode = enums.ParseMode.HTML)
        
        elif field == "user":
            await client.update_profile(username = value)
            return await message.edit(f"Юзернейм изменен на <b>{value}</b>", parse_mode = enums.ParseMode.HTML)
        
        elif field == "bio":
            await client.update_profile(bio=value)
            return await message.edit(f"Описание изменено на <b>{value}</b>", parse_mode = enums.ParseMode.HTML)

        else:
            await message.edit("Используй: name OR user OR bio")

    except Exception as e:
        return await message.edit(f"{e}")
