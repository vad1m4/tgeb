from electricity_bot.application import Application
from electricity_bot.config import TOKEN, TOKEN_DEBUG
import sys

### Command line args

debug = False
debug_termux = False
token = TOKEN

if "--debug" in sys.argv or "--d" in sys.argv:
    debug = True
    token = TOKEN_DEBUG

if "--debug-termux" in sys.argv or "--dt" in sys.argv:
    debug_termux = True


def main() -> None:
    app = Application(token, debug, debug_termux)
    app.infinity_polling()


if __name__ == "__main__":
    main()
