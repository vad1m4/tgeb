from electricity_bot.application import Application
from electricity_bot.config import TOKEN, TOKEN_DEBUG
import argparse

### Command line args


def main() -> None:
    parser = argparse.ArgumentParser("TGEB")
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-dt", "--debug-termux", action="store_true")
    args = parser.parse_args()

    token = TOKEN_DEBUG if args.debug else TOKEN
    app = Application(token, args.debug, args.debug_termux)
    app.infinity_polling()


if __name__ == "__main__":
    main()
