from electricity_bot.application import Application
from electricity_bot.config import TOKEN, TOKEN_DEBUG
from electricity_bot.logger import setup_logging
from electricity_bot.time import get_date, get_time
from logging import INFO, DEBUG
import argparse


def main() -> None:
    parser = argparse.ArgumentParser("TGEB")
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-dt", "--debug-termux", action="store_true")
    args = parser.parse_args()

    file_name = f"bot_{get_date()}_{get_time('-')}.txt"

    setup_logging(file_name, DEBUG if args.debug else INFO)

    token = TOKEN_DEBUG if args.debug else TOKEN
    app = Application(token, args.debug, args.debug_termux)
    app.infinity_polling()


if __name__ == "__main__":
    main()
