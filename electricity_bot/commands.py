from threading import Thread
import time
from electricity_bot.config import ADDRESS
from electricity_bot.vars import generic_markup, cancel, generic_choice
from electricity_bot.time import get_date, get_time
from electricity_bot import termux_api
from telebot import TeleBot, types

# import random


# def termux_apibattery_status():
#     states = ["PLUGGED", "UNPLUGGED"]
#     result = random.randint(0, 1)
#     print(states[result])
#     return {"plugged": states[result]}


def loop(bot: TeleBot, run_event: Thread) -> None:

    a = termux_api.battery_status()
    if a.result["plugged"] == "UNPLUGGED":
        bot.state_v = False
    else:
        bot.state_v = True

    bot.general_logger.info(
        f"Electricity checker thread initialized. Initial state: {a['plugged']}"
    )
    bot.outage_logger.info(
        f"Electricity checker thread initialized. Initial state: {a['plugged']}"
    )
    while run_event.is_set():
        time.sleep(10)
        current_time = get_time()
        a = termux_api.battery_status()
        if a.result["plugged"] == "UNPLUGGED":
            if bot.state_v != False:
                bot.state_v = False
                bot.general_logger.info(f"Electricity is out. Notifying users.")
                bot.outage_logger.warning(f"Electricity is out.")
                for user_id in bot.user_storage.read():
                    bot.general_logger.info(f"Notified: {user_id}")
                    bot.send_message(
                        user_id,
                        f"❌ {current_time} - {ADDRESS}, світло вимкнули.",
                        parse_mode="html",
                    )
                bot.general_logger.info(f"Users notified.")
            else:
                continue
        else:
            if bot.state_v != True:
                bot.state_v = True
                bot.general_logger.info(f"Electricity is back on. Notifying users.")
                bot.outage_logger.warning(f"Electricity is back on.")
                for user_id in bot.user_storage.read():
                    bot.general_logger.info(f"Notified: {user_id}")
                    bot.send_message(
                        user_id,
                        f"✅ {current_time} - Івасюка 50А, світло увімкнули.",
                        parse_mode="html",
                    )
                bot.general_logger.info(f"Users notified.")
            else:
                continue


def start(message: types.Message, bot: TeleBot) -> None:
    bot.user_action_logger.cmd(message, "start")
    name = message.from_user.first_name
    if name.lower() == "group":
        bot.send_message(
            message.chat.id,
            f"👋 Привіт<b> всім</b>! \n\n💡 Я - ваш персональний помічник, який буде сповіщати вас про відключення електроенергії у будинку {ADDRESS}. Мене можна додати в групи або підписатися на сповіщення в особистих повідомленнях.",
            parse_mode="html",
            reply_markup=generic_markup,
        )
    else:
        bot.send_message(
            message.chat.id,
            f"👋 Привіт,<b> {name}</b>! \n\n💡 Я - твій персональний помічник, який буде тебе сповіщати про відключення електроенергії у будинку {ADDRESS}. Мене можна додати в групи або підписатися на сповіщення в особистих повідомленнях.",
            parse_mode="html",
            reply_markup=generic_markup,
        )


def generic(message: types.Message, bot: TeleBot) -> None:
    name = message.from_user.first_name
    bot.send_message(
        message.chat.id,
        f"👋 Чим я можу тобі допомогти,<b> {name}</b>?",
        parse_mode="html",
        reply_markup=generic_markup,
    )


def handle_other(message: types.Message, bot: TeleBot) -> None:
    bot.send_message(
        message.chat.id,
        f"Я ще не вмію сприймати такі повідомлення. Щоб мною користуватися, оберіть одну з опцій нижче.",
        parse_mode="html",
        reply_markup=generic_markup,
    )


def subscribe(message: types.Message, bot: TeleBot) -> None:
    bot.user_action_logger.cmd(message, "subscribe")
    if not bot.user_storage.subscribed(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "🔔 Ви <b>успішно</b> підписалися на сповіщення!",
            parse_mode="html",
            reply_markup=generic_markup,
        )
        bot.user_storage.save(message.chat.id)
    else:
        bot.send_message(
            message.chat.id,
            "🔔 Ви <b>вже</b> підписані на сповіщення.",
            parse_mode="html",
            reply_markup=generic_markup,
        )


