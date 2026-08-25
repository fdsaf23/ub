from pyrogram import filters, enums
from pyrogram.raw.types import UpdateDeleteMessages, UpdateDeleteChannelMessages
import asyncio
from core import app
from cfg import PREFIXES
import os

muted_users = set()
group_save_id = -5596420347
msg_cache = {}

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
📣 {name} был разьючен ❗
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

@app.on_message(filters.private & filters.incoming, group = 4)
async def save_msg(client, message):

  chat_id = message.chat.id

  if chat_id == group_save_id:
    return

  if message.from_user or message.from_user.is_self:
    return

  key = f"{chat_id}:{message.id}"

  data = {
    "chat_id": chat_id,
    "message_id": message.id,
    "text": message.text or message.caption or "",
    "user_id": message.from_user.id,
    "name": message.from_user.first_name,
    "media": None
  }
  
  if message.media:
    try:
      os.makedirs("archive_media", exists_ok=True)

      file_path = await message.download(f"archive_media/{chat_id}_{message.id}")

      data["media"] = file_path
      
    except Exception as e:
      print(e)

  msg_cache[key] = data

@app.on_raw_update()
async def delected_msg(client, update, users, chats):
  if not isinstance(update, UpdateDeleteMessage):
    return

  delete_ids = update.messages

  for key, data in list(msg_cache.items()):

    if data["message_id"] not in delete_ids:
      continue

    name = data['name']
    user_id = data['user_id']
    text = data['text']

    caption = f"""
🗑 Сообщение было удалено от <b><a href='tg://user?id={user_id}'>{name}</a></b>

📋 Содержимое:
<b><i>{text}</i></b>
"""

  try:
    if (data['media'] and os.path.exists(data['media'])):
      return await client.send_photo(chat_id=group_save_id, photo=data['media'], caption=caption)
    else:
      await client.send_message(chat_id=group_save_id, text=caption)

  except Exception as e:
    print(e)

  del msg_cache[key]

  









  


