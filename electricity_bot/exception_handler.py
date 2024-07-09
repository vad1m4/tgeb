from telebot import ExceptionHandler  # type: ignore

import logging

logger = logging.getLogger(__name__)


class TGEBExceptionHandler(ExceptionHandler):
    # def __init__(self, logger: logging.Logger) -> None:

    def handle(self, exception: Exception) -> bool:
        logger.error(
            f"{exception} occured. Take actions regarding this error as soon as possible."
        )
        return True
