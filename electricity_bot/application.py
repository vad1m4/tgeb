import telebot
from telebot.types import Message
from electricity_bot.storage import (
    JSONFileUserStorage,
    JSONFileScheduleStorage,
    JSONFileOutageStorage,
)
from electricity_bot.exception_handler import TGEBExceptionHandler
from electricity_bot.vars import subscribe_str, unsubscribe_str, state_str, schedule_str
from electricity_bot.time import get_date, get_time
from electricity_bot.logger import TGEBLogger
import electricity_bot.commands as commands
import electricity_bot.funcs as funcs
from logging import INFO, DEBUG
from pathlib import Path
import threading


class Application(telebot.TeleBot):
    def __init__(
        self, token: str, debug: bool = False, debug_termux: bool = False
    ) -> None:

        ### Loggers

        self.debug = debug
        self.debug_termux = debug_termux

        if self.debug:
            self.level = DEBUG
        else:
            self.level = INFO

        self.general_logger = TGEBLogger(
            "General logger",
            f"general_logs/bot_{get_date()}_{get_time('-')}.txt",
            True,
            self.level,
        )

        self.outage_logger = TGEBLogger(
            "Outage logger", f"outage_logs/bot_{get_date()}_{get_time('-')}.txt"
        )
        self.general_logger.init("Outage logger", True, self.level)

        self.user_action_logger = TGEBLogger(
            "User action logger",
            f"user_action_logs/bot_{get_date()}_{get_time('-')}.txt",
        )
        self.general_logger.init("User action logger", True, self.level)

        ### Telegram bot init

        exception_handler = TGEBExceptionHandler(self.general_logger)

        try:
            super().__init__(token, exception_handler=exception_handler)
            self.general_logger.init("Telegram bot", True)
        except Exception as e:
            self.general_logger.init("Telegram bot", False)
            exit()

        ### Storage init

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
        try:
            self.outages_storage = JSONFileOutageStorage(Path.cwd() / "outages.json")
            self.general_logger.init("Outages storage", True)
        except Exception as e:
            self.general_logger.init("Outages storage", False)
            exit()

        ### Electricity checker loop init

        self.last_power_on = int
        self.last_power_off = int

        self.state_v = bool
        self._init_loop()

        ### Handle messages

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

    ### Electricity checker loop init

    def _init_loop(self):
        try:
            run_event = threading.Event()
            run_event.set()
            t = threading.Thread(
                target=funcs.loop,
                args=(
                    self,
                    run_event,
                ),
            )
            t.start()
        except Exception as e:
            self.general_logger.init("Electricity checker loop", False)
            exit()

    ### Check if user_id is in self.admins

    def is_admin(self, message: Message) -> bool:
        if not message.from_user.id in self.admins:
            return False
        else:
            return True
