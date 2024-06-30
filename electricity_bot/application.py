import telebot
from telebot import types
from telebot.types import Message
from electricity_bot.config import admins
from electricity_bot.storage import JSONFileUserStorage, JSONFileScheduleStorage
from electricity_bot.exception_handler import TGEBExceptionHandler
from electricity_bot.vars import subscribe_str, unsubscribe_str, state_str, schedule_str
from electricity_bot.time import get_date, get_time
from electricity_bot.logger import TGEBLogger
import electricity_bot.commands as commands
import time
from pathlib import Path
import threading
import random


class Application(telebot.TeleBot):
    def __init__(self, token) -> None:
        self.general_logger = TGEBLogger(
            "General logger", f"general_logs/bot_{get_date()}_{get_time('-')}.txt", True
        )
        self.general_logger.init("General logger", True)

        self.outage_logger = TGEBLogger(
            "Outage logger", f"outage_logs/bot_{get_date()}_{get_time('-')}.txt"
        )
        self.outage_logger.init("Outage logger", True)
        self.general_logger.init("Outage logger", True)

        self.user_action_logger = TGEBLogger(
            "User action logger",
            f"user_action_logs/bot_{get_date()}_{get_time('-')}.txt",
        )
        self.user_action_logger.init("User action logger", True)
        self.general_logger.init("User action logger", True)

        try:
            super().__init__(token, exception_handler=TGEBExceptionHandler())
            self.general_logger.init("Telegram bot", True)
        except Exception as e:
            self.general_logger.init("Telegram bot", False)
            exit()
        try:
            self.user_storage = JSONFileUserStorage(Path.cwd() / "users.json")
            self.general_logger.init("User storage", True)
        except Exception as e:
            self.general_logger.init("User storage", False)
            exit()
        try:
            self.id_storage = JSONFileScheduleStorage(Path.cwd() / "schedules.json")
            self.general_logger.init("Schedule storage", True)
        except Exception as e:
            self.general_logger.init("Schedule storage", False)
            exit()

        self._init_loop()

        self.state_v = bool

        @self.message_handler(commands=["start"])
        def start(message: Message) -> None:
            commands.start(message, self)

        @self.message_handler(regexp=subscribe_str)
        @self.message_handler(commands=["subscribe"])
        def subscribe(message: Message) -> None:
            commands.subscribe(message, self)

        @self.message_handler(regexp=unsubscribe_str)
        @self.message_handler(commands=["unsubscribe"])
        def unsubscribe(message: Message) -> None:
            commands.unsubscribe(message, self)

        @self.message_handler(regexp=state_str)
        @self.message_handler(commands=["electricitystate"])
        def state(message: Message) -> None:
            commands.state(message, self)

        @self.message_handler(regexp=schedule_str)
        @self.message_handler(commands=["seeschedule"])
        def see_schedule(message: Message) -> None:
            commands.see_schedule(message, self)

        @self.message_handler(commands=["addschedule"])
        def schedule(message: Message) -> None:
            commands.add_schedule(message, self, False)

        @self.message_handler(func=lambda message: True)
        def handle_other(message: Message) -> None:
            commands.handle_other(message, self)

    def _init_loop(self):
        # a = termux_api.battery_status()
        # a.result['plugged']
        try:
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
        except Exception as e:
            self.general_logger.init("Electricity checker loop", False)
            exit()

    def is_admin(self, message: Message) -> bool:
        if not message.from_user.id in admins:
            return False
        else:
            return True
