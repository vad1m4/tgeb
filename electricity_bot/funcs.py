from telebot import TeleBot, types
from electricity_bot.vars import generic_choice, generic_markup, cancel
from electricity_bot.config import ADDRESS
from electricity_bot.time import get_time, get_unix, get_date
import electricity_bot.formatter as formatter
from threading import Event
import time
import schedule

# from application import Application


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
        bot.last_power_off = get_unix()
        bot.last_power_off_local = get_unix()
    else:
        bot.state_v = True
        bot.last_power_on = get_unix()
        bot.last_power_on_local = get_unix()

    bot.general_logger.info(
        f"Electricity checker thread initialized. Initial state: {a.result['plugged']}"
    )
    bot.outage_logger.info(
        f"Electricity checker thread initialized. Initial state: {a.result['plugged']}"
    )

    i = 0
    while run_event.is_set():
        i += 1
        time.sleep(10)
        current_time = get_time()
        a = termux_api.battery_status()
        bot.general_logger.debug(f"ECT: Iteration #{i}, state: {a.result['plugged']}")
        if a.result["plugged"] == "UNPLUGGED":
            if bot.state_v != False:
                bot.state_v = False
                bot.last_power_off = get_unix()
                bot.last_power_off_local = get_unix()
                bot.general_logger.info(f"Electricity is out. Notifying users.")
                bot.outage_logger.warning(f"Electricity is out.")
                for user_id in bot.user_storage.read()["outages"]:
                    try:
                        bot.general_logger.info(f"Notified: {user_id}")
                        bot.send_message(
                            user_id,
                            f"❌ {current_time} - {ADDRESS}, світло вимкнули. Світло було {formatter.format(bot.last_power_off-bot.last_power_on)}",
                            parse_mode="html",
                        )
                    except Exception as e:
                        bot.general_logger.error(
                            f"{e} occured. Take actions regarding this error as soon as possible."
                        )
                        continue
                bot.general_logger.info(f"Users notified.")
            else:
                continue
        else:
            if bot.state_v != True:
                bot.state_v = True
                bot.last_power_on = get_unix()
                bot.outages_storage.save(bot.last_power_off_local, bot.last_power_on)
                bot.general_logger.info(f"Electricity is back on. Notifying users.")
                bot.outage_logger.warning(f"Electricity is back on.")
                for user_id in bot.user_storage.read()["outages"]:
                    try:
                        bot.general_logger.info(f"Notified: {user_id}")
                        bot.send_message(
                            user_id,
                            f"✅ {current_time} - Івасюка 50А, світло увімкнули. Світла не було {formatter.format(bot.last_power_on-bot.last_power_off)}",
                            parse_mode="html",
                        )
                    except Exception as e:
                        bot.general_logger.error(
                            f"{e} occured. Take actions regarding this error as soon as possible."
                        )
                        continue
                bot.general_logger.info(f"Users notified.")
            else:
                continue


def generic(message: types.Message, bot: TeleBot) -> None:
    name = message.from_user.first_name
    bot.send_message(
        message.chat.id,
        f"👋 Чим я можу тобі допомогти,<b> {name}</b>?",
        parse_mode="html",
        reply_markup=generic_markup,
    )


def do_update_schedule(
    message: types.Message,
    bot: TeleBot,
):
    if message.text == "Назад":
        generic(message, bot)
    elif message.text == "Так":
        bot.send_message(
            message.chat.id,
            f"Надішліть фотографію графіку.",
            parse_mode="html",
            reply_markup=cancel,
        )
        bot.register_next_step_handler(message, handle_photos, bot, False)

    elif message.text == "Ні":
        generic(message, bot)
    else:
        bot.send_message(
            message.chat.id,
            f'Не розумію. Оберіть відповідь "Так", "Ні" або "Назад".',
            parse_mode="html",
            reply_markup=generic_choice,
        )


def handle_photos(
    message: types.Message,
    bot: TeleBot,
    is_generic: bool = False,
) -> None:
    bot.user_action_logger.cmd(message, "handle_photos")
    if message.content_type == "photo":
        file_id = message.photo[-1].file_id
        bot.id_storage.save(file_id)

        bot.send_message(
            message.chat.id,
            f"Графік успішно додано.",
            parse_mode="html",
            reply_markup=generic_markup,
        )
        generic(message, bot)
    else:
        if message.text == "Назад":
            generic(message, bot)
        else:
            bot.send_message(
                message.chat.id,
                f"Надішліть коректну фотографію.",
                parse_mode="html",
                reply_markup=cancel,
            )
            bot.register_next_step_handler(message, handle_photos, bot)


def job(bot: TeleBot) -> None:
    if not bot.state_v:
        bot.last_power_on_local = get_unix()
        bot.last_power_off_local = get_unix()
        bot.outages_storage.save(bot.last_power_off, bot.last_power_on_local)
    stats(bot, get_date(-1))


def schedule_loop(bot: TeleBot, run_event: Event) -> None:
    bot.general_logger.init("Schedule loop", True)
    while run_event.is_set():
        schedule.run_pending()
        time.sleep(1)


def stats(bot: TeleBot, date: str = get_date(-1)) -> None:
    data = bot.outages_storage.read()
    if date in data.keys():
        total = 0
        outages = dict(list(data[date].items())[1:]).keys()
        for outage in outages:
            total += bot.outages_storage.lasted(outage, date)

        count = bot.outages_storage.get_outage("outages")
    for user_id in bot.user_storage.read()["outages"]:
        try:
            bot.general_logger.info(f"Notified: {user_id}")
            bot.send_message(
                user_id,
                f"💡 Статистика відключень за {get_date(-1)}: \n\nКількість відключень: {count}\n\nЗагалом світла не було {formatter.format(total)}, що складає {round((total/86400)*100, 1)}% доби",
                parse_mode="html",
                reply_markup=generic_markup,
            )
        except Exception as e:
            bot.general_logger.error(
                f"{e} occured. Take actions regarding this error as soon as possible."
            )
            continue
