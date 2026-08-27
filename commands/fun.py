from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pyrogram import filters, enums
from pyrogram.errors import FloodWait
import asyncio
import random
from core import app
from cfg import PREFIXES

typing_active = {}
bull_active = set()
dice_game = False

font_text = ImageFont.truetype(
    "fonts/FredokaOneCyrillic-Regular.ttf", 48
)
font_id = ImageFont.truetype(
    "fonts/FredokaOneCyrillic-Regular.ttf", 40
)
font_username = ImageFont.truetype(
    "fonts/FredokaOneCyrillic-Regular.ttf", 30
)

font_wanted = ImageFont.truetype("fonts/Rye-Regular.ttf", 55)
font_wanted_user = ImageFont.truetype("fonts/FredokaOneCyrillic-Regular.ttf", 23)
font_wanted_username = ImageFont.truetype("fonts/FredokaOneCyrillic-Regular.ttf", 20)
font_reward = ImageFont.truetype("fonts/FredokaOneCyrillic-Regular.ttf", 35)

font_music_title = ImageFont.truetype("fonts/FredokaOneCyrillic-Regular.ttf", 42)
font_music_artist = ImageFont.truetype("fonts/FredokaOneCyrillic-Regular.ttf", 26)
font_music_time = ImageFont.truetype("fonts/FredokaOneCyrillic-Regular.ttf", 22)

@app.on_message(filters.me & filters.command("music", prefixes = PREFIXES))
async def music_card(client, message):
    reply = message.reply_to_message
    audio = reply.audio or reply.voice

    if not reply:
        return await message.edit("❌ Ответь на сообщение с музыкой")

    if not reply.audio or reply.voice:
        return await message.edit("❌ В сообщение музыка не обнаружена")

    thumb_path = None
    if audio.thumbs:
        thumb_path = await client.download_media(audio.thumbs[-1].file_id, file_name = "avatarMusic.jpeg")

    if thumb_path:
        raw_img = Image.open(thumb_path).convert("RGBA")
    else:
        raw_img = Image.new("RGBA", (500, 500), (60, 60, 40, 255))

    bg = raw_img.resize((1000, 400))
    bg = bg.filter(ImageFilter.BoxBlur(radius = 17))
    overlay = Image.new("RGBA", bg.size, (0, 0, 0, 160))
    bg = Image.alpha_composite(bg.convert("RGBA"), overlay)

    draw = ImageDraw.Draw(bg)

    avatar = raw_img.resize((280, 280))
    mask = Image.new("L", (280, 280), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 280, 280), radius = 35, fill = 255)
    avatar.putalpha(mask)
    bg.alpha_composite(avatar, (40, 70))

    title = audio.title
    author = audio.performer
    duration = audio.duration 
    duration_str = f"{duration // 60}:{duration % 60:02d}"

    text_x = 370
    draw.text((text_x, 100), title, font=font_music_title, fill="white")
    draw.text((text_x, 150), author, font=font_music_artist, fill=(167, 167, 167))
    
    final_buffer = BytesIO()
    bg.convert("RGB").save(final_buffer, "JPEG", quality = 90)
    final_buffer.seek(0)
    final_buffer.name = "music_card.jpeg"

    await message.reply_photo(photo = final_buffer)
    await message.delete()

