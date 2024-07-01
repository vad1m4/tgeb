from pathlib import Path
import json
from abc import ABC, abstractmethod
from typing import Iterable
from electricity_bot.time import get_time, get_date


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
            self._jsonfile.write_text('{"subscribed_users": []}')

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


class JSONFileScheduleStorage(JSONStorage):
    def __init__(self, jsonfile: Path) -> None:
        self._jsonfile = jsonfile
        self._init_storage()

    def _init_storage(self) -> None:
        if not self._jsonfile.exists():
            self._jsonfile.write_text("{}")

    def read(self) -> dict:
        with open(self._jsonfile, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data

    def write(self, file_ids: dict) -> None:
        with open(self._jsonfile, "w", encoding="utf-8") as f:
            json.dump(file_ids, f, indent=4)

    def save(self, file_id: str, date: str = get_date()) -> None:
        file_ids = self.read()
        file_ids[date] = file_id
        self.write(file_ids)

    def delete(self) -> None:
        file_ids = self.read()
        date = get_date()
        del file_ids[date]
        self.write(file_ids)

    def exists(self, date: str = get_date()) -> bool:
        if date in self.read().keys():
            return True
        else:
            return False

    def get_schedule(self, date: str = get_date()):
        return self.read()[date]


class JSONFileOutageStorage(JSONStorage):
    def __init__(self, jsonfile: Path) -> None:
        self._jsonfile = jsonfile
        self._init_storage()

    def _init_storage(self) -> None:
        if not self._jsonfile.exists():
            self._jsonfile.write_text("{}")

    def read(self) -> dict:
        with open(self._jsonfile, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data

    def write(self, outages: dict) -> None:
        with open(self._jsonfile, "w", encoding="utf-8") as f:
            json.dump(outages, f, indent=4)

    def save(self, outage: dict, outage_type: str, date: str = get_date()) -> None:
        outages = self.read()
        if "outages" in outage[date]:
            outage[date]["outages"] = 0
        else:
            outage[date]["outages"] += 1
        outage[date][len(outage[date])][outage_type] = 

    def delete(self) -> None:
        file_ids = self.read()
        date = get_date()
        del file_ids[date]
        self.write(file_ids)

    def exists(self, date: str = get_date()) -> bool:
        if date in self.read().keys():
            return True
        else:
            return False

    def get_schedule(self, date: str = get_date()):
        return self.read()[date]
