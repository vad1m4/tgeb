from telebot import types, TeleBot, apihelper  # type: ignore

from electricity_bot.vars import (
    cancel,
    schedules_markup,
    generic_choice,
    admin_markup,
    group_choice,
    stats_group_str,
    outages_group_str,
    all_str,
    cancel_str,
    no_str,
    yes_str,
    generic_str,
    group_dict,
)
from electricity_bot.time import get_date, get_time
from electricity_bot.logger import log_cmd
from electricity_bot.funcs import notify

import logging

import os
from pathlib import Path

logger = logging.getLogger("general")
user_logger = logging.getLogger("user_actions")


def not_admin(message: types.Message, bot: TeleBot) -> None:
    log_cmd(message, "not_admin")
    bot.send_message(
        message.from_user.id,
        f" \n\n❌ Ви не є адміном цього бота.",
        parse_mode="html",
    )


def menu(data: types.Message, bot: TeleBot) -> None:
    if isinstance(data, types.Message):
        from_user = data.from_user
    else:
        from_user = data
    log_cmd(from_user, "admin menu")
    bot.send_message(
        from_user.id,
        f"💻 Оберіть одну з опцій.",
        parse_mode="html",
        reply_markup=admin_markup,
    )


def _blacklist_(message: types.Message, bot: TeleBot) -> None:
    log_cmd(message, "blacklist 1")
    bot.send_message(
        message.from_user.id,
        f"🤖 Введіть номер або User ID користувача, якого ви хочете заблокувати.",
        parse_mode="html",
        reply_markup=cancel,
    )
    bot.register_next_step_handler(message, _blacklist, bot)


def _blacklist(message: types.Message, bot: TeleBot) -> None:
    log_cmd(message, "blacklist 2")
    try:
        if message.text[0] == "+":
            number = message.text
        else:
            number = int(message.text)
        bot.send_message(
            message.from_user.id,
            f"❌ Напишіть причину блокування:",
            parse_mode="html",
            reply_markup=cancel,
        )
        bot.register_next_step_handler(message, blacklist, bot, number)
    except:
        bot.send_message(
            message.from_user.id,
            f"❌ {number} не є коректним номером або Telegram ID",
            parse_mode="html",
            reply_markup=cancel,
        )
        bot.register_next_step_handler(message, _blacklist, bot)


def blacklist(message: types.Message, bot: TeleBot, number: int | str) -> None:
    log_cmd(message, "blacklist 3")
    bot.user_storage.blacklist(number, message.text)
    user_logger.info(
        f"Admin {message.from_user.first_name} {message.from_user.last_name} [{message.from_user.id}] blocked {number}, reason: {message.text}"
    )
    logger.info(
        f"Admin {message.from_user.first_name} {message.from_user.last_name} [{message.from_user.id}] blocked {number}, reason: {message.text}"
    )
    bot.send_message(
        message.from_user.id,
        f"✅ Успішно заблоковано {number}",
        parse_mode="html",
        reply_markup=admin_markup,
    )


def _unblacklist(message: types.Message, bot: TeleBot) -> None:
    log_cmd(message, "unblacklist 1")
    bot.send_message(
        message.from_user.id,
        f"🤖 Введіть номер або User ID користувача, якого ви хочете розблокувати.",
        parse_mode="html",
        reply_markup=cancel,
    )
    bot.register_next_step_handler(message, unblacklist, bot)


def unblacklist(message: types.Message, bot: TeleBot) -> None:
    log_cmd(message, "unblacklist 2")
    number = message.text
    if bot.user_storage.unblacklist(number):
        bot.send_message(
            message.from_user.id,
            f"✅ Успішно розблоковано {number}",
            parse_mode="html",
            reply_markup=admin_markup,
        )
        user_logger.info(
            f"Admin {message.from_user.first_name} {message.from_user.last_name} [{message.from_user.id}] unblocked {number}"
        )
        logger.info(
            f"Admin {message.from_user.first_name} {message.from_user.last_name} [{message.from_user.id}] unblocked {number}"
        )
    else:
        bot.send_message(
            message.from_user.id,
            f"❌ {number} не є заблокованим.",
            parse_mode="html",
            reply_markup=admin_markup,
        )


def current_date(message: types.Message, bot: TeleBot) -> None:
    log_cmd(message, "current_date")
    bot.send_message(
        message.from_user.id,
        f"📅 Сьогоднішня дата: {get_date()} {get_time()}",
        parse_mode="html",
        reply_markup=admin_markup,
    )


