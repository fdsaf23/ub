from pyrogram import filters, enums
from pyrogram.raw.types import UpdateDeleteMessages, UpdateDeleteChannelMessages
import asyncio
from core import app
from cfg import PREFIXES
import os

muted_users = set()
group_save_id = 1891318329
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

@app.on_message(filters.private & filters.incoming, group=4)
async def save_msg(client, message):
    chat_id = message.chat.id

    # Не сохраняем сообщения из самой группы-архива
    if chat_id == group_save_id:
        return

    if not message.from_user or message.from_user.is_self:
        return

    key = f"{chat_id}:{message.id}"

    data = {
        "chat_id": chat_id,
        "message_id": message.id,
        "text": message.text or message.caption or "",
        "user_id": message.from_user.id,
        "name": message.from_user.first_name or "Пользователь",
        "media": None,
        "media_type": None
    }

    if message.media:
        try:
            os.makedirs("archive_media", exist_ok=True)

            file_path = await message.download(
                f"archive_media/{chat_id}_{message.id}"
            )

            data["media"] = file_path

            if message.photo:
                data["media_type"] = "photo"
            else:
                data["media_type"] = "document"

        except Exception as error:
            print(f"Ошибка скачивания медиа: {error}")

    msg_cache[key] = data


@app.on_raw_update()
async def deleted_msg(client, update, users, chats):
    if not isinstance(update, UpdateDeleteMessages):
        return

    deleted_ids = update.messages

    for key, data in list(msg_cache.items()):
        if data["message_id"] not in deleted_ids:
            continue

        name = html.escape(data["name"])
        text = html.escape(data["text"] or "Без текста")

        header = (
            f"🗑 Сообщение удалено от "
            f'<a href="tg://user?id={data["user_id"]}">{name}</a>'
        )

        try:
            media_path = data["media"]

            # Если было медиа — сначала отправляем файл
            if media_path and os.path.exists(media_path):
                if data["media_type"] == "photo":
                    await client.send_photo(
                        chat_id=group_save_id,
                        photo=media_path,
                        caption=header,
                        parse_mode=enums.ParseMode.HTML
                    )
                else:
                    await client.send_document(
                        chat_id=group_save_id,
                        document=media_path,
                        caption=header,
                        parse_mode=enums.ParseMode.HTML
                    )

                # Текст/подпись медиа — отдельным сообщением
                if data["text"]:
                    await client.send_message(
                        chat_id=group_save_id,
                        text=f"📋 Содержимое:\n<i>{text[:3900]}</i>",
                        parse_mode=enums.ParseMode.HTML
                    )

            # Обычное текстовое сообщение
            else:
                await client.send_message(
                    chat_id=group_save_id,
                    text=f"{header}\n\n📋 Содержимое:\n<i>{text[:3900]}</i>",
                    parse_mode=enums.ParseMode.HTML
                )

        except Exception as error:
            print(f"Ошибка отправки в архив: {error}")

        finally:
            msg_cache.pop(key, None)

  









  


