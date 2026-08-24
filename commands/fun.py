import os
import asyncio
from io import BytesIO
from datetime import datetime
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pyrogram import filters, enums

from core import app
from cfg import PREFIXES

font_name = ImageFont.truetype("fonts/FredokaOneCyrillic-Regular.ttf", 50)
font_text = ImageFont.truetype("fonts/FredokaOneCyrillic-Regular.ttf", 65)
font_id = ImageFont.truetype("fonts/FredokaOneCyrillic-Regular.ttf", 40)
font_time = ImageFont.truetype("fonts/FredokaOneCyrillic-Regular.ttf", 25)

@app.on_message(filters.me & filters.command("quote", prefixes = PREFIXES))
async def quote(client, message):

  reply = message.reply_to_message

  if not reply or not reply.from_user:
    return await message.edit("❌ Используй реплеем")

  user = reply.from_user
  text = textwrap.fill(reply.text, width = 50)

  if user.photo:
    avatar = await client.download_media(user.photo.big_file_id, file_name = f"bg.jpeg")
    await message.edit("🖼 Загружаю аватар...")
  else:
    return await message.edit("У пользователя нету аватарки")

  raw_img = Image.open(avatar).convert("RGBA")

  bg = raw_img.resize((1280, 720))
  bg = bg.filter(ImageFilter.BoxBlur(radius = 15))
  bg = bg.convert("RGBA")

  overlay = Image.new("RGBA", bg.size, (0, 0, 0, 160))

  bg = Image.alpha_composite(bg, overlay)

  draw = ImageDraw.Draw(bg)

  draw.text((640, 300), f"{user.first_name}", font=font_name, anchor="mm", fill = "white")
  draw.text((640, 360), text, font = font_text, anchor="mm", fill = "white")
  draw.text((640, 420), f"{user.id}", font = font_id, anchor = "mm", fill = "white")
  
  final_buffer = BytesIO()
  bg.convert("RGB").save(final_buffer, "JPEG", quality=85)
  final_buffer.seek(0)

  final_buffer.name = "quote.jpeg"

  await client.send_photo(message.chat.id, photo=final_buffer)

  await message.delete()