def add_schedule(
    message: types.Message,
    bot: TeleBot,
) -> None:
    log_cmd(message, "add_schedule 1")
    markup = schedules_markup(True)
    bot.send_message(
        message.from_user.id,
        f"Оберіть дату.",
        parse_mode="html",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, _add_schedule, bot)


def _add_schedule(
    message: types.Message,
    bot: TeleBot,
) -> None:
    log_cmd(message, "add_schedule 2")
    schedule = message.text
    if schedule == cancel_str:
        menu(message, bot)
    else:
        if schedule == generic_str:
            schedule = "generic"

        if bot.id_storage.exists(schedule):
            bot.send_message(
                message.from_user.id,
                f"🤖 Цей графік вже було додано. Оновити його?",
                parse_mode="html",
                reply_markup=generic_choice,
            )
            bot.register_next_step_handler(message, do_update_schedule, bot, schedule)
        else:
            bot.send_message(
                message.from_user.id,
                f"🤖 Надішліть фотографію графіку.",
                parse_mode="html",
                reply_markup=cancel,
            )
            bot.register_next_step_handler(message, handle_photos, bot, schedule)


def do_update_schedule(message: types.Message, bot: TeleBot, date: None) -> None:
    log_cmd(message, "do_update_schedule")
    if message.text == cancel_str or message.text == no_str:
        menu(message, bot)
    elif message.text == yes_str:
        bot.send_message(
            message.from_user.id,
            f"🛠 Надішліть фотографію графіку.",
            parse_mode="html",
            reply_markup=cancel,
        )
        bot.register_next_step_handler(message, handle_photos, bot, date)
    else:
        bot.send_message(
            message.from_user.id,
            f'🤖 Не розумію. Оберіть відповідь "{yes_str}", "{no_str}" або "{cancel_str}".',
            parse_mode="html",
            reply_markup=generic_choice,
        )
        bot.register_next_step_handler(message, do_update_schedule, bot, message.text)


def handle_photos(
    message: types.Message,
    bot: TeleBot,
    date: str = None,
) -> None:
    if date == None:
        date = get_date()
    log_cmd(message, "handle_photos")
    if message.content_type == "photo":
        file_id = message.photo[-1].file_id
        bot.id_storage.save(file_id, date)

        bot.send_message(
            message.from_user.id,
            f"✅ Графік успішно додано.",
            parse_mode="html",
            reply_markup=admin_markup,
        )
        menu(message, bot)
    else:
        if message.text == cancel_str:
            menu(message, bot)
        else:
            bot.send_message(
                message.from_user.id,
                f"🤖 Надішліть коректну фотографію.",
                parse_mode="html",
                reply_markup=cancel,
            )
            bot.register_next_step_handler(message, handle_photos, bot)


def _announce_(message: types.Message, bot: TeleBot) -> None:
    log_cmd(message, "announce 1")
    bot.send_message(
        message.from_user.id,
        f"📲 Оберіть групу користувачів, для яких ви хочете створити оголошення.",
        parse_mode="html",
        reply_markup=group_choice,
    )
    bot.register_next_step_handler(message, _announce, bot)


def _announce(message: types.Message, bot: TeleBot):
    log_cmd(message, "announce 2")
    if message.text == cancel_str:
        menu(message, bot)
    elif message.text in [outages_group_str, stats_group_str, all_str]:
        group = group_dict[message.text]
        bot.send_message(
            message.from_user.id,
            f"⌨️ Тепер напишіть ваше оголошення.",
            parse_mode="html",
            reply_markup=cancel,
        )
        # logger.info(group)
        bot.register_next_step_handler(message, announce, bot, group)
    else:
        bot.send_message(
            message.from_user.id,
            f'🤖 Не розумію. Оберіть відповідь "{outages_group_str}", "{stats_group_str}" або "{cancel_str}".',
            parse_mode="html",
            reply_markup=group_choice,
        )
        bot.register_next_step_handler(message, _announce, bot)


