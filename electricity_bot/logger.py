import logging.config
import logging.handlers
from pathlib import Path
from telebot.types import Message  # type: ignore
import os


def setup_logging(log_file: str, level: int):
    general_logs = Path.cwd() / "general_logs"
    if not general_logs.exists():
        os.makedirs("general_logs")
    user_action_logs = Path.cwd() / "user_action_logs"
    if not user_action_logs.exists():
        os.makedirs("user_action_logs")
    outage_logs = Path.cwd() / "outage_logs"
    if not outage_logs.exists():
        os.makedirs("outage_logs")

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "[%(asctime)s] %(levelname)s at %(module)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S%z",
            },
        },
        "handlers": {
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
                "filename": f"{general_logs}/{log_file}",
                "encoding": "utf8",
            },
            "file_outage": {
                "class": "logging.FileHandler",
                "level": "INFO",
                "formatter": "simple",
                "filename": f"{outage_logs}/{log_file}",
                "encoding": "utf8",
            },
            "file_user_actions": {
                "class": "logging.FileHandler",
                "level": "INFO",
                "formatter": "simple",
                "filename": f"{user_action_logs}/{log_file}",
                "encoding": "utf8",
            },
        },
        "loggers": {
            "general": {"level": level, "handlers": ["stdout", "file_general"]},
            "outage": {"level": "INFO", "handlers": ["file_outage"]},
            "user_actions": {"level": "INFO", "handlers": ["file_user_actions"]},
        },
    }

    logging.config.dictConfig(config)


# class UserCmdFilter(logging.Filter):
#     @override
#     def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
#         return record.message[:3] == "cmd"


# class OutageFilter(logging.Filter):
#     @override
#     def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
#         return record.message[:3] == "otg"


# class CustomFormatter(logging.Formatter):
#     @override
#     def format(self, record: logging.LogRecord) -> str:
#         return f"[{record.asctime}] {record.levelname} at {record.module} - {record.message[4:]}"


logger = logging.getLogger("user_actions")


def log_cmd(message: Message, name: str):
    logger.info(
        f"{message.from_user.first_name} {message.from_user.last_name} [{message.from_user.id}] has used the following command: {name}"
    )
