import telebot
from telebot import types
from telebot.types import Message
from electricity_bot.config import admins
from electricity_bot.storage import JSONFileUserStorage
import electricity_bot.commands as commands
import time
from pathlib import Path
import threading
import random


class Application(telebot.TeleBot):
    def __init__(self, token) -> None:
        super().__init__(token)

        self.storage = JSONFileUserStorage(Path.cwd() / "database.json")
        self.__init__loop()

        self.state_v = bool

        @self.message_handler(commands=["start"])
        def start_h(message: Message) -> None:
            commands.start(message, self)

        @self.message_handler(regexp="Підписатися на сповіщення")
        @self.message_handler(commands=["subscribe"])
        def subscribe_h(message: Message) -> None:
            commands.subscribe(message, self)

        @self.message_handler(regexp="Відписатися від сповіщень")
        @self.message_handler(commands=["unsubscribe"])
        def unsubscribe_h(message: Message) -> None:
            commands.unsubscribe(message, self)

        @self.message_handler(regexp="Який стан світла?")
        @self.message_handler(commands=["electricitystate"])
        def state_h(message: Message) -> None:
            commands.state(message, self)

        @self.message_handler(commands=["addschedule"])
        def schedule_h(message: Message) -> None:
            commands.add_schedule(message, self, False)
    def __init__loop(self):
        # a = termux_api.battery_status()
        # a.result['plugged']
        run_event = threading.Event()
        run_event.set()
        t = threading.Thread(
            target=commands.loop,
            args=(
                self,
                run_event,
            ),
        )
        t.start()

    def is_admin(self, message: Message) -> bool:
        if not message.from_user.id in admins:
            return False
        else:
            return True