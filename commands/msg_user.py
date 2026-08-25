from pyrogram import filters, enums
from pyrogram.errors import FloodWait
import asyncio
from core import app
from cfg import PREFIXES

muted_users = set()

@app.on_message(filters.me & filters.private & filters.command("mute", prefixes = PREFIXES))
async def mute(client, message):
  chat_id = message.chat.id
  if chat_id in muted_users:
    return await message.edit("❌ Пользователь уже замьючен")

  muted_users.add(chat_id)

  chat = await client.get_chat(chat_id)
  name = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>" if chat.username else f"<a href='tg://user?id={chat_id}'>{chat.first_name}</a>"

  text = f"""
🔇 {name} был замьючен навсегда ❗
Для снятия используй: <code>.unmute</code> в этом чате
  """
  await message.edit(text)

@app.on_message(filters.me & filters.private & filters.command("unmute", prefixes = PREFIXES))
async def unmute(client, message):
  chat_id = message.chat.id
  if chat_id not in muted_users:
    return await message.edit("❌ Пользователь не замьючен")

  muted_users.remove(chat_id)

  chat = await client.get_chat(chat_id)
  name = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>" if chat.username else f"<a href='tg://user?id={chat_id}'>{chat.first_name}</a>"

  text = f"""
📣 {name} был разьючен ❗
  """
  await message.edit(text)

@app.on_message(filters.private & filters.incoming, group = 3)
async def del_msg(client, message):
  chat_id = message.chat.id
  if chat_id not in muted_users:
    return

  try:
    await message.delete()
  except Exception as e:
    await message.reply(e)




