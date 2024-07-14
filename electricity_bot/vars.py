from telebot import types, TeleBot  # type: ignore

from electricity_bot.config import GROUP
from electricity_bot.time import get_date

subscribe_str: str = "Підписатися на сповіщення"
unsubscribe_str: str = "Відписатися від сповіщень"
subscribe_stats_str: str = "Підписатися на щоденну статистику"
unsubscribe_stats_str: str = "Відписатися від щоденної статистики"


state_str: str = "Який стан світла?"
schedule_str: str = f"Графік відключень групи {GROUP}"
notifications_str: str = "Сповіщення"
admin_str: str = "Меню адміна"
feedback_str: str = "Залишити відгук"


def _generic_markup(bot: TeleBot, user_id: int) -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    notifications = types.KeyboardButton(str(notifications_str))
    state = types.KeyboardButton(str(state_str))
    schedule = types.KeyboardButton(str(schedule_str))
    feedback = types.KeyboardButton(str(feedback_str))
    if bot.is_admin(user_id):
        admin = types.KeyboardButton(str(admin_str))
        return markup.add(state, notifications, schedule, admin, feedback)
    return markup.add(state, notifications, schedule, feedback)


def notifications_markup(bot: TeleBot, user_id: int) -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if not bot.user_storage.subscribed(user_id, "outages"):
        generic = types.KeyboardButton(str(subscribe_str))
    else:
        generic = types.KeyboardButton(str(unsubscribe_str))
    if not bot.user_storage.subscribed(user_id, "stats"):
        stats = types.KeyboardButton(str(subscribe_stats_str))
    else:
        stats = types.KeyboardButton(str(unsubscribe_stats_str))

    return markup.add(generic, stats, cancel_b)


generic_str = "Загальний"


def schedules_markup(_tomorrow: bool = False) -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    today = types.KeyboardButton(str(get_date()))
    generic = types.KeyboardButton(generic_str)
    if _tomorrow:
        tomorrow = types.KeyboardButton(str(get_date(1)))
        return markup.add(today, tomorrow, generic)
    return markup.add(today, generic)


none: types.ReplyKeyboardRemove = types.ReplyKeyboardRemove()

cancel_str: str = "Назад"

cancel: types.ReplyKeyboardMarkup = types.ReplyKeyboardMarkup(
    resize_keyboard=True, row_width=1
)
cancel_b = types.KeyboardButton(cancel_str)
cancel.add(cancel_b)

yes_str: str = "Так"
no_str: str = "Ні"

generic_choice: types.ReplyKeyboardMarkup = types.ReplyKeyboardMarkup(
    resize_keyboard=True, row_width=2
)
yes = types.KeyboardButton(yes_str)
no = types.KeyboardButton(no_str)
generic_choice.add(yes, no, cancel_b)

login_str: str = "Авторизуватися"

login_markup: types.ReplyKeyboardMarkup = types.ReplyKeyboardMarkup(
    resize_keyboard=True, row_width=1
)
login = types.KeyboardButton(text=login_str, request_contact=True)
login_markup.add(login)

add_schedule_str: str = "Додати графік"
scrape_str: str = "Дістати графік з сайту"
current_date_str: str = "Сьогоднішня дата"
blacklist_str: str = "Заблокувати номер"
unblacklist_str: str = "Розблокувати номер"
announcement_str: str = "Оголошення"
stats_str: str = "Статистика"

admin_markup: types.ReplyKeyboardMarkup = types.ReplyKeyboardMarkup(
    resize_keyboard=True, row_width=2
)
add_schedule = types.KeyboardButton(add_schedule_str)
scrape = types.KeyboardButton(scrape_str)
current_date = types.KeyboardButton(current_date_str)
blacklist = types.KeyboardButton(blacklist_str)
unblacklist = types.KeyboardButton(unblacklist_str)
announcement = types.KeyboardButton(announcement_str)
stats = types.KeyboardButton(stats_str)
admin_markup.add(
    add_schedule, scrape, blacklist, unblacklist, announcement, stats, cancel_b
)

outages_group_str: str = "Відключення"
stats_group_str: str = "Статистика"
all_str: str = "Всім користувачам"

group_choice: types.ReplyKeyboardMarkup = types.ReplyKeyboardMarkup(
    resize_keyboard=True, row_width=3
)
outages_group = types.KeyboardButton(outages_group_str)
stats_group = types.KeyboardButton(stats_group_str)
_all = types.KeyboardButton(stats_group_str)
group_choice.add(outages_group, stats_group, _all, cancel_b)
