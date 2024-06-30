from telebot import types
from electricity_bot.config import GROUP
from datetime import datetime

subscribe_str = "Підписатися на сповіщення"
unsubscribe_str = "Відписатися від сповіщень"
state_str = "Який стан світла?"
schedule_str = f"Графік відключень групи {GROUP}"

generic_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
subscribe = types.KeyboardButton(subscribe_str)
unsubscribe = types.KeyboardButton(unsubscribe_str)
state = types.KeyboardButton(state_str)
schedule = types.KeyboardButton(schedule_str)
generic_markup.add(subscribe, unsubscribe, state, schedule)

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