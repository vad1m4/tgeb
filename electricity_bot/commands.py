from electricity_bot.config import ADDRESS, GROUP
from electricity_bot.vars import (
    _generic_markup,
    cancel,
    notifications_markup,
    login_markup,
    cancel_str,
    schedules_markup,
    generic_str,
)
from electricity_bot.funcs import generic
from electricity_bot.time import get_date, get_time
from electricity_bot.config import admins as admins_list
from electricity_bot.logger import log_cmd

from telebot import TeleBot, types  # type: ignore

import logging

logger = logging.getLogger("general")
user_logger = logging.getLogger("user_actions")

### User commands


def start(message: types.Message, bot: TeleBot) -> None:
    log_cmd(message, "start")
    name = message.from_user.first_name
    bot.send_message(
        message.chat.id,
        f"👋 Привіт<b> {name}</b>! \n\n💡 Я - ваш персональний помічник, який буде сповіщати вас про відключення електроенергії у будинку {ADDRESS}.\n\nДля початку роботи зі мною, авторизуйтеся за допомогою номеру телефона.\n\n<i>Зверніть увагу: цей бот не є офіційним продуктом ДТЕК чи Львівобленерго та не є офіційним джерелом інформації про енергопостачання.</i>",
        parse_mode="html",
    )
    bot.send_message(
        message.from_user.id,
        "⚠️ <b>Авторизуючись, ви підтверджуєте що ви прочитали наступне:</b>\n\nЦей бот був розроблений ентузіастом для вашої зручності, його основна мета - сповіщати користувачів про фактичні відключення світла.\nБот знаходиться у стані активної розробки. Недоліки, недостовірність інформації, відгуки та побажання можна залишити командою /feedback",
        parse_mode="html",
        reply_markup=login_markup,
    )


def not_authorized(message: types.Message, bot: TeleBot) -> None:
    log_cmd(message, "not authorized")
    bot.send_message(
        message.chat.id,
        f" \n\n❌ Ви не авторизовані. Для початку роботи зі мною, авторизуйтеся за допомогою номеру телефона.",
        parse_mode="html",
        reply_markup=login_markup,
    )


def authorize(message: types.Message, bot: TeleBot) -> None:
    log_cmd(message, "authorize")
    user_id = message.from_user.id
    generic_markup = _generic_markup(bot, message.from_user.id)
    if not bot.user_storage.is_authorized(user_id):
        phone_num = message.contact.phone_number

        if bot.user_storage.authorize(user_id, phone_num):
            logger.info(
                f"Successfully authorised user {message.from_user.first_name} {message.from_user.last_name} via phone number ({phone_num})"
            )
            user_logger.info(
                f"Successfully authorised user {message.from_user.first_name} {message.from_user.last_name} via phone number ({phone_num})"
            )
            bot.user_storage.save(user_id, "stats")
            bot.user_storage.save(user_id, "outages")
            bot.send_message(
                message.chat.id,
                f"✅ Вас було успішно авторизовано за номером телефону {phone_num}. Тепер вам доступні мої функції, наприклад:\n\n- Дізнатися стан світла (/electricitystate)\n\n- Змінити налаштування сповіщень (/notifications)\n\n- Передивитися актуальний графік відключень групи {GROUP} (/seeschedule)\n\n- Залишити відгук (/feedback)",
                parse_mode="html",
            )
            bot.send_message(
                message.from_user.id,
                "🔔 Як нового користувача, вас було автоматично підписано на <b>усі</b> сповіщення.",
                parse_mode="html",
                reply_markup=generic_markup,
            )
        else:
            logger.info(
                f"Failed to authorise user {message.from_user.first_name} {message.from_user.last_name} via phone number ({phone_num}): phone number blacklisted"
            )
            user_logger.info(
                f"Failed to authorise user {message.from_user.first_name} {message.from_user.last_name} via phone number ({phone_num}): phone number blacklisted"
            )
            bot.send_message(
                message.chat.id,
                f"❌ На жаль, номер {phone_num} був заблокований в нашому боті. Причина блокування: {bot.user_storage.why_blacklist(phone_num)}",
                parse_mode="html",
            )
    else:
        bot.send_message(
            message.chat.id,
            f"♻️ Ви вже авторизувалися в нашому боті.",
            parse_mode="html",
            reply_markup=generic_markup,
        )