@app.on_message(filters.me & filters.command("quote", prefixes=PREFIXES))
async def quote(client, message):
    reply = message.reply_to_message

    if not reply or not reply.from_user:
        return await message.edit("❌ Используй команду реплеем на сообщение")

    user = reply.from_user
    message_text = reply.text or reply.caption

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
        f"- {user.first_name}",
        font=font_id,
        fill=(66, 135, 245),
    )

    draw.text(
        (text_x, avatar_y + avatar_size - 38),
        f"ID: {user.id}",
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

@app.on_message(filters.me & filters.command("wanted", prefixes = PREFIXES))
async def wanted_user(client, message):
    reply = message.reply_to_message

    if not reply or not reply.from_user:
        return await message.edit("❌ Используй ответом на сообщение")

    user = reply.from_user
    message_text = reply.text or reply.caption

    if not user.photo:
        return await message.edit("❌ У пользователя нету аватара")

    await message.edit(f"🔍 Ищу <b>{user.first_name}</b> в базе преступников...")
    await asyncio.sleep(1.7)

    await message.edit("Отправляю сведения...")

    avatar_path = await client.download_media(user.photo.big_file_id, file_name = "avatar_wantedUser.jpeg")

    raw_img = Image.open(avatar_path).convert("RGBA")
    
    bg = raw_img.resize((400, 800))
    bg = bg.filter(ImageFilter.BoxBlur(radius = 28))
    overlay = Image.new("RGBA", bg.size, (0, 0, 0, 165))
    bg = Image.alpha_composite(bg.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(bg)

    avatar_img = raw_img.resize((300, 300))

    mask = Image.new("L", (300, 300), 0)
    mask_draw = ImageDraw.Draw(mask)

    mask_draw.rounded_rectangle((0, 0, 300, 300), radius = 55, fill = 255)
    avatar_img.putalpha(mask)

    avatar_x = (400 - 300) // 2

    bg.alpha_composite(avatar_img, (avatar_x, 150))

    random_reward = random.randint(100000, 10000000)
    user_name = f"@{user.username}" if user.username else f"{user.id}"
    
    draw.text((200, 45), "WANTED", font=font_wanted, fill=(252, 0, 50), anchor="mm")
    draw.text((200, 550), f"- {user.first_name} -", font=font_wanted_user, fill=(217, 217, 217), anchor="mm")
    draw.text((200, 585), f"{user_name}", font=font_wanted_username, fill=(148, 148, 148), anchor="mm")
    draw.text((200, 750), f"REWARD: ${random_reward}", font = font_reward, fill="white", anchor="mm")

    final_buffer = BytesIO()
    bg.convert("RGB").save(final_buffer, "JPEG", qualite = 85)
    final_buffer.seek(0)
    final_buffer.name = "wanted.jpeg"
    
    await message.reply_photo(photo=final_buffer)
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

    args = message.text.split(maxsplit=2)

    reply = message.reply_to_message

    if len(args) > 1 and args[1].lower() == "stop":
        
        if not reply or not reply.from_user:
            return await message.edit("❌ Используй реплеем")
        
        if reply.from_user.id not in bull_active:
            return await message.edit("❌ Пользователь не найден")
        
        bull_active.remove(reply.from_user.id)

        return await message.edit("Пользователь удален")

    if not reply or not reply.from_user:
        return await message.edit("❌ Используй реплеем")

    user_id = reply.from_user.id

    if user_id in bull_active:
        return await message.edit("❌ Пользователь уже добавлен")

    bull_active.add(user_id)

    await message.edit("Пользователь добавлен")

@app.on_message(~filters.me & filters.incoming, group = 1)
async def bull_loop(client, message):
    if not message.from_user:
        return

    chat_id = message.chat.id

    user_id = message.from_user.id

    if user_id not in bull_active:
        return

    with open("bull/shablon.txt", "r", encoding="utf-8") as file:
        phrases = [
            line.strip()
            for line in file
            if line.strip()
        ]

    if not phrases:
        return

    phrase = random.choice(phrases)

    await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
    await asyncio.sleep(2.5)
    await client.send_message(
        chat_id=message.chat.id,
        text=phrase,
        reply_to_message_id=message.id)

@app.on_message(filters.me & filters.command('type', prefixes = PREFIXES))
async def type_anim(client, message):

    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        return await message.edit("❌ Используй: <code>.type text</code>")

    orig_text = args[1]
    text = orig_text
    tbp = ""
    symbol = "|"

    while(tbp != orig_text):
        try:
            await message.edit(tbp + symbol)
            await asyncio.sleep(0.05)

            tbp = tbp + text[0]
            text = text[1:]

            await message.edit(tbp)
            await asyncio.sleep(0.05)

        except FloodWait as e:
            await asyncio.sleep(e.value)

@app.on_message(filters.me & filters.command("dice", prefixes = PREFIXES))
async def dice_status_edit(client, message):

    global dice_game

    args = message.text.split(maxsplit=2)

    if len(args) > 1 and args[1].lower() == "stop":
        if not dice_game:
            return await message.edit("❌ Игра с кубиком не запущена, используй <code>.dice</code> для запуска")

        dice_game = False
        return await message.edit("✅ Игра прекращена")

    if dice_game:
        return await message.edit("❌ Игра уже запущена, используй <code>.dice stop</code> для остановки")

    dice_game = True

    await message.edit("✅ Игра с кубиком запущена")

@app.on_message(~filters.me & filters.incoming, group = 2)
async def dice_send(client, message):
    global dice_game

    if not dice_game:
        return

    player1 = message.dice.value
    player2 = await client.send_dice(chat_id = message.chat.id, reply_to_message_id=message.id,emoji = "🎲")

    await asyncio.sleep(4)

    if player1 > player2.dice.value:
        return await message.reply(f"Удача на твоей стороне. {player1} VS {player2.dice.value}")
    elif player1 < player2.dice.value:
        return await message.reply(f"Моя взяла. {player2.dice.value} VS {player1}")
    else:
        return await message.reply("Судьба не выбрала победителя.")
