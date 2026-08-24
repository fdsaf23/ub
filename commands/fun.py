import os
import asyncio
from io import BytesIO
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pyrogram import filters, enums

from core import app
from cfg import PREFIXES


W, H = 1200, 675


def font(size, bold=False):
    path = (
        "C:/Windows/Fonts/arialbd.ttf"
        if bold else
        "C:/Windows/Fonts/arial.ttf"
    )

    if os.path.exists(path):
        return ImageFont.truetype(path, size)

    return ImageFont.load_default()


def round_avatar(img, size=230):
    img = img.convert("RGBA")
    img.thumbnail((size, size))

    result = Image.new("RGBA", (size, size))
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    result.paste(img, (x, y))

    mask = Image.new("L", (size, size))
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, size, size),
        radius=35,
        fill=255
    )

    result.putalpha(mask)
    return result


def wrap(draw, text, font_obj, width):
    words = text.split()
    lines, line = [], ""

    for word in words:
        test = f"{line} {word}".strip()

        if draw.textlength(test, font=font_obj) <= width:
            line = test
        else:
            lines.append(line)
            line = word

    if line:
        lines.append(line)

    return lines


@app.on_message(filters.me & filters.command("quote", prefixes=PREFIXES))
async def quote(client, message):

    reply = message.reply_to_message

    if not reply or not reply.from_user:
        return await message.edit(
            "❌ Ответь на сообщение пользователя"
        )

    user = reply.from_user

    await message.edit("📥 Получаю данные...")
    await asyncio.sleep(0.3)

    try:
        # Аватарка
        await message.edit("🖼 Загружаю аватар...")

        if user.photo:
            photo = await client.download_media(
                user.photo.big_file_id,
                in_memory=True
            )
            avatar = Image.open(
                BytesIO(photo.getvalue())
            ).convert("RGB")
        else:
            avatar = Image.new("RGB", (500, 500), (40, 40, 40))

        await asyncio.sleep(0.3)

        # Фон
        await message.edit("🎨 Создаю фон...")

        bg = avatar.resize((W, H)).filter(
            ImageFilter.GaussianBlur(35)
        ).convert("RGBA")

        # Средний цвет аватарки
        color = avatar.resize((1, 1)).getpixel((0, 0))

        # Градиент слева
        gradient = Image.new("RGBA", (W, H))

        for x in range(W):
            alpha = int(180 * (1 - x / W))

            for y in range(H):
                gradient.putpixel(
                    (x, y),
                    (*color, alpha)
                )

        bg.alpha_composite(gradient)

        # Затемнение
        bg.alpha_composite(
            Image.new(
                "RGBA",
                (W, H),
                (0, 0, 0, 100)
            )
        )

        await asyncio.sleep(0.3)

        # Карточка
        await message.edit("✨ Создаю quote...")

        draw = ImageDraw.Draw(bg)

        name_font = font(45, True)
        text_font = font(32)
        small_font = font(22)

        # Аватарка
        ava = round_avatar(avatar)

        bg.alpha_composite(
            ava,
            (110, (H - 230) // 2)
        )

        # Имя
        name = user.first_name or "Unknown"

        if user.last_name:
            name += f" {user.last_name}"

        x = 390

        draw.text(
            (x, 160),
            name,
            font=name_font,
            fill="white"
        )

        # Текст
        text = reply.text or reply.caption or "Без текста"

        lines = wrap(
            draw,
            text,
            text_font,
            700
        )[:5]

        y = 240

        for line in lines:
            draw.text(
                (x, y),
                line,
                font=text_font,
                fill=(230, 230, 230)
            )
            y += 45

        # ID
        draw.text(
            (x, H - 110),
            f"ID: {user.id}",
            font=small_font,
            fill=(180, 180, 180)
        )

        # Время
        current_time = datetime.now().strftime("%H:%M")

        time_width = draw.textlength(
            current_time,
            font=small_font
        )

        draw.text(
            (W - time_width - 60, H - 70),
            current_time,
            font=small_font,
            fill="white"
        )

        # Сохраняем
        os.makedirs("temp", exist_ok=True)

        path = f"temp/quote_{user.id}.jpg"

        bg.convert("RGB").save(path, quality=95)

        await message.edit("📤 Отправляю...")

        await message.reply_photo(path)

        await message.delete()

        os.remove(path)

    except Exception as e:

        await message.edit(
            f"❌ Ошибка: <code>{e}</code>",
            parse_mode=enums.ParseMode.HTML
        )