def announce(message: types.Message, bot: TeleBot, group: str):
    log_cmd(message, "announce 3")
    if message.text == cancel_str:
        menu(message, bot)
    else:
        logger.info(
            f"Admin {message.from_user.first_name} {message.from_user.last_name} [{message.from_user.id}] announced to {group}, text: {message.text}"
        )
        user_logger.info(
            f"Admin {message.from_user.first_name} {message.from_user.last_name} [{message.from_user.id}] announced to {group}, text: {message.text}"
        )
        if group == "users":
            group_list = list(bot.user_storage.read()[group].keys())[1:]
        else:
            group_list = bot.user_storage.read()[group]
        notify(bot, group_list, f"⚠️ Оголошення від адміністратора:\n\n{message.text}")
        bot.send_message(
            message.from_user.id,
            f"✅ {len(group_list)} отримали ваше оголошення.",
            parse_mode="html",
            reply_markup=admin_markup,
        )

        menu(message, bot)


def logs_menu(bot: TeleBot, message: types.Message):
    log_cmd(message, "logs_menu")
    # filenames = [:10]
    # search_dir = "/mydir/"
    os.chdir("general_logs/")
    filenames = os.listdir()
    # files = [os.path.join(search_dir, f) for f in files] # add path to each file
    filenames.sort(key=lambda x: os.path.getmtime(x))
    filenames.reverse()
    filenames = filenames[:30]
    if len(filenames) > 0:
        formatted_filenames = []
        for i, filename in enumerate(filenames, start=1):
            stripped_filename = filename.removeprefix("bot_").removesuffix(".txt")
            new_filename = f"{stripped_filename}_new.txt"
            formatted_filenames.append(f"{i}. {new_filename}")
        message_text = (
            "\n".join(formatted_filenames)
            + "\n\n📄 Введіть номер файлу який вас цікавить."
        )
        bot.send_message(message.from_user.id, message_text, reply_markup=cancel)
        bot.register_next_step_handler(message, send_logs, bot, filenames)
    else:
        bot.send_message(message.from_user.id, "❌ Немає жодного файлу з логами.")
        menu(message, bot)
    os.chdir("..")


def send_file(message: types.Message, bot: TeleBot, filename: str):
    file = open(filename, "rb")
    bot.send_document(message.chat.id, file)


def send_logs(message: types.Message, bot: TeleBot, filenames: list):
    if message.text == cancel_str:
        menu(message, bot)
    else:
        try:
            if int(message.text) <= len(filenames) and int(message.text) > 0:
                filename = Path.cwd() / f"general_logs/{filenames[int(message.text)-1]}"
                with open(filename, "r") as file:
                    lines = file.readlines()
                    chunks = [lines[i : i + 20] for i in range(0, len(lines), 20)]
                edit_message = bot.send_message(message.from_user.id, ".")
                bot.chunks[edit_message.id] = [
                    chunks,
                    filename,
                ]
                update_page(message, edit_message.id, message.from_user.id, bot, len(chunks)-1)

            else:
                raise ValueError
        except ValueError:
            bot.send_message(
                message.from_user.id,
                f"🤖 Не розумію. Оберіть відповідь від 1 до {len(filenames)}.",
                parse_mode="html",
                reply_markup=cancel_str,
            )
            bot.register_next_step_handler(message, send_logs, bot, filenames)


def update_page(
    message: types.Message,
    message_id: int,
    chat_id: int,
    bot: TeleBot,
    page_number: int,
):
    # chat_id = message.from_user.id
    # message_id = message.id
    chunks = bot.chunks[message_id][0]
    if 0 <= page_number < len(chunks):
        text = "".join(chunks[page_number])
        markup = types.InlineKeyboardMarkup()

        if page_number > 0:
            markup.add(
                types.InlineKeyboardButton(
                    "⬆️ Попередня", callback_data=f"page_{page_number - 1}"
                )
            )

        if page_number < len(chunks) - 1:
            markup.add(
                types.InlineKeyboardButton(
                    "⬇️ Наступна", callback_data=f"page_{page_number + 1}"
                )
            )

        markup.add(types.InlineKeyboardButton("❌ Вийти", callback_data="exit"))
        markup.add(
            types.InlineKeyboardButton("📄 Переглянути файл", callback_data="send_file")
        )

        bot.edit_message_text(
            chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup
        )
    else:
        bot.edit_message_text(
            chat_id=chat_id, message_id=message_id, text="Сторінки скінчилися."
        )


def user_stats(bot: TeleBot, message: types.Message):
    data = bot.user_storage.read()
    users = len(data["users"]) - 1
    stats = len(data["stats"])
    outages = len(data["outages"])
    bot.send_message(
        message.from_user.id,
        f"Усього користувачів: {users}\n\nПідписано на статистику: {stats}\nПідписано на сповіщення: {outages}",
    )
    menu(message, bot)
