import logging
from telebot.types import Message # type: ignore
import os


def add_logger(
    self,
    name: str,
    log_file: str,
    do_stream: bool = False,
    level=logging.INFO,
):
    logger = logging.Logger(name, level)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    try:
        handler = logging.FileHandler(log_file)
        handler.setFormatter(self.formatter)
    except FileNotFoundError:
        dirname = log_file.split("/")[0]
        os.makedirs(dirname)
        handler = logging.FileHandler(log_file)
        handler.setFormatter(self.formatter)
    if do_stream:
        stream = logging.StreamHandler()
        stream.setFormatter(self.formatter)
        logger.addHandler(self.stream)

    logger.setLevel(level)
    logger.addHandler(self.handler)

    logger.info(f"{name} initialized.")

    return logger


# def init(self, name: str, success: bool, e: str = ""):
#     if success:
#         self.info(f"{name} initialized.")
#     else:
#         self.warning(f"{name} failed to initialize due to an exception: {e}")


# def cmd(self, message: Message, name: str):
#     self.info(
#         f"{message.from_user.first_name} {message.from_user.last_name} [{message.from_user.id}] has used the following command: {name}"
#     )
