from core import app

def load_modules():
    import commands.basic
    import commands.automation
    import commands.fun
    import commands.msg_user

if __name__ == "__main__" :

    print("USERBOT запущен")

    load_modules()

    app.run()
