from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pyrogram import filters, enums
import asyncio
import random
from core import app
from cfg import PREFIXES

typing_active = {}
bull_active = set()

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
        (text_x, avatar_y + avatar_size - 38),
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
        (text_x, message_y - 10),
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
        "#",
        "#2",
        "#20",
        "#201",
        "#2016"
    ]

    for step in steps:
        await message.edit(step)
        await asyncio.sleep(0.61)
    await asyncio.sleep(0.7)

    url = ("https://www.image2url.com/r2/default/files/1787585136007-cd55e8a9-6014-4de7-870a-fa00010cfd4b.mp4")

    text = """<blockquote>Я стою как thunderstorm, зови меня «onda andar»
Зеркала меня слепят, зови меня «onda andar»

Я стою как thunderstorm, зови меня «onda andar»
Зеркала меня слепят, зови меня «onda andar»

Я стою как thunderstorm, зови меня «onda andar»
Зеркала меня слепят, зови меня «onda andar»</blockquote>"""

    await client.send_video(
        message.chat.id,
        video=url,
        caption=text,
        supports_streaming=True,
        parse_mode=enums.ParseMode.HTML
    )

    await message.delete()

@app.on_message(filters.me & filters.command("roast", prefixes = PREFIXES))
async def roast(client, message):
    reply = message.reply_to_message

    if not reply or not reply.from_user:
        return await message.edit("❌ Используй на ответ пользователя")

    user = reply.from_user
    name = f"@{user.username}" if user.username else f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

    roasts = [
        f"{name}, ты не тормоз — ты просто даёшь всем шанс тебя обогнать.",
        f"{name} настолько загадочный человек, что даже его мысли иногда не знают, куда идут.",
        f"{name} пишет так уверенно, будто проверял информацию в комментариях YouTube.",
        f"У {name} такой вайб, будто он зашёл на минутку и случайно стал легендой чата.",
        f"{name} — причина, по которой кнопка «редактировать сообщение» вообще существует.",
        f"{name}, твой план был хорошим. Жаль, что он не пережил встречу с реальностью.",
        f"{name} выглядит как человек, который говорит «я всё понял», а потом спрашивает ещё раз.",
        f"{name}, ты не опоздал — ты просто появился в своём часовом поясе.",
        f"{name} настолько уникален, что ошибки рядом с ним начинают выглядеть как стиль.",
        f"{name}, если бы уверенность была интернетом, у тебя был бы безлимит."
    ]

    await message.edit(random.choice(roasts))

@app.on_message(filters.me & filters.command("typing", prefixes = PREFIXES))
async def typing(client, message):
    chat_id = message.chat.id

    args = message.text.split(maxsplit=2)

    if len(args) > 1 and args[1].lower() == "stop":
        task = typing_active.pop(chat_id, None)

        if not task:
            return await message.edit("❌ Тайпинг не запущен")

        task.cancel()

        chat = await client.get_chat(chat_id)
        chat_name = chat.title or chat.first_name

        return await message.edit(f"✅ Тайпинг в чате <b>{chat_name}</b> остановлен")

    if chat_id in typing_active:
        return await message.edit("❌ Тайпинг уже запущен, для остановки: <code>.typing stop</code>")
    
    chat = await client.get_chat(chat_id)
    chat_name = chat.title or chat.first_name
    
    await message.edit(f"⌨️ Тайпинг в чате <b>{chat_name}</b> запущен")
    
    async def typing_loop():
        try:
            while chat_id in typing_active:
                await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
                await asyncio.sleep(12)
        finally:
            typing_active.pop(chat_id, None)
    
    typing_active[chat_id] = asyncio.create_task(typing_loop())

@app.on_message(filters.me & filters.command('bull', prefixes = PREFIXES))
async def bull(client, message):
    reply = message.reply_to_message

    if not reply or not reply.from_user:
        return await message.edit("❌ Используй реплеем")

    user_id = reply.from_user.id

    if user_id in bull_active:
        return await message.edit("Пользователь уже добавлен")

    bull_active.add(user_id)

    await message.edit("Пользователь добавлен")

@app.on_message(filters.incoming & filters.text)
async def bull_loop(client, message):
    if not message.from_user:
        return
        
    user_id = message.from_user.id

    if user_id not in bull_active:
        return
    
    with open("bull/shablon.txt", "r", encoding = "utf-8") as f:
        phrases = [line.strip() for line in f if line.strip()]

    phrases = random.choiсe(phrases)
                
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await asyncio.sleep(3.5)
    await message.reply_text(phrases)


