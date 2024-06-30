from electricity_bot.application import Application
from electricity_bot.config import TOKEN


def main() -> None:
    app = Application(TOKEN)
    app.polling(none_stop=True)


if __name__ == "__main__":
    main()
