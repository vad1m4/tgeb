import logging
from telebot.types import Message
import os


class TGEBLogger(logging.Logger):
    def __init__(self, name: str, log_file: str,  stream: bool = False, level=logging.INFO,):
        super().__init__(name)
        self.formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
        )
        try:
            self.handler = logging.FileHandler(log_file)
            self.handler.setFormatter(self.formatter)
        except FileNotFoundError:
            dirname = log_file.split("/")[0]
            os.makedirs(dirname)
            self.handler = logging.FileHandler(log_file)
            self.handler.setFormatter(self.formatter)
        if stream:
            self.stream = logging.StreamHandler()
            self.stream.setFormatter(self.formatter)
            self.addHandler(self.stream)
        
        self.setLevel(level)
        self.addHandler(self.handler)
        

    def init(self, name: str, success: bool, e: str = ""):
        if success:
            self.info(f"{name} initialized.")
        else:
            self.warning(f"{name} failed to initialize due to an exception: {e}")

    def cmd(self, message: Message, name: str):
        self.info(
            f"{message.from_user.first_name} {message.from_user.last_name} [{message.from_user.id}] has used the following command: {name}"
        )
