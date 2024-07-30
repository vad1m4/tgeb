import datetime
from time import localtime, time, strftime  # type: ignore
import pytz  # type: ignore

tz = pytz.timezone("Europe/Kiev")


def get_date(day: int = 0) -> str:
    _datetime = datetime.datetime.now() + datetime.timedelta(days=day)
    date = _datetime.strftime("%d-%m-%Y")
    return date


def get_time(hyphen_type: str = ":") -> str:
    t = localtime()
    return str(strftime(f"%H{hyphen_type}%M{hyphen_type}%S", t))


def unix_to_date(date_unix: int) -> str:
    return str(datetime.datetime.fromtimestamp(date_unix, tz).strftime("%d-%m-%Y"))


def unix_to_time(date_unix: int) -> str:
    return str(datetime.datetime.fromtimestamp(date_unix, tz).strftime("%H:%M:%S"))


def seconds_to_time(seconds: int) -> str:
    # timedelta = str(datetime.timedelta(seconds=seconds))

    days, remainder = divmod(seconds, 86400)

    hours, remainder = divmod(remainder, 3600)

    minutes, seconds = divmod(remainder, 60)
    return f"{days}:{hours}:{minutes}:{seconds}"


def get_unix() -> int:
    return int(round(time()))



print(seconds_to_time(1233))