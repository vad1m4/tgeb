from telebot import ExceptionHandler # type: ignore

import logging


class TGEBExceptionHandler(ExceptionHandler):
    # def __init__(self, logger: logging.Logger) -> None:

    def handle(self, exception: Exception) -> bool:
        self.logger.error(
            f"{exception} occured. Take actions regarding this error as soon as possible."
        )
        return True
