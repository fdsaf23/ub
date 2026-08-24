import os
import textwrap
from datetime import datetime
from io import BytesIO
import PIL
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageStat

from pyrogram import filters
from pyrogram.enums import ParseMode

from core import app
from cfg import PREFIXES


WIDTH = 1200
HEIGHT = 675

OUTPUT_DIR = "temp"


def get_font(size, bold=False):
    fonts = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]

    for font_path in fonts:
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)

    return ImageFont.load_default()


def rounded_image(image, size, radius):
    image = image.convert("RGBA")
    image.thumbnail(size)

    avatar = Image.new("RGBA", size, (0, 0, 0, 0))

    x = (size[0] - image.width) // 2
    y = (size[1] - image.height) // 2

    avatar.paste(image, (x, y))

    mask = Image.new("L", size, 0)
    mask_draw = ImageDraw.Draw(mask)

    mask_draw.rounded_rectangle(
        (0, 0, size[0], size[1]),
        radius=radius,
        fill=255
    )

    avatar.putalpha(mask)

    return avatar


def get_average_color(image):
    image = image.convert("RGB")
    image = image.resize((1, 1))

    return image.getpixel((0, 0))


def draw_gradient(background, color):
    gradient = Image.new("RGBA", (WIDTH, HEIGHT))

    pixels = gradient.load()

    r, g, b = color

    for x in range(WIDTH):
        progress = x / WIDTH

        alpha = int(210 * (1 - progress))

        for y in range(HEIGHT):
            pixels[x, y] = (r, g, b, alpha)

    background.alpha_composite(gradient)


def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:

        test_line = (
            f"{current_line} {word}".strip()
        )

        bbox = draw.textbbox(
            (0, 0),
            test_line,
            font=font
        )

        line_width = bbox[2] - bbox[0]

        if line_width <= max_width:
            current_line = test_line
        else:

            if current_line:
                lines.append(current_line)

            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


async def create_quote(client, reply):

    user = reply.from_user

    # -------------------------
    # АВАТАРКА
    # -------------------------

    avatar = None

    try:
        avatar_file = await client.download_media(
            user.photo.big_file_id,
            in_memory=True
        )

        avatar = Image.open(
            BytesIO(avatar_file.getvalue())
        ).convert("RGB")

    except Exception:
        avatar = Image.new(
            "RGB",
            (500, 500),
            (40, 40, 40)
        )

    # -------------------------
    # ФОН ИЗ АВАТАРКИ
    # -------------------------

    background = avatar.copy()

    background = background.resize(
        (WIDTH, HEIGHT)
    )

    background = background.filter(
        ImageFilter.GaussianBlur(35)
    )

    background = background.convert("RGBA")

    # Затемняем фон
    dark_overlay = Image.new(
        "RGBA",
        (WIDTH, HEIGHT),
        (0, 0, 0, 120)
    )

    background.alpha_composite(dark_overlay)

    # -------------------------
    # ГРАДИЕНТ С ЦВЕТА АВАТАРКИ
    # -------------------------

    average_color = get_average_color(avatar)

    draw_gradient(
        background,
        average_color
    )

    # -------------------------
    # НИЖНЯЯ ТЁМНАЯ ПОДЛОЖКА
    # -------------------------

    overlay = Image.new(
        "RGBA",
        (WIDTH, HEIGHT),
        (0, 0, 0, 0)
    )

    overlay_draw = ImageDraw.Draw(overlay)

    overlay_draw.rounded_rectangle(
        (35, 35, WIDTH - 35, HEIGHT - 35),
        radius=35,
        fill=(15, 15, 20, 110)
    )

    background.alpha_composite(overlay)

    # -------------------------
    # РИСОВАНИЕ
    # -------------------------

    draw = ImageDraw.Draw(background)

    # Шрифты
    name_font = get_font(48, bold=True)
    text_font = get_font(35)
    id_font = get_font(23)
    time_font = get_font(25)

    # -------------------------
    # АВАТАРКА
    # -------------------------

    avatar_size = (230, 230)

    avatar_card = rounded_image(
        avatar,
        avatar_size,
        32
    )

    avatar_x = 110
    avatar_y = (HEIGHT - avatar_size[1]) // 2

    background.alpha_composite(
        avatar_card,
        (avatar_x, avatar_y)
    )

    # -------------------------
    # ИМЯ
    # -------------------------

    name = user.first_name or "Unknown"

    if user.last_name:
        name += f" {user.last_name}"

    text_x = 390
    name_y = 175

    draw.text(
        (text_x, name_y),
        name,
        font=name_font,
        fill="white"
    )

    # -------------------------
    # ТЕКСТ СООБЩЕНИЯ
    # -------------------------

    message_text = (
        reply.text
        or reply.caption
        or "Сообщение без текста"
    )

    lines = wrap_text(
        draw,
        message_text,
        text_font,
        680
    )

    quote_y = 255

    # Максимум 5 строк
    if len(lines) > 5:
        lines = lines[:5]

        lines[-1] += "..."

    for line in lines:

        draw.text(
            (text_x, quote_y),
            line,
            font=text_font,
            fill=(235, 235, 235)
        )

        quote_y += 48

    # -------------------------
    # ID ПОЛЬЗОВАТЕЛЯ
    # -------------------------

    id_text = f"ID: {user.id}"

    draw.text(
        (text_x, HEIGHT - 125),
        id_text,
        font=id_font,
        fill=(190, 190, 190)
    )

    # -------------------------
    # ЛОКАЛЬНОЕ ВРЕМЯ
    # -------------------------

    current_time = datetime.now().strftime("%H:%M")

    time_bbox = draw.textbbox(
        (0, 0),
        current_time,
        font=time_font
    )

    time_width = (
        time_bbox[2] - time_bbox[0]
    )

    draw.text(
        (
            WIDTH - time_width - 80,
            HEIGHT - 90
        ),
        current_time,
        font=time_font,
        fill=(220, 220, 220)
    )

    # -------------------------
    # СОХРАНЕНИЕ
    # -------------------------

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    file_path = (
        f"{OUTPUT_DIR}/quote_{user.id}_{reply.id}.png"
    )

    background.convert("RGB").save(
        file_path,
        quality=95
    )

    return file_path