def handle_other(message: types.Message, bot: TeleBot) -> None:
    log_cmd(message, "handler_other")
    generic_markup = _generic_markup(bot, message.from_user.id)
    bot.send_message(
        message.chat.id,
        f"🤖 Я ще не вмію сприймати такі повідомлення. Щоб мною користуватися, оберіть одну з опцій нижче.",
        parse_mode="html",
        reply_markup=generic_markup,
    )


def subscribe(message: types.Message, bot: TeleBot) -> None:
    log_cmd(message, "subscribe")
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
    log_cmd(message, "notifications")
    markup = notifications_markup(bot, message.from_user.id)
    bot.send_message(
        message.chat.id,
        f"🛠 Ось перелік ваших налаштувань:\n\nВи {'підписані' if bot.user_storage.subscribed(message.from_user.id, 'outages') else 'не підписані'} на сповіщення.\n\nВи {'підписані' if bot.user_storage.subscribed(message.from_user.id, 'stats') else 'не підписані'} на щоденну статистику.",
        parse_mode="html",
        reply_markup=markup,
    )


def unsubscribe(message: types.Message, bot: TeleBot) -> None:
    log_cmd(message, "unsubscribe")
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
    log_cmd(message, "subscribe_stats")
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
    log_cmd(message, "unsubscribe_stats")
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
    generic_markup = _generic_markup(bot, message.from_user.id)
    log_cmd(message, "state")
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


def _see_schedule(message: types.Message, bot: TeleBot) -> None:
    log_cmd(message, "see_schedule 1")
    markup = schedules_markup(bot.id_storage.exists(get_date(1)))
    bot.send_message(
        message.from_user.id,
        f"Оберіть дату.",
        parse_mode="html",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, see_schedule, bot)


def see_schedule(message: types.Message, bot: TeleBot) -> None:
    generic_markup = _generic_markup(bot, message.from_user.id)
    log_cmd(message, "see_schedule 2")
    schedule = message.text
    if schedule == cancel_str:
        generic(message, bot)
    else:
        if schedule == generic_str:
            schedule = "generic"
        if bot.id_storage.exists(schedule):
            date = schedule if schedule != "generic" else get_date()
            bot.send_photo(
                message.chat.id,
                bot.id_storage.get_schedule(schedule),
                parse_mode="html",
                reply_markup=generic_markup,
                caption=f"💡 Графік відключень світла на {date}.\n\n<i>Неправильний графік? Ви можете залишити відгук</i>",
            )
        else:
            bot.send_message(
                message.chat.id,
                f"❌ На жаль, графіку відключень світла немає. Якщо проблема продовжиться, залиште відгук.",
                parse_mode="html",
                reply_markup=generic_markup,
            )


def _feedback(message: types.Message, bot: TeleBot) -> None:
    bot.send_message(
        message.chat.id,
        f"📲 Чудово! Напищіть ваш відгук у наступному повідомленні.",
        parse_mode="html",
        reply_markup=cancel,
    )
    bot.register_next_step_handler(message, feedback, bot)


def feedback(message: types.Message, bot: TeleBot) -> None:
    if message.text == cancel_str:
        generic(message, bot)
    else:
        bot.send_message(
            message.from_user.id,
            f"✅ Відгук успішно залишено!",
            parse_mode="html",
        )
        generic(message, bot)
        bot.send_message(
            admins_list[0],
            f'❕ {message.from_user.first_name} {message.from_user.last_name} [{message.from_user.id}] залишили відгук!\n\n"{message.text}"',
            parse_mode="html",
        )
