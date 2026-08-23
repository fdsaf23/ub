from pyrogram import filters, enums
from core import app
from cfg import PREFIXES

@app.on_message(filters.me & filters.command("help", prefixes=PREFIXES))
async def help(client, message):

    text = """
<b>Все команды бота</b>
<blockquote>
<code>help</code> - список команд
</blockquote>
"""

    await message.edit(text, parse_mode = enums.ParseMode.HTML)
