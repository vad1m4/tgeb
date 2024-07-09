import logging.config
import logging.handlers
import atexit
from pathlib import Path
from typing import Any, override
from telebot.types import Message  # type: ignore
import os


def setup_logging(log_file: str, level: int):
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "[%(asctime)s] %(levelname)s at %(module)s - %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            },
            "user_cmd": {
                "()": "electricity_bot.logger.UserCmdFormatter",
                "format": "[%(asctime)s] %(levelname)s at %(module)s - %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            },
            "outage": {
                "()": "electricity_bot.logger.OutageFormatter",
                "format": "[%(asctime)s] %(levelname)s at %(module)s - %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            },
        },
        "filters": {
            "user_cmd": {"()": "electricity_bot.logger.UserCmdFilter"},
            "outage_cmd": {"()": "electricity_bot.logger.OutageFilter"},
        },
        "handlers": {
            "queue_handler": {
                "class": "logging.handlers.QueueHandler",
                "handlers": [
                    "stdout",
                    "file_general",
                    "file_outage",
                    "file_user_actions",
                ],
                "respect_handler_level": True,
            },
            "stderr": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "simple",
                "stream": "ext://sys.stdout",
            },
            "file_general": {
                "class": "logging.FileHandler",
                "level": level,
                "formatter": "simple",
                "filename": f"general_logs/{log_file}",
            },
            "file_outage": {
                "class": "logging.FileHandler",
                "level": "INFO",
                "formatter": "simple",
                "filters": ["user_cmd"],
                "filename": f"outage_logs/{log_file}",
            },
            "file_user_actions": {
                "class": "logging.FileHandler",
                "level": "INFO",
                "formatter": "simple",
                "filters": ["user_cmd"],
                "filename": f"user_action_logs/{log_file}",
            },
        },
        "loggers": {"root": {"level": "DEBUG", "handlers": ["queue_handler"]}},
    }

    logging.config.dictConfig(config)
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)


class UserCmdFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return record.message[:3] == "cmd"


class OutageFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return record.message[:6] == "Outage"


class UserCmdFormatter(logging.Formatter):
    @override
    def format(self, record: logging.LogRecord) -> str:
        return record.message[3:]


class OutageFormatter(logging.Formatter):
    @override
    def format(self, record: logging.LogRecord) -> str:
        return record.message[6:]


# def add_logger(
#     name: str,
#     log_file: str,
#     do_stream: bool = False,
#     level=logging.INFO,
# ):
#     logger = logging.Logger(name, level)
#     formatter = logging.Formatter(
#         "[%(asctime)s] %(levelname)s at %(module)s - %(message)s",
#         "%Y-%m-%dT%H:%M:%S%z",
#     )
#     try:
#         handler = logging.FileHandler(log_file)
#         handler.setFormatter(formatter)
#     except FileNotFoundError:
#         dirname = log_file.split("/")[0]
#         os.makedirs(dirname)
#         handler = logging.getHandlerByName()
#         handler.setFormatter(formatter)
#     if do_stream:
#         stream = logging.StreamHandler()
#         stream.setFormatter(formatter)
#         logger.addHandler(stream)

#     logger.setLevel(level)
#     logger.addHandler(handler)

#     logger.info(f"{name} initialized.")

#     return logger


def log_cmd(message: Message, name: str, _logger: str | Any = None):
    if _logger == None:
        _logger = "user_actions_logger"
    logger = logging.getLogger(_logger)
    logger.info(
        f"cmd {message.from_user.first_name} {message.from_user.last_name} [{message.from_user.id}] has used the following command: {name}"
    )
