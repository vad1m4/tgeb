from telebot import TeleBot  # type: ignore
from telebot.types import Message  # type: ignore

from electricity_bot.storage import (
    JSONFileUserStorage,
    JSONFileScheduleStorage,
    JSONFileOutageStorage,
)
from electricity_bot.exception_handler import TGEBExceptionHandler
from electricity_bot.vars import (
    subscribe_str,
    unsubscribe_str,
    state_str,
    schedule_str,
    unsubscribe_stats_str,
    subscribe_stats_str,
    notifications_str,
    admin_str,
    add_schedule_str,
    scrape_str,
    current_date_str,
    blacklist_str,
    unblacklist_str,
    announcement_str,
    feedback_str,
    stats_str,
)
from electricity_bot.time import get_date, get_time
from electricity_bot.logger import TGEBLogger
from electricity_bot.config import admins
import electricity_bot.commands as commands
import electricity_bot.funcs as funcs
from electricity_bot.image_scraper import TGEBImageScraper
import electricity_bot.admin_commands as admin_cmd

from logging import INFO, DEBUG

from pathlib import Path

import threading

import schedule


class Application(TeleBot):
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
            self.general_logger.init("Telegram bot", False, e)
            exit()

        ### Storage init

        try:
            self.user_storage = JSONFileUserStorage(Path.cwd() / "users.json")
            self.general_logger.init("User storage", True)
        except Exception as e:
            self.general_logger.init("User storage", False, e)
            exit()
        try:
            self.id_storage = JSONFileScheduleStorage(Path.cwd() / "schedules.json")
            self.general_logger.init("Schedule storage", True)
        except Exception as e:
            self.general_logger.init("Schedule storage", False, e)
            exit()
        try:
            self.outages_storage = JSONFileOutageStorage(Path.cwd() / "outages.json")
            self.general_logger.init("Outages storage", True)
        except Exception as e:
            self.general_logger.init("Outages storage", False, e)
            exit()

        ### Electricity checker loop init

        self.last_power_on: int = self.outages_storage.read()["temp_start"]
        self.last_power_off: int = self.outages_storage.read()["temp_end"]

        self.last_power_on_local: int = self.outages_storage.read()["temp_start"]
        self.last_power_off_local: int = self.outages_storage.read()["temp_end"]

        self.state_v: bool = bool
        self._init_loop()

        try:
            self.image_scraper = TGEBImageScraper(
                self.general_logger, "https://poweron.loe.lviv.ua/"
            )
            self.general_logger.init("Image scraper", True)
        except Exception as e:
            self.general_logger.init("Image scraper", False, e)
            exit()

        self._init_schedule()

        ### User commands

        @self.message_handler(commands=["start"])
        def start(message: Message) -> None:
            if not self.user_storage.is_authorized(message.from_user.id):
                commands.start(message, self)
            else:
                funcs.generic(message, self)

        @self.message_handler(content_types=["contact"])
        def authorise(message: Message) -> None:
            commands.authorize(message, self)

        @self.message_handler(regexp=subscribe_str)
        @self.message_handler(commands=["subscribe"])
        def subscribe(message: Message) -> None:
            if self.user_storage.is_authorized(message.from_user.id):
                commands.subscribe(message, self)
            else:
                commands.not_authorized(message, self)

        @self.message_handler(regexp=unsubscribe_str)
        @self.message_handler(commands=["unsubscribe"])
        def unsubscribe(message: Message) -> None:
            if self.user_storage.is_authorized(message.from_user.id):
                commands.unsubscribe(message, self)
            else:
                commands.not_authorized(message, self)

        @self.message_handler(regexp=subscribe_stats_str)
        @self.message_handler(commands=["subscribestats"])
        def subscribe_stats(message: Message) -> None:
            if self.user_storage.is_authorized(message.from_user.id):
                commands.subscribe_stats(message, self)
            else:
                commands.not_authorized(message, self)

        @self.message_handler(regexp=unsubscribe_stats_str)
        @self.message_handler(commands=["unsubscribestats"])
        def unsubscribe_stats(message: Message) -> None:
            if self.user_storage.is_authorized(message.from_user.id):
                commands.unsubscribe_stats(message, self)
            else:
                commands.not_authorized(message, self)

        @self.message_handler(regexp=notifications_str)
        @self.message_handler(commands=["notifications"])
        def notifications(message: Message) -> None:
            if self.user_storage.is_authorized(message.from_user.id):
                commands.notifications(message, self)
            else:
                commands.not_authorized(message, self)

        @self.message_handler(regexp=state_str)
        @self.message_handler(commands=["electricitystate"])
        def state(message: Message) -> None:
            if self.user_storage.is_authorized(message.from_user.id):
                commands.state(message, self)
            else:
                commands.not_authorized(message, self)

        @self.message_handler(regexp=schedule_str)
        @self.message_handler(commands=["seeschedule"])
        def see_schedule(message: Message) -> None:
            if self.user_storage.is_authorized(message.from_user.id):
                commands.see_schedule(message, self)
            else:
                commands.not_authorized(message, self)

        @self.message_handler(regexp=feedback_str)
        @self.message_handler(commands=["feedback"])
        def handle_other(message: Message) -> None:
            if self.user_storage.is_authorized(message.from_user.id):
                commands._feedback(message, self)
            else:
                commands.not_authorized(message, self)

        @self.message_handler(regexp="Назад")
        def handle_other(message: Message) -> None:
            if self.user_storage.is_authorized(message.from_user.id):
                funcs.generic(message, self)
            else:
                commands.not_authorized(message, self)

        ### Admin commands

        @self.message_handler(regexp=admin_str)
        @self.message_handler(commands=["adminmenu"])
        def admin_menu(message: Message):
            if self.is_admin(message.from_user.id):
                admin_cmd.menu(message, self)
            else:
                admin_cmd.not_admin(message, self)

        @self.message_handler(regexp=add_schedule_str)
        @self.message_handler(commands=["addschedule"])
        def addschedule(message: Message) -> None:
            if self.is_admin(message.from_user.id):
                admin_cmd.add_schedule(message, self)
            else:
                admin_cmd.not_admin(message, self)

        @self.message_handler(regexp=scrape_str)
        @self.message_handler(commands=["scrape"])
        def scrape(message: Message) -> None:
            if self.is_admin(message.from_user.id):
                funcs.scrape_job(self, get_date(), message.from_user.id, True)
            else:
                admin_cmd.not_admin(message, self)

        @self.message_handler(regexp=current_date_str)
        @self.message_handler(commands=["currentdate"])
        def current_date(message: Message) -> None:
            if self.is_admin(message.from_user.id):
                admin_cmd.current_date(message, self)
            else:
                admin_cmd.not_admin(message, self)

        @self.message_handler(regexp=blacklist_str)
        @self.message_handler(commands=["block"])
        def block(message: Message) -> None:
            if self.is_admin(message.from_user.id):
                admin_cmd._blacklist_(message, self)
            else:
                admin_cmd.not_admin(message, self)

        @self.message_handler(regexp=unblacklist_str)
        @self.message_handler(commands=["unblock"])
        def unblock(message: Message) -> None:
            if self.is_admin(message.from_user.id):
                admin_cmd._unblacklist(message, self)
            else:
                admin_cmd.not_admin(message, self)

        @self.message_handler(regexp=announcement_str)
        @self.message_handler(commands=["announce"])
        def unblock(message: Message) -> None:
            if self.is_admin(message.from_user.id):
                admin_cmd._announce_(message, self)
            else:
                admin_cmd.not_admin(message, self)

        @self.message_handler(regexp=stats_str)
        @self.message_handler(commands=["stats"])
        def stats(message: Message):
            if self.is_admin(message.from_user.id):
                funcs.stats(self, get_date(-1), message)
            else:
                admin_cmd.not_admin(message, self)

        ### Handle other

        @self.message_handler(func=lambda message: True)
        def handle_other(message: Message) -> None:
            if self.user_storage.is_authorized(message.from_user.id):
                commands.handle_other(message, self)
            else:
                commands.not_authorized(message, self)

    ### Electricity checker loop init

    def _init_loop(self):
        try:
            run_event = threading.Event()
            run_event.set()
            t = threading.Thread(
                target=funcs.termux_loop,
                args=(
                    self,
                    run_event,
                ),
            )
            t.start()
        except Exception as e:
            self.general_logger.init("Electricity checker loop", False)
            exit()

    def _init_schedule(self):

        schedule.every().day.at("00:00", "Europe/Kiev").do(funcs.stats_job, self)

        schedule.every().day.at("22:00", "Europe/Kiev").do(funcs.scrape_job, self)

        try:
            run_event = threading.Event()
            run_event.set()
            t = threading.Thread(
                target=funcs.schedule_loop,
                args=(
                    self,
                    run_event,
                ),
            )
            t.start()
        except Exception as e:
            self.general_logger.init("Schedule loop", False)
            exit()

    ### Check if user_id is in self.admins

    def is_admin(self, user_id: int) -> bool:
        if not user_id in admins:
            return False
        else:
            return True

        # def start_message(message):
        #     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        #     reg_button = types.KeyboardButton(text="Отправить номер телефона",
        #     request_contact=True)
        #     keyboard.add(reg_button)
        #     bot.send_message(message.chat.id, 'Оставьте ваш контактный номер чтобы наш менеджер смог связаться с вами. ', reply_markup=keyboard)
