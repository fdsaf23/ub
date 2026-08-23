# Telegram Userbot

Минимальный Telegram userbot на Python и Pyrogram. Авторизация выполняется
через строку сессии (`STRING_SESSION`), поэтому файл `userbot.session` для
работы не нужен.

## Установка

Нужен Python 3.10 или новее.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Откройте `.env` и укажите `API_ID` и `API_HASH`, полученные на
[my.telegram.org/apps](https://my.telegram.org/apps), а также строку сессии.

## Как получить STRING_SESSION

Создайте её один раз локально. Команда попросит номер телефона, код Telegram и,
если включена, двухфакторную аутентификацию:

```powershell
python generate_session.py
```

Скопируйте выведенную строку целиком в `STRING_SESSION` в `.env`, затем
запустите userbot:

```powershell
python bot.py
```

## Команды

- `.help` или `/help` — список команд.

## Публикация на GitHub

В репозиторий можно добавлять исходный код, `.env.example`, `README.md` и
`requirements.txt`. `.env`, строки сессии и файлы `*.session` уже исключены в
`.gitignore`.

> Не публикуйте `STRING_SESSION`: она даёт полный доступ к Telegram-аккаунту.
