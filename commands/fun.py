from io import BytesIO

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pyrogram import filters

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

    avatar_path = await client.download_media(
        user.photo.big_file_id,
        file_name="bg.jpeg"
    )

    raw_img = Image.open(avatar_path).convert("RGBA")

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

    # Левая граница всего текста
    text_x = 430
    id_y = 210
    message_y = 275

    # ID сверху
    draw.text(
        (text_x, id_y),
        f"ID: {user.id}",
        font=font_id,
        fill="white",
        anchor="la"
    )

    # Перенос текста по ширине
    max_width = 730
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

    # Текст сообщения
    draw.multiline_text(
        (text_x, message_y),
        text,
        font=font_text,
        fill="white",
        anchor="la",
        align="left",
        spacing=5
    )

    # Высота текста — чтобы username был сразу под сообщением
    text_bbox = draw.multiline_textbbox(
        (text_x, message_y),
        text,
        font=font_text,
        spacing=5
    )

    username_y = text_bbox[3] + 15

    if user.username:
        draw.text(
            (text_x, username_y),
            f"@{user.username}",
            font=font_username,
            fill=(210, 210, 210),
            anchor="la"
        )

    final_buffer = BytesIO()
    bg.convert("RGB").save(final_buffer, "JPEG", quality=85)
    final_buffer.seek(0)
    final_buffer.name = "quote.jpeg"

    await client.send_photo(
        message.chat.id,
        photo=final_buffer
    )

    await message.delete()