def unsubscribe(message: types.Message, bot: TeleBot) -> None:
    bot.user_action_logger.cmd(message, "unsubscribe")
    if bot.user_storage.subscribed(message.from_user.id):
        bot.user_storage.delete(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "🔕 Ви <b>успішно</b> відписалися від сповіщень!",
            parse_mode="html",
            reply_markup=generic_markup,
        )
    else:
        bot.send_message(
            message.chat.id,
            "🔕 Ви <b>не</b> підписані на сповіщення.",
            parse_mode="html",
            reply_markup=generic_markup,
        )


def state(message: types.Message, bot: TeleBot) -> None:
    bot.user_action_logger.cmd(message, "state")
    current_time = get_time()
    if bot.state_v == True:
        bot.send_message(
            message.chat.id,
            f"✅ Станом на {current_time} за адресою {ADDRESS} світло <b>є</b>.",
            parse_mode="html",
            reply_markup=generic_markup,
        )
    else:
        bot.send_message(
            message.chat.id,
            f"❌ Станом на {current_time} за адресою {ADDRESS} світла <b>нема</b>.",
            parse_mode="html",
            reply_markup=generic_markup,
        )


def see_schedule(message: types.Message, bot: TeleBot) -> None:
    bot.user_action_logger.cmd(message, "see_schedule")
    if bot.id_storage.exists():
        bot.send_photo(
            message.chat.id,
            bot.id_storage.get_schedule(),
            parse_mode="html",
            reply_markup=generic_markup,
            caption=f"Графік відключень світла на {get_date()}",
        )
    elif bot.id_storage.exists("generic"):
        bot.send_photo(
            message.chat.id,
            bot.id_storage.get_schedule("generic"),
            parse_mode="html",
            reply_markup=generic_markup,
            caption=f"Графік відключень світла на {get_date()}",
        )
    else:
        bot.send_message(
            message.chat.id,
            f"На жаль, графіку відключень світла немає. Якщо проблема продовжиться, залиште відгук.",
            parse_mode="html",
            reply_markup=generic_markup,
        )


def add_schedule(
    message: types.Message,
    bot: TeleBot,
    generic: bool,
) -> None:
    bot.user_action_logger.cmd(message, "add_schedule")
    if bot.is_admin(message):
        if generic:
            bot.send_message(
                message.chat.id,
                f"Надішліть фотографію графіку.",
                parse_mode="html",
                reply_markup=cancel,
            )
            bot.register_next_step_handler(message, handle_photos, bot, generic)
        else:
            if bot.id_storage.exists():
                bot.send_message(
                    message.chat.id,
                    f"Графік за сьогодні вже було додано. Оновити його?",
                    parse_mode="html",
                    reply_markup=generic_choice,
                )
                bot.register_next_step_handler(message, do_update_schedule, bot)
            else:
                bot.send_message(
                    message.chat.id,
                    f"Надішліть фотографію графіку.",
                    parse_mode="html",
                    reply_markup=cancel,
                )
                bot.register_next_step_handler(message, handle_photos, bot, generic)
    else:
        bot.send_message(
            message.chat.id,
            f"❌ Ви не є адміном цього бота.",
            parse_mode="html",
            reply_markup=generic_markup,
        )


def do_update_schedule(
    message: types.Message,
    bot: TeleBot,
):
    if message.text == "Назад":
        generic()
    elif message.text == "Так":
        bot.send_message(
            message.chat.id,
            f"Надішліть фотографію графіку.",
            parse_mode="html",
            reply_markup=cancel,
        )
        bot.register_next_step_handler(message, handle_photos, bot, False)

    elif message.text == "Ні":
        generic()
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
        generic()
    else:
        if message.text == "Назад":
            generic()
        else:
            bot.send_message(
                message.chat.id,
                f"Надішліть коректну фотографію.",
                parse_mode="html",
                reply_markup=cancel,
            )
            bot.register_next_step_handler(message, handle_photos, bot)
