from io import BytesIO

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pyrogram import filters

import asyncio

from core import app
from cfg import PREFIXES


font_text = ImageFont.truetype(
    "fonts/FredokaOneCyrillic-Regular.ttf", 48
)
font_id = ImageFont.truetype(
    "fonts/FredokaOneCyrillic-Regular.ttf", 40
)
font_username = ImageFont.truetype(
    "fonts/FredokaOneCyrillic-Regular.ttf", 30
)


@app.on_message(filters.me & filters.command("quote", prefixes=PREFIXES))
async def quote(client, message):
    reply = message.reply_to_message

    if not reply or not reply.from_user:
        return await message.edit("❌ Используй команду реплеем на сообщение")

    user = reply.from_user
    message_text = reply.text or reply.caption or ""

    if not message_text:
        return await message.edit("❌ В сообщении нет текста")

    if not user.photo:
        return await message.edit("❌ У пользователя нет аватарки")

    await message.edit("🖼 Загружаю аватар...")
    await asyncio.sleep(0.4)

    avatar_path = await client.download_media(
        user.photo.big_file_id,
        file_name="bg.jpeg"
    )

    await message.edit("🎨 Cоздаю фон...")
    await asyncio.sleep(0.4)

    raw_img = Image.open(avatar_path).convert("RGBA")

    # Фон
    bg = raw_img.resize((1280, 720))
    bg = bg.filter(ImageFilter.BoxBlur(radius=15))

    overlay = Image.new("RGBA", bg.size, (0, 0, 0, 165))
    bg = Image.alpha_composite(bg.convert("RGBA"), overlay)

    draw = ImageDraw.Draw(bg)

    # Аватарка
    avatar_size = 260
    avatar_img = raw_img.resize((avatar_size, avatar_size))

    mask = Image.new("L", (avatar_size, avatar_size), 0)
    mask_draw = ImageDraw.Draw(mask)

    mask_draw.rounded_rectangle(
        (0, 0, avatar_size, avatar_size),
        radius=40,
        fill=255
    )

    avatar_img.putalpha(mask)

    avatar_x = 100
    avatar_y = (720 - avatar_size) // 2

    bg.alpha_composite(avatar_img, (avatar_x, avatar_y))

    # Общая левая граница текста
    text_x = avatar_x + avatar_size + 70

    # ID — на уровне верхнего края аватарки
    draw.text(
        (text_x, avatar_y),
        f"ID: {user.id}",
        font=font_id,
        fill="white",
    )

    # Username — на уровне нижнего края аватарки
    username_text = f"@{user.username}" if user.username else user.first_name

    draw.text(
        (text_x, avatar_y + avatar_size),
        username_text,
        font=font_username,
        fill=(210, 210, 210),
    )

    # Перенос сообщения по словам
    max_width = 700
    lines = []
    current_line = ""

    for word in message_text.split():
        test_line = f"{current_line} {word}".strip()

        bbox = draw.textbbox((0, 0), test_line, font=font_text)
        line_width = bbox[2] - bbox[0]

        if line_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    text = "\n".join(lines)

    # Вычисляем высоту сообщения
    text_bbox = draw.multiline_textbbox(
        (0, 0),
        text,
        font=font_text,
        spacing=8
    )

    text_height = text_bbox[3] - text_bbox[1]

    # Границы свободной области между ID и username
    id_bottom = avatar_y + 55
    username_top = avatar_y + avatar_size - 45

    # Сообщение центрируется между ними
    message_y = id_bottom + (username_top - id_bottom - text_height) // 2

    draw.multiline_text(
        (text_x, message_y),
        text,
        font=font_text,
        fill="white",
        align="left",
        spacing=8
    )

    await message.edit("✨ Добавляю текст...")
    await asyncio.sleep(0.4)

    await message.edit("📤 Отправляю...")
    await asyncio.sleep(0.4)

    final_buffer = BytesIO()
    bg.convert("RGB").save(final_buffer, "JPEG", quality=85)
    final_buffer.seek(0)
    final_buffer.name = "quote.jpeg"

    await message.reply_photo(
        photo=final_buffer
    )

    await message.delete()

@app.on_message(filters.me & filters.command("spam", prefixes=PREFIXES))
async def spam(client, message):
    args = message.text.split(maxsplit=3)

    if len(args) < 3:
        return await message.edit("❌ Используй: spam count text")
        
    try:
        count = int(args[1])
    except:
        return await message.edit("❌ Введи кол-во сообщений")

    if count < 1:
        return await message.edit("Выбери число больше 0")

    text = " ".join(args[2:])

    await message.delete()

    for _ in range(count):
        await client.send_message(message.chat.id, text)
        await asyncio.sleep(0.3)

@app.on_message(filters.me & filters.command("onda", prefixes=PREFIXES))
async def onda(client, message):

    steps = [
        "#2",
        "#20",
        "#201",
        "#2016"
    ]

    for step in steps:
        await message.edit(step)
        await asyncio.sleep(0.4)
        






