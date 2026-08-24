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
AFK_REASON = "👋 Привет, я автоответчик! \nЖди ответа в течении 2-5 часов если я не в сети, если ответа нет - пиши в @feedbackZLX_bot \nОт спама в лс смысла нет ведь уведомления выключены"

@app.on_message(filters.me & filters.command("afk", prefixes=PREFIXES))
async def afk(client, message):

    global AFK, AFK_REASON

    if AFK:
        return await message.edit("АФК уже включен")

    AFK = True

    await message.edit("💤 АФК включен")

@app.on_message(~filters.me & filters.private & filters.incoming)
async def afk_reply(client, message):

    global AFK

    if not AFK:
        return

    if message.from_user and message.from_user.is_bot:
        return

    if AFK:
        time.sleep(15)
        await message.reply(AFK_REASON)
