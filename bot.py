from core import app

def load_modules():
    import commands.basic
    import commands.automation

if __name__ == "__main__" :

    print("USERBOT запущен")

    load_modules()

    app.run()
