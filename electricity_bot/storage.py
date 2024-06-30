from pathlib import Path
import json
from abc import ABC, abstractmethod
from typing import Iterable

class JSONStorage(ABC):
    @abstractmethod
    def save(self, record) -> None: ...

    @abstractmethod
    def read(self) -> list: ...

    @abstractmethod
    def write(self, records) -> None: ...

    @abstractmethod
    def delete(self, indexes_to_delete: Iterable[int]) -> None: ...

class JSONFileUserStorage(JSONStorage):
    def __init__(self, jsonfile: Path) -> None:
        self._jsonfile = jsonfile
        self._init_storage()

    def _init_storage(self) -> None:
        if not self._jsonfile.exists():
            self._jsonfile.write_text("[]")

    def read(self) -> list[int]:
        with open(self._jsonfile, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data["subscribed_users"]
        
    def write(self, users_l: list[int]) -> None:
        with open(self._jsonfile, "w", encoding="utf-8") as f:
            users = {"subscribed_users": users_l}
            json.dump(users, f, indent=4)

    def save(self, user_id: int) -> None:
        if not self.subscribed(user_id):
            users = self.read()
            users.append(user_id)
            self.write(users)

    def delete(self, user_id: int) -> None:
        users = self.read()
        if self.subscribed(user_id):
            users.remove(user_id)
        self.write(users)

    def subscribed(self, user_id: int) -> bool:
        if user_id in self.read():
            return True
        else:
            return False


