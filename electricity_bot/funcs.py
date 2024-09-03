from telebot import TeleBot, types  # type: ignore
from telebot import apihelper

from electricity_bot.vars import generic_choice, _generic_markup
from electricity_bot.config import ADDRESS, admins
from electricity_bot.time import get_time, get_unix, get_date
import electricity_bot.formatter as formatter

from threading import Event

import time
import schedule
import logging


logger = logging.getLogger("general")
outage_logger = logging.getLogger("outage")


def notify(bot: TeleBot, group: str | list, message: str):
    if isinstance(group, list):
        group_list = group
    else:
        group_list = bot.user_storage.read()[group]
    for user_id in group_list:
        try:
            bot.send_message(
                user_id,
                message,
                parse_mode="html",
            )
            logger.info(f"Notified: {user_id}")
            continue
        except apihelper.ApiTelegramException as e:
            if e.error_code == 403:
                logger.error(
                    f"{user_id} has blocked the bot. Removing them from the list"
                )
                bot.user_storage.delete(user_id, group)
            elif e.error_code in [401, 404]:
                logger.error(f"Could not access {user_id}. Removing them from the list")
                bot.user_storage.delete(user_id, group)
            continue
        except Exception as e:
            logger.error(
                f"{e} occured. Take actions regarding this error as soon as possible."
            )
            continue
    logger.info(f"Users notified.")


def termux_loop(bot: TeleBot, run_event: Event) -> None:
    if bot.debug_termux:
        import random

        class TermuxApi:
            def battery_status(self) -> dict[str:str]:
                states = ["PLUGGED_AC", "UNPLUGGED"]
                result = random.randint(0, 1)
                self.result = {"plugged": states[result]}
                return self

        termux_api = TermuxApi()
    else:
        from electricity_bot import termux_api

    a = termux_api.battery_status()
    if a.result["plugged"] == "UNPLUGGED":
        bot.state_v = False
    else:
        bot.state_v = True

    logger.info(
        f"Electricity checker thread initialized. Initial state: {a.result['plugged']}"
    )
    outage_logger.info(
        f"Electricity checker thread initialized. Initial state: {a.result['plugged']}"
    )

    i = 0
    while run_event.is_set():
        i += 1
        time.sleep(10)
        current_time = get_time()
        a = termux_api.battery_status()
        logger.debug(f"ECT: Iteration #{i}, state: {a.result['plugged']}")
        if a.result["plugged"] == "UNPLUGGED":
            if bot.state_v != False:
                bot.state_v = False
                unix = get_unix()
                bot.outages_storage.temp("start", unix)
                bot.last_power_off = unix
                bot.last_power_off_local = unix
                logger.info(f"Electricity is out. Notifying users.")
                outage_logger.info(f"Electricity is out.")
                notify(
                    bot,
                    "outages",
                    f"❌ {current_time} - {ADDRESS}, світло вимкнули. Світло було {formatter.format(bot.last_power_off-bot.last_power_on)}",
                )
            else:
                continue
        else:
            if bot.state_v != True:
                bot.state_v = True
                unix = get_unix()
                bot.outages_storage.temp("end", unix)
                bot.last_power_on = unix
                bot.outages_storage.save(bot.last_power_off_local, bot.last_power_on)
                logger.info(f"Electricity is back on. Notifying users.")
                outage_logger.info(f"otg Electricity is back on.")
                notify(
                    bot,
                    "outages",
                    f"✅ {current_time} - {ADDRESS}, світло увімкнули. Світла не було {formatter.format(bot.last_power_on-bot.last_power_off)}",
                )
            else:
                continue


def generic(message: types.Message, bot: TeleBot) -> None:
    generic_markup = _generic_markup(bot, message.from_user.id)
    name = message.from_user.first_name
    bot.send_message(
        message.chat.id,
        f"👋 Чим я можу тобі допомогти,<b> {name}</b>?",
        parse_mode="html",
        reply_markup=generic_markup,
    )


def stats_job(bot: TeleBot) -> None:
    if not bot.state_v:
        bot.last_power_on_local = get_unix()
        bot.last_power_off_local = get_unix()
        bot.outages_storage.save(bot.last_power_off, bot.last_power_on_local)
    stats(bot, get_date(-1))


def scrape_job(bot: TeleBot, date_i: int = None, user_id: int = None) -> None:
    if date_i == None:
        date_i = 1
    date = get_date(date_i)
    logger.info(f"Scraping images from {bot.image_scraper.url}.")
    if user_id != None:
        bot.send_message(
            user_id,
            f"Scraping images from {bot.image_scraper.url}.",
            parse_mode="html",
        )
    images = bot.image_scraper.scrape_images()
    if len(images) > 0:
        try:
            if date_i > 0:
                image = images[1]
            else:
                image = images[0]
            bot.id_storage.save(image, date)
            logger.info("Schedule image scraped successfully.")
            if user_id != None:
                bot.send_message(
                    user_id,
                    "Schedule image scraped successfully.",
                )
        except Exception as e:
            logger.error(
                f"{e} occured. Take actions regarding this error as soon as possible."
            )
            if user_id != None:
                bot.send_message(
                    user_id,
                    f"{e} occured. Take actions regarding this error as soon as possible.",
                )

    else:
        logger.error("Found no images to scrape")
        if user_id != None:
            bot.send_message(
                user_id,
                "Found no images to scrape",
            )


def schedule_loop(run_event: Event) -> None:
    while run_event.is_set():
        schedule.run_pending()
        time.sleep(1)


def stats(bot: TeleBot, date: str = None, message: types.Message = None) -> None:
    if date == None:
        date: str = get_date(-1)
    data = bot.outages_storage.read()
    if date in data.keys():
        total: int = 0
        outages: dict = dict(list(data[date].items())[1:]).keys()
        for outage in outages:
            if bot.outages_storage.exists(outage, date):
                total += bot.outages_storage.lasted(outage, date)

        count: int = bot.outages_storage.get_outage("outages", date)
        message_text: str = (
            f"💡 Статистика відключень за {get_date(-1)}: \n\nКількість відключень: {count}\n\nЗагалом світла не було {formatter.format(total)}, що складає {round((total/86400)*100, 1)}% доби"
        )
    else:
        message_text: str = f"🥳 За минулу добу не було жодного відключення світла!"
    if message == None:
        notify(bot, "stats", message_text)
    else:
        logger.info(f"Notified: {message.from_user.id}")
        bot.send_message(
            message.from_user.id,
            message_text,
            parse_mode="html",
        )
