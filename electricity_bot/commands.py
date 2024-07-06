from electricity_bot.config import ADDRESS
from electricity_bot.vars import (
    generic_markup,
    cancel,
    generic_choice,
    notifications_markup,
    schedules_markup,
)
from electricity_bot.time import get_date, get_time
from electricity_bot.funcs import handle_photos, do_update_schedule
from electricity_bot.funcs import add_schedule as _add_schedule
from telebot import TeleBot, types


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


def handle_other(message: types.Message, bot: TeleBot) -> None:
    bot.send_message(
        message.chat.id,
        f"Я ще не вмію сприймати такі повідомлення. Щоб мною користуватися, оберіть одну з опцій нижче.",
        parse_mode="html",
        reply_markup=generic_markup,
    )


def subscribe(message: types.Message, bot: TeleBot) -> None:
    bot.user_action_logger.cmd(message, "subscribe")
    if not bot.user_storage.subscribed(message.from_user.id, "outages"):
        bot.user_storage.save(message.chat.id, "outages")
        markup = notifications_markup(bot, message.from_user.id)
        bot.send_message(
            message.chat.id,
            "🔔 Ви <b>успішно</b> підписалися на сповіщення!",
            parse_mode="html",
            reply_markup=markup,
        )
    else:
        markup = notifications_markup(bot, message.from_user.id)
        bot.send_message(
            message.chat.id,
            "🔔 Ви <b>вже</b> підписані на сповіщення.",
            parse_mode="html",
            reply_markup=markup,
        )


def notifications(message: types.Message, bot: TeleBot) -> None:
    bot.user_action_logger.cmd(message, "notifications")
    markup = notifications_markup(bot, message.from_user.id)
    bot.send_message(
        message.chat.id,
        f"Ось перелік ваших налаштувань:\n\nВи {'підписані' if bot.user_storage.subscribed(message.from_user.id, 'outages') else 'не підписані'} на сповіщення.\n\nВи {'підписані' if bot.user_storage.subscribed(message.from_user.id, 'stats') else 'не підписані'} на щоденну статистику.",
        parse_mode="html",
        reply_markup=markup,
    )


def unsubscribe(message: types.Message, bot: TeleBot) -> None:
    bot.user_action_logger.cmd(message, "unsubscribe")
    if bot.user_storage.subscribed(message.from_user.id, "outages"):
        bot.user_storage.delete(message.from_user.id, "outages")
        markup = notifications_markup(bot, message.from_user.id)
        bot.send_message(
            message.chat.id,
            "🔕 Ви <b>успішно</b> відписалися від сповіщень!",
            parse_mode="html",
            reply_markup=markup,
        )
    else:
        markup = notifications_markup(bot, message.from_user.id)
        bot.send_message(
            message.chat.id,
            "🔕 Ви <b>не</b> підписані на сповіщення.",
            parse_mode="html",
            reply_markup=markup,
        )


def subscribe_stats(message: types.Message, bot: TeleBot) -> None:
    bot.user_action_logger.cmd(message, "subscribe_stats")
    if not bot.user_storage.subscribed(message.from_user.id, "stats"):
        bot.user_storage.save(message.chat.id, "stats")
        markup = notifications_markup(bot, message.from_user.id)
        bot.send_message(
            message.chat.id,
            "🔔 Ви <b>успішно</b> підписалися на щоденну статистику!",
            parse_mode="html",
            reply_markup=markup,
        )
    else:
        markup = notifications_markup(bot, message.from_user.id)
        bot.send_message(
            message.chat.id,
            "🔔 Ви <b>вже</b> підписані на щоденну статистику.",
            parse_mode="html",
            reply_markup=markup,
        )


def unsubscribe_stats(message: types.Message, bot: TeleBot) -> None:
    markup = notifications_markup(bot, message.from_user.id)
    bot.user_action_logger.cmd(message, "unsubscribe_stats")
    if bot.user_storage.subscribed(message.from_user.id, "stats"):
        bot.user_storage.delete(message.from_user.id, "stats")
        markup = notifications_markup(bot, message.from_user.id)
        bot.send_message(
            message.chat.id,
            "🔕 Ви <b>успішно</b> відписалися від щоденної статистики!",
            parse_mode="html",
            reply_markup=markup,
        )
    else:
        markup = notifications_markup(bot, message.from_user.id)
        bot.send_message(
            message.chat.id,
            "🔕 Ви <b>не</b> підписані на щоденну статистику.",
            parse_mode="html",
            reply_markup=markup,
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
            caption=f"Графік відключень світла на {get_date()}.",
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
    generic: bool = False,
) -> None:
    bot.user_action_logger.cmd(message, "add_schedule")
    if generic:
        bot.send_message(
            message.chat.id,
            f"Надішліть фотографію графіку.",
            parse_mode="html",
            reply_markup=cancel,
        )
        bot.register_next_step_handler(message, handle_photos, bot, generic)
    else:
        markup = schedules_markup(bot)
        bot.send_message(
            message.chat.id,
            f"Оберіть дату.",
            parse_mode="html",
            reply_markup=markup,
        )
        bot.register_next_step_handler(message, _add_schedule, bot)


def current_date(message: types.Message, bot: TeleBot):
    if bot.is_admin(message):
        bot.send_message(
            message.chat.id,
            f"Сьогоднішня дата: {get_date()} {get_time()}",
            parse_mode="html",
            reply_markup=generic_markup,
        )
    else:
        bot.send_message(
            message.chat.id,
            f"❌ Ви не є адміном цього бота.",
            parse_mode="html",
            reply_markup=generic_markup,
        )
