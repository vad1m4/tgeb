from telebot import ExceptionHandler
import logging


class TGEBExceptionHandler(ExceptionHandler):
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger
        self.logger.init("Exception handler", True)

    def handle(self, exception: Exception) -> None:
        self.logger.error(
            f"{exception} occured. Take actions regarding this error as soon as possible."
        )
        return True
