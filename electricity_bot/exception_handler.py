import telebot  # type: ignore

import logging

logger = logging.getLogger("general")

telebot.apihelper.RETRY_ON_ERROR = True
telebot.apihelper.RETRY_TIMEOUT = 20
telebot.apihelper.MAX_RETRIES = 20


class TGEBExceptionHandler(telebot.ExceptionHandler):
    # def __init__(self, logger: logging.Logger) -> None:

    def handle(self, exception: Exception) -> bool:
        logger.error(
            f"{exception} occured. Take actions regarding this error as soon as possible."
        )
        return True
