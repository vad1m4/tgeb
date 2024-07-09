from pathlib import Path
import json
from abc import ABC, abstractmethod
from electricity_bot.time import get_date, get_unix, unix_to_date


class JSONStorage(ABC):
    @abstractmethod
    def save(self, record) -> None: ...

    @abstractmethod
    def read(self) -> list: ...

    @abstractmethod
    def write(self, records) -> None: ...

    @abstractmethod
    def delete(self, index: int) -> None: ...


class JSONFileUserStorage(JSONStorage):
    def __init__(self, jsonfile: Path) -> None:
        self._jsonfile = jsonfile
        self._init_storage()

    def _init_storage(self) -> None:
        if not self._jsonfile.exists():
            self._jsonfile.write_text(
                '{"outages": [], "stats": [], "users": {"blacklist": {}}}'
            )

    def read(self) -> dict:
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

    def authorize(self, user_id: int, phone_number: int) -> bool:
        if not self.is_blacklisted(phone_number) and not self.is_blacklisted(user_id):
            if not self.is_authorized(user_id):
                users = self.read()
                users["users"][user_id] = phone_number
                self.write(users)
                return True
            else:
                return True

    def is_authorized(self, user_id: int) -> bool:
        if str(user_id) in self.read()["users"].keys():
            return True
        else:
            return False

    def blacklist(self, phone_number: int | str, reason: str) -> None:
        users = self.read()
        users["users"]["blacklist"][phone_number] = reason
        users["users"] = {
            key: val for key, val in users["users"].items() if val != phone_number
        }
        self.write(users)

    def unblacklist(self, phone_number: int | str) -> bool:
        if self.is_blacklisted(phone_number):
            users = self.read()
            users["users"]["blacklist"].pop(phone_number)
            self.write(users)
            return True
        else:
            return False

    def is_blacklisted(self, phone_number: int | str) -> bool:
        if str(phone_number) in self.read()["users"]["blacklist"].keys():
            return True
        else:
            return False

    def why_blacklist(self, phone_number: int | str) -> str:
        if self.is_blacklisted(phone_number):
            return self.read()["users"]["blacklist"][phone_number]
        else:
            return None


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

    def save(self, file_id: str, date: str = None) -> None:
        if date == None:
            date = get_date()
        file_ids = self.read()
        file_ids[date] = file_id
        self.write(file_ids)

    def delete(self) -> None:
        file_ids = self.read()
        date = get_date()
        del file_ids[date]
        self.write(file_ids)

    def exists(self, date: str = None) -> bool:
        if date == None:
            date = get_date()
        if date in self.read().keys():
            return True
        else:
            return False

    def get_schedule(self, date: str = None):
        if date == None:
            date = get_date()
        return self.read()[date]


class JSONFileOutageStorage(JSONStorage):
    def __init__(self, jsonfile: Path) -> None:
        self._jsonfile = jsonfile
        self._init_storage()

    def _init_storage(self) -> None:
        if not self._jsonfile.exists():
            self._jsonfile.write_text(
                f'{{"temp_start": {get_unix()}, "temp_end": {get_unix()}}}'
            )

    def read(self) -> dict:
        with open(self._jsonfile, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data

    def write(self, outages: dict) -> None:
        with open(self._jsonfile, "w", encoding="utf-8") as f:
            json.dump(outages, f, indent=4)

    def save(self, power_off: int, power_on: int = None) -> None:
        if power_on == None:
            power_on = get_unix()
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

    def temp(self, _type: str = "start", time: int = None):
        if time == None:
            time = get_unix()
        general_outages = self.read()
        general_outages[f"temp_{_type}"] = time
        self.write(general_outages)

    def delete(self, outage: int = 1) -> None:
        outages = self.read()
        date = get_date()
        del outages[date][outage]
        self.write(outages)

    def exists(self, outage: int = 1, date: str = None) -> bool:
        if date == None:
            date = get_date()
        data = self.read()
        if date in data.keys():
            if str(outage) in self.read()[date].keys():
                return True
            else:
                return False
        else:
            return False

    def get_outage(self, outage: int = 1, date: str = None) -> dict[str:int]:
        if date == None:
            date = get_date()
        if self.exists(outage):
            return self.read()[date][outage]

    def lasted(self, outage: int = 1, date: str = None) -> int:
        if date == None:
            date = get_date()
        data = self.read()
        return int(data[date][str(outage)]["end"] - data[date][outage]["start"])
