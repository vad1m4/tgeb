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
    logs_str,
    user_stats_str,
)
from electricity_bot.time import get_date, get_unix

# from electricity_bot.logger import add_logger
from electricity_bot.config import admins
import electricity_bot.commands as commands
import electricity_bot.funcs as funcs
from electricity_bot.image_scraper import TGEBImageScraper
import electricity_bot.admin_commands as admin_cmd

from pathlib import Path

import logging
import threading
import schedule


logger = logging.getLogger("general")


class Application(TeleBot):
    def __init__(
        self, token: str, debug: bool = False, debug_termux: bool = False
    ) -> None:

        self.debug = debug
        self.debug_termux = debug_termux

        ### Telegram bot init

        exception_handler = TGEBExceptionHandler()

        super().__init__(token, exception_handler=exception_handler)
        logger.info("Telegram bot initialized")

        ### Storage init

        self.user_storage = JSONFileUserStorage(Path.cwd() / "users.json")
        self.id_storage = JSONFileScheduleStorage(Path.cwd() / "schedules.json")
        self.outages_storage = JSONFileOutageStorage(Path.cwd() / "outages.json")
        logger.info("Storage initialized")

        ### Electricity checker loop init

        try:
            temp_start = self.outages_storage.read()["temp_start"]
            temp_end = self.outages_storage.read()["temp_end"]
        except KeyError or UnboundLocalError:
            temp_start = get_unix()
            temp_end = get_unix()
            self.outages_storage.temp("start", temp_start)
            self.outages_storage.temp("end", temp_end)
            logger.warn(
                "Temporary values not found inside outages.json. Using get_unix instead"
            )
        finally:
            self.last_power_on: int = temp_start
            self.last_power_off: int = temp_end
            self.last_power_on_local: int = temp_start
            self.last_power_off_local: int = temp_end

        self.state_v: bool = bool
        self._init_loop()

        self.image_scraper = TGEBImageScraper("https://poweron.loe.lviv.ua/")

        self._init_schedule()

        self.chunks = {}
        logger.info("All services have been initalized successfully")
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
                commands._see_schedule(message, self)
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
                funcs.scrape_job(self, 0, message.from_user.id)
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

        @self.message_handler(regexp=logs_str)
        @self.message_handler(commands=["logs"])
        def logs(message: Message):
            if self.is_admin(message.from_user.id):
                admin_cmd.logs_menu(self, message)
            else:
                admin_cmd.not_admin(message, self)

        @self.callback_query_handler(
            func=lambda call: call.data.startswith("page_")
            or call.data in ["exit", "send_file"]
        )
        def handle_page_navigation(call):
            if call.data in ["exit", "send_file"]:
                self.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="Ви вийшли з режиму перегляду файлу.",
                )
                if call.data == "send_file":
                    admin_cmd.send_file(
                        call.message, self, self.chunks[call.message.id][1]
                    )
                self.chunks.pop(call.message.id)
                admin_cmd.menu(call.from_user, self)
            else:
                page_number = int(call.data.split("_")[1])
                admin_cmd.update_page(
                    call.message,
                    call.message.message_id,
                    call.message.chat.id,
                    self,
                    page_number,
                )

        @self.message_handler(regexp=user_stats_str)
        @self.message_handler(commands=["user_stats"])
        def logs(message: Message):
            if self.is_admin(message.from_user.id):
                admin_cmd.user_stats(self, message)
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

    def _init_schedule(self):

        schedule.every().day.at("00:00", "Europe/Kiev").do(funcs.stats_job, self)

        schedule.every().day.at("05:00", "Europe/Kiev").do(funcs.scrape_job, self, 0)
        schedule.every().day.at("10:00", "Europe/Kiev").do(funcs.scrape_job, self, 0)
        schedule.every().day.at("11:00", "Europe/Kiev").do(funcs.scrape_job, self, 0)
        schedule.every().day.at("12:00", "Europe/Kiev").do(funcs.scrape_job, self, 0)
        schedule.every().day.at("13:00", "Europe/Kiev").do(funcs.scrape_job, self, 0)
        schedule.every().day.at("14:00", "Europe/Kiev").do(funcs.scrape_job, self, 0)
        schedule.every().day.at("15:00", "Europe/Kiev").do(funcs.scrape_job, self, 0)
        schedule.every().day.at("16:00", "Europe/Kiev").do(funcs.scrape_job, self, 0)
        schedule.every().day.at("17:00", "Europe/Kiev").do(funcs.scrape_job, self, 0)
        schedule.every().day.at("18:00", "Europe/Kiev").do(funcs.scrape_job, self, 0)
        schedule.every().day.at("19:00", "Europe/Kiev").do(funcs.scrape_job, self, 0)
        schedule.every().day.at("19:00", "Europe/Kiev").do(funcs.scrape_job, self, 1)
        schedule.every().day.at("21:00", "Europe/Kiev").do(funcs.scrape_job, self, 1)

        run_event = threading.Event()
        run_event.set()
        t = threading.Thread(
            target=funcs.schedule_loop,
            args=(run_event,),
        )
        t.start()

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
