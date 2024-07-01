from telebot import TeleBot, types
from electricity_bot.vars import generic_choice, generic_markup, cancel

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