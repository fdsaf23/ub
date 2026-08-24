from pyrogram import filters, enums
from core import app
from cfg import PREFIXES
import time

# .afk — включить AFK
# .unafk — выключить AFK
# .autoreply — автоответчик
# .delreply — удалить автоответ
# .replies — список автоответов
# .autoreact — авто-реакции

replies = {}

AFK = False
REPLY_SLEEP = 0
AFK_REASON = "<b>👋 Привет, я автоответчик! \n-------------------\n<i>Жди ответа в течении 2-5 часов если я не в сети, если ответа нет - пиши в @feedbackZLX_bot</i> \n-------------------\nОт спама в лс смысла нет ведь уведомления выключены</b>"

@app.on_message(filters.me & filters.command("afk", prefixes=PREFIXES))
async def afk(client, message):

    global AFK

    if AFK:
        return await message.edit("АФК уже включен")

    AFK = True

    await message.edit("💤 АФК включен")

@app.on_message(~filters.me & filters.private & filters.incoming)
async def afk_reply(client, message):

    global AFK, REPLY_SLEEP

    if not AFK:
        return

    if message.from_user and message.from_user.is_bot:
        return

    now = time.time()

    if now - REPLY_SLEEP < 15:
        return

    await message.reply(AFK_REASON, parse_mode = enums.ParseMode.HTML)

    REPLY_SLEEP = now

@app.on_message(filters.me & filters.command("unafk", prefixes = PREFIXES))
async def unafk(client, message):

    global AFK

    if not AFK:
        return await message.edit("АФК не был включен")
    
    AFK = False
    
    await message.edit("АФК Выключен")

@app.on_message(filters.me & filters.command("areply", prefixes=PREFIXES))
async def areply(client, message):

    reply = message.reply_to_message

    if not reply or not reply.from_user:
        return await message.edit("❌ Используй ответом на сообщение пользователя")

    if len(message.text) < 2:
        return await message.edit("❌ Использование: .areply text")

    user_id = reply.from_user.id
    text = message.text.split(maxsplit=1)[1].strip()

    replies[user_id] = text

    await message.edit(f"<b>✅ Автоответ запущен \n\nТаргет: <code>{reply.from_user.first_name}</code>\nТекст: <code>{text}</code></b>", parse_mode = enums.ParseMode.HTML)

@app.on_message(filters.me & filters.command("dreply", prefixes=PREFIXES))
async def dreply(client, message):

    reply = message.reply_to_message
    
    if not reply or not reply.from_user:
        return await message.edit("❌ Используй ответом на сообщение пользователя")

    user_id = reply.from_user.id

    if user_id not in replies:
        return await message.edit("❌ На пользователе нет автореплея")

    del replies[user_id]

    await message.edit(f"✅ Автоответ с <b>{reply.from_user.first_name}</b> cнят", parse_mode = enums.ParseMode.HTML)

@app.on_message(filters.me & filters.command("replies", prefixes=PREFIXES))
async def replies(client, message):

    if not replies:
        return await message.edit("📋 Cписок пуст.")

    text = "📋 Список автоответов:\n\n"

    for number, user_id in enumerate(replies, 1):

        user = await client.get_users(user_id)

        name = user.first_name

        text += f"""
{number}. <code>{name}</code> → <code>{replies[user_id]}</code>
"""

    await message.edit(text, parse_mode = enums.ParseMode.HTML)

@app.on_message(~filters.me & filters.incoming)
async def reply(client, message):

    if not message.from_user:
        return

    user_id = message.from_user.id

    if user_id not in replies:
        return

    now = time.time()

    if now - REPLY_SLEEP < 15:
        return

    await client.send_message(
        chat = message.chat.id,
        text = replies[user_id],
        reply_to_message_id = message.id
    )

    REPLY_SLEEP = now
