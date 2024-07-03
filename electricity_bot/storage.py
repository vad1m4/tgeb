from pathlib import Path
import json
from abc import ABC, abstractmethod
from typing import Iterable
from electricity_bot.time import get_time, get_date, get_unix, unix_to_date


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
            self._jsonfile.write_text('{"outages": [], "stats": []}')

    def read(self) -> list[int]:
        with open(self._jsonfile, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data

    def write(self, users_d: dict[str:int]) -> None:
        with open(self._jsonfile, "w", encoding="utf-8") as f:
            json.dump(users_d, f, indent=4)

    def save(self, user_id: int, _type: str) -> None:
        if not self.subscribed(user_id, _type):
            users = self.read()
            users[_type].append(user_id)
            self.write(users)

    def delete(self, user_id: int, _type: str) -> None:
        users = self.read()
        if self.subscribed(user_id, _type):
            users[_type].remove(user_id)
        self.write(users)

    def subscribed(self, user_id: int, _type: str) -> bool:
        if user_id in self.read()[_type]:
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

    def save(self, power_off: int, power_on: int = get_unix()) -> None:
        date = unix_to_date(power_off)
        general_outages = self.read()
        if not date in general_outages.keys():
            general_outages[date] = {"outages": 1}
        else:
            general_outages[date]["outages"] += 1
        general_outages[date][general_outages[date]["outages"]] = {
            "start": power_off,
            "end": power_on,
        }
        self.write(general_outages)

    def delete(self, outage: int = 1) -> None:
        outages = self.read()
        date = get_date()
        del outages[date][outage]
        self.write(outages)

    def exists(self, outage: int = 1, date: str = get_date()) -> bool:
        if str(outage) in self.read()[date].keys():
            return True
        else:
            return False

    def get_outage(self, outage: int = 1, date: str = get_date()) -> dict[str:int]:
        if self.exists(outage):
            return self.read()[date][outage]

    def lasted(self, outage: int = 1, date: str = get_date()) -> int:
        if self.exists(outage):
            data = self.read()
            return int(data[date][str(outage)]["end"] - data[date][outage]["start"])
