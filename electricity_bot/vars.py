from telebot import types, TeleBot
from electricity_bot.config import GROUP
from electricity_bot.time import get_date

subscribe_str = "Підписатися на сповіщення"
unsubscribe_str = "Відписатися від сповіщень"
subscribe_stats_str = "Підписатися на щоденну статистику"
unsubscribe_stats_str = "Відписатися від щоденної статистики"


state_str = "Який стан світла?"
schedule_str = f"Графік відключень групи {GROUP}"
notifications_str = "Сповіщення"

generic_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
notifications = types.KeyboardButton(notifications_str)
state = types.KeyboardButton(state_str)
schedule = types.KeyboardButton(schedule_str)
generic_markup.add(state, notifications, schedule)


def notifications_markup(bot: TeleBot, user_id: int) -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    if not bot.user_storage.subscribed(user_id, "outages"):
        generic = types.KeyboardButton(str(subscribe_str))
    else:
        generic = types.KeyboardButton(str(unsubscribe_str))
    if not bot.user_storage.subscribed(user_id, "stats"):
        stats = types.KeyboardButton(str(subscribe_stats_str))
    else:
        stats = types.KeyboardButton(str(unsubscribe_stats_str))

    return markup.add(generic, stats, cancel_b)


def schedules_markup(bot: TeleBot) -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    today = types.KeyboardButton(str(get_date()))
    tomorrow = types.KeyboardButton(str(get_date(1)))

    return markup.add(today, tomorrow)


none = types.ReplyKeyboardRemove()

cancel_str = "Назад"

cancel = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
cancel_b = types.KeyboardButton(cancel_str)
cancel.add(cancel_b)

yes_str = "Так"
no_str = "Ні"

generic_choice = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
yes = types.KeyboardButton(yes_str)
no = types.KeyboardButton(no_str)
generic_choice.add(yes, no, cancel_b)
