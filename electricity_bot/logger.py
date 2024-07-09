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
                "datefmt": "%Y-%m-%d %H:%M:%S%z",
            },
            "user_cmd": {
                "()": "electricity_bot.logger.UserCmdFormatter",
                "format": "[%(asctime)s] %(levelname)s at %(module)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S%z",
            },
            "outage": {
                "()": "electricity_bot.logger.OutageFormatter",
                "format": "[%(asctime)s] %(levelname)s at %(module)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S%z",
            },
        },
        "filters": {
            "user_cmd": {"()": "electricity_bot.logger.UserCmdFilter"},
            "outage": {"()": "electricity_bot.logger.OutageFilter"},
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
            "stdout": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "simple",
                "stream": "ext://sys.stdout",
            },
            "file_general": {
                "class": "logging.FileHandler",
                "level": "INFO",
                "formatter": "simple",
                "filename": f"general_logs/{log_file}",
            },
            "file_outage": {
                "class": "logging.FileHandler",
                "level": "INFO",
                "formatter": "simple",
                "filters": ["outage"],
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


def log_cmd(message: Message, name: str, logger: logging.Logger):
    logger.info(
        f"cmd {message.from_user.first_name} {message.from_user.last_name} [{message.from_user.id}] has used the following command: {name}"
    )
