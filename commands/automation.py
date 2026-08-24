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

AFK = False
AFK_REPLY_SLEEP = 0
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

    global AFK, AFK_REPLY_SLEEP

    if not AFK:
        return

    if message.from_user and message.from_user.is_bot:
        return

    now = time.time()

    if now - AFK_REPLY_SLEEP < 15:
        return

    await message.reply(AFK_REASON, parse_mode = enums.ParseMode.HTML)

@app.on_message(filters.me & filters.command("unafk", prefixes = PREFIXES))
async def unafk(client, message):

    global AFK

    if not AFK:
        return await message.edit("АФК не был включен")
    
    AFK = False
    
    await message.edit("АФК Выключен")
