from pyrogram import filters, enums
from core import app
from cfg import PREFIXES
import time
import emoji

replies = {}
react = {}

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

    if len(message.command) < 2:
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
        return await message.edit(
            "❌ На пользователе нет автореплея"
    )

    del replies[user_id]

    await message.edit(f"✅ Автоответ с <b>{reply.from_user.first_name}</b> cнят", parse_mode = enums.ParseMode.HTML)

@app.on_message(filters.me & filters.command("replies", prefixes=PREFIXES))
async def replies_array(client, message):

    if not replies:
        return await message.edit("📋 Cписок пуст")

    text = "📋 Список автоответов:\n"

    for number, user_id in enumerate(replies, 1):

        user = await client.get_users(user_id)

        name = user.first_name

        text += f"{number}. <code>{name}</code> → <code>{replies[user_id]}</code>"

    await message.edit(text, parse_mode = enums.ParseMode.HTML)

@app.on_message(filters.me & filters.command("areact", prefixes = PREFIXES))
async def add_react(client, message):

    reply = message.reply_to_message

    if not reply or not reply.from_user:
        return await message.edit("❌ Используй ответом на сообщение пользователя")

    if len(message.command) < 2:
        return await message.edit("❌ Использование: .areact emoji")

    user_id = reply.from_user.id

    reaction = message.text.split(maxsplit=1)[1].strip()

    if len(emoji.emoji_list(reaction)) > 1:
        return await message.edit(
            "❌ Используй одно эмодзи, например 😂"
        )
    
    react[user_id] = reaction

    await message.edit(f"✅ Автореакция добавлена \n\nТаргет: <code>{reply.from_user.first_name}</code>\nРеакция: {reaction}")

@app.on_message(filters.me & filters.command("dreact", prefixes = PREFIXES))
async def dreact(client, message):
    reply = message.reply_to_message

    if not reply or not reply.from_user:
        return await message.edit("❌ Используй ответом на сообщение пользователя")

    user_id = reply.from_user.id

    if user_id not in react:
        return await message.edit("❌ Автореакции на пользователя не найдена")

    del react[user_id]

    await message.edit(f"✅ Автореакция на <b>{reply.from_user.first_name}</b> удалена", parse_mode = enums.ParseMode.HTML)

@app.on_message(filters.me & filters.command("lreact", prefixes = PREFIXES))
async def list_react(client, message):

    if not react:
        return message.edit("📋 Список пуст")

    text = "📋 Список автореакций:\n"

    for num, user_id in enumerate(react, 1):
        user = await client.get_users(user_id)

        name = user.first_name

        text += f"{num}. <code>{name}</code> → <code>{react[user_id]}</code>"

    await message.edit(text, parse_mode = enums.ParseMode.HTML)

@app.on_message(~filters.me & filters.incoming)
async def incoming_handler(client, message):

    if not message.from_user:
        return

    if message.from_user.is_bot:
        return

    user_id = message.from_user.id

    # =========================
    # AFK
    # =========================

    global AFK, REPLY_SLEEP

    if AFK and message.chat.type == enums.ChatType.PRIVATE:

        now = time.time()

        if now - REPLY_SLEEP >= 15:

            await message.reply(
                AFK_REASON,
                parse_mode=enums.ParseMode.HTML
            )

            REPLY_SLEEP = now

    # =========================
    # AUTOREPLY
    # =========================

    if user_id in replies:

        await app.send_message(
            chat_id=message.chat.id,
            text=replies[user_id],
            reply_to_message_id=message.id
    )

    # =========================
    # AUTOREACT
    # =========================

    if user_id in react:
        await message.react(react[user_id])
