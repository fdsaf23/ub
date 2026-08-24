import os
import asyncio
from io import BytesIO
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pyrogram import filters, enums

from core import app
from cfg import PREFIXES

font = "fonts/FredokaOneCyrillic-Regular.ttf"

@app.on_message(filters.me & filters.command("quote", prefixes = PREFIXES))
async def quote(client, message):

  reply = message.reply_to_message

  if not reply and not reply.from_user:
    return await message.edit("❌ Используй реплеем")

  user = reply.from_user
  text = textwrap.fill(target.text, width = 50)

  if user.photo:
    avatar = await client.download_media()
