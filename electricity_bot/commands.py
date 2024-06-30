from threading import Thread
import time
from datetime import datetime
from electricity_bot.config import ADDRESS
from electricity_bot.vars import generic, none, cancel, generic_choice
from telebot import TeleBot, types
import random
import os.path


def termux_apibattery_status():
    states = ["PLUGGED", "UNPLUGGED"]
    result = random.randint(0, 1)
    print(states[result])
    return {"plugged": states[result]}


def loop(bot: TeleBot, run_event: Thread) -> None:
    print("Script is up and running")
    while run_event.is_set():
        time.sleep(10)
        a = termux_apibattery_status()
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        print(current_time)
        if a["plugged"] == "UNPLUGGED":
            if bot.state_v != False:
                bot.state_v = False
                for user_id in bot.storage.read():
                    bot.send_message(
                        user_id,
                        f"❌ {current_time} - {ADDRESS}, світло вимкнули.",
                        parse_mode="html",
                    )
            else:
                continue
        else:
            if bot.state_v != True:
                bot.state_v = True
                for user_id in bot.storage.read():
                    bot.send_message(
                        user_id,
                        f"✅ {current_time} - Івасюка 50А, світло увімкнули.",
                        parse_mode="html",
                    )
            else:
                continue


def start(message: types.Message, bot: TeleBot) -> None:
    name = message.from_user.first_name
    if name.lower() == "group":
        bot.send_message(
            message.chat.id,
            f"👋 Привіт<b> всім</b>! \n\n💡 Я - ваш персональний помічник, який буде сповіщати вас про відключення електроенергії у будинку {ADDRESS}. Мене можна додати в групи або підписатися на сповіщення в особистих повідомленнях.",
            parse_mode="html",
            reply_markup=generic,
        )
    else:
        bot.send_message(
            message.chat.id,
            f"👋 Привіт,<b> {name}</b>! \n\n💡 Я - твій персональний помічник, який буде тебе сповіщати про відключення електроенергії у будинку {ADDRESS}. Мене можна додати в групи або підписатися на сповіщення в особистих повідомленнях.",
            parse_mode="html",
            reply_markup=generic,
        )


def generic(message: types.Message, bot: TeleBot) -> None:
    name = message.from_user.first_name
    bot.send_message(
        message.chat.id,
        f"👋 Чим я можу тобі допомогти,<b> {name}</b>?",
        parse_mode="html",
        reply_markup=generic,
    )


def handle_other(message: types.Message, bot: TeleBot) -> None:
    bot.send_message(
        message.chat.id,
        f"Я ще не вмію сприймати такі повідомлення. Щоб мною користуватися, оберіть одну з опцій нижче.",
        parse_mode="html",
        reply_markup=generic,
    )


def subscribe(message: types.Message, bot: TeleBot) -> None:
    if not bot.storage.subscribed(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "🔔 Ви <b>успішно</b> підписалися на сповіщення!",
            parse_mode="html",
            reply_markup=generic,
        )
        bot.storage.save(message.chat.id)
    else:
        bot.send_message(
            message.chat.id,
            "🔔 Ви <b>вже</b> підписані на сповіщення.",
            parse_mode="html",
            reply_markup=generic,
        )


def unsubscribe(message: types.Message, bot: TeleBot) -> None:
    if bot.storage.subscribed(message.from_user.id):
        bot.storage.delete(message.from_user.id)
        bot.send_message(
            message.chat.id,
            "🔕 Ви <b>успішно</b> відписалися від сповіщень!",
            parse_mode="html",
            reply_markup=generic,
        )
    else:
        bot.send_message(
            message.chat.id,
            "🔕 Ви <b>не</b> підписані на сповіщення.",
            parse_mode="html",
            reply_markup=generic,
        )


def state(message: types.Message, bot: TeleBot) -> None:
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    if bot.state_v == True:
        bot.send_message(
            message.chat.id,
            f"✅ Станом на {current_time} за адресою {ADDRESS} світло <b>є</b>.",
            parse_mode="html",
            reply_markup=generic,
        )
    else:
        bot.send_message(
            message.chat.id,
            f"❌ Станом на {current_time} за адресою {ADDRESS} світла <b>нема</b>.",
            parse_mode="html",
            reply_markup=generic,
        )


def add_schedule(message: types.Message, bot: TeleBot, generic: bool) -> None:
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
            current_datetime = datetime.now()
            filename = "schedule/" + current_datetime.strftime("%d-%m-%Y") + ".jpg"
            if filename.exists():
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
            f"❌ Ви не є адміном цього бота.",
            parse_mode="html",
            reply_markup=generic,
        )


def do_update_schedule(message: types.Message, bot: TeleBot):
    if message.text == "Назад":
        bot.generic()
    elif message.text == "Так":
        bot.send_message(
            message.chat.id,
            f"Надішліть фотографію графіку.",
            parse_mode="html",
            reply_markup=cancel,
        )
        bot.register_next_step_handler(message, handle_photos, bot, False)

    elif message.text == "Ні":
        bot.generic()
    else:
        bot.send_message(
            message.chat.id,
            f'Не розумію. Оберіть відповідь "Так", "Ні" або "Назад".',
            parse_mode="html",
            reply_markup=generic_choice,
        )


def handle_photos(message: types.Message, bot: TeleBot, generic: bool) -> None:
    if message.content_type == "photo":
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        current_datetime = datetime.now()
        filename = current_datetime.strftime("%d-%m-%Y") + ".jpg"
        with open(filename, "wb") as new_file:
            new_file.write(downloaded_file)

        bot.send_message(
            message.chat.id,
            f"Графік успішно додано",
            parse_mode="html",
            reply_markup=cancel,
        )
    else:
        if message.text == "Назад":
            bot.generic()
        else:
            bot.send_message(
                message.chat.id,
                f"Надішліть коректну фотографію.",
                parse_mode="html",
                reply_markup=cancel,
            )
            bot.register_next_step_handler(message, handle_photos, bot)
