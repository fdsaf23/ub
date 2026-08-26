from pyrogram import filters, enums
from pyrogram.raw.types import UpdateDeleteMessages, UpdateDeleteChannelMessages
import asyncio
from core import app
from cfg import PREFIXES
import os

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
  await message.edit(text, disable_web_page_preview=True)

@app.on_message(filters.me & filters.private & filters.command("unmute", prefixes = PREFIXES))
async def unmute(client, message):
  chat_id = message.chat.id
  if chat_id not in muted_users:
    return await message.edit("❌ Пользователь не замьючен")

  muted_users.remove(chat_id)

  chat = await client.get_chat(chat_id)
  name = f"<a href='https://t.me/{chat.username}'>{chat.first_name}</a>" if chat.username else f"<a href='tg://user?id={chat_id}'>{chat.first_name}</a>"

  text = f"""
📣 {name} был размьючен ❗
  """
  await message.edit(text, disable_web_page_preview=True)

@app.on_message(filters.private & filters.incoming, group = 3)
async def del_msg(client, message):
  chat_id = message.chat.id
  if chat_id not in muted_users:
    return

  try:
    await message.delete()
  except Exception as e:
    await message.reply(e)

@app.on_message(filters.command(["hug", "slap", "kiss", "pat", "bite", "poke", "wave", "hit", "fuck", "kick"]), prefixes = PREFIXES)
async def interaction_cmd(client, message):

  text = message.command[0].lower()

  if text.lower() == "hug":
    await client.send_message(chat_id=message.chat_id, text="ты обнял его", reply_to_message_id=message.id)




    



