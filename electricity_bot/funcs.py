from telebot import TeleBot, types
from electricity_bot.vars import generic_choice, generic_markup, cancel
from electricity_bot.config import ADDRESS
from electricity_bot.time import get_time, get_unix
import electricity_bot.formatter as formatter
from threading import Thread
import time

# from application import Application


def loop(bot: TeleBot, run_event: Thread) -> None:
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
    else:
        bot.state_v = True
        bot.last_power_on = get_unix()

    bot.general_logger.info(
        f"Electricity checker thread initialized. Initial state: {a.result['plugged']}"
    )
    bot.outage_logger.info(
        f"Electricity checker thread initialized. Initial state: {a.result['plugged']}"
    )
    if bot.debug:
        i = 0
    while run_event.is_set():
        if bot.debug:
            i += 1
        time.sleep(10)
        current_time = get_time()
        a = termux_api.battery_status()
        bot.general_logger.debug(f"ECT: Iteration #{i}, state: {a.result['plugged']}")
        if a.result["plugged"] == "UNPLUGGED":
            if bot.state_v != False:
                bot.state_v = False
                bot.last_power_off = get_unix()
                bot.general_logger.info(f"Electricity is out. Notifying users.")
                bot.outage_logger.warning(f"Electricity is out.")
                for user_id in bot.user_storage.read():
                    bot.general_logger.info(f"Notified: {user_id}")
                    bot.send_message(
                        user_id,
                        f"❌ {current_time} - {ADDRESS}, світло вимкнули. Світло було {formatter.format(bot.last_power_off-bot.last_power_on)}",
                        parse_mode="html",
                    )
                bot.general_logger.info(f"Users notified.")
            else:
                continue
        else:
            if bot.state_v != True:
                bot.state_v = True
                bot.last_power_on = get_unix()
                bot.outages_storage.save(bot.last_power_off, bot.last_power_on)
                bot.general_logger.info(f"Electricity is back on. Notifying users.")
                bot.outage_logger.warning(f"Electricity is back on.")
                for user_id in bot.user_storage.read():
                    bot.general_logger.info(f"Notified: {user_id}")
                    bot.send_message(
                        user_id,
                        f"✅ {current_time} - Івасюка 50А, світло увімкнули. Світла не було {formatter.format(bot.last_power_on-bot.last_power_off)}",
                        parse_mode="html",
                    )
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
