import datetime
import time
import pytz

tz = pytz.timezone("Europe/Kiev")


def get_date(day: int = 0) -> str:
    current_datetime = datetime.datetime.now()
    current_datetime -= datetime.timedelta(days=-day)
    date = current_datetime.strftime("%d-%m-%Y")
    return date


def get_time(hyphen_type: str = ":") -> str:
    t = time.localtime()
    current_time = time.strftime(f"%H{hyphen_type}%M{hyphen_type}%S", t)
    return current_time


def unix_to_date(date_unix: int) -> time.struct_time:
    return datetime.datetime.fromtimestamp(date_unix, tz).strftime("%d-%m-%Y")


def unix_to_time(date_unix: int) -> time.struct_time:
    return datetime.datetime.fromtimestamp(date_unix, tz).strftime("%H:%M:%S")


def seconds_to_time(seconds: int) -> str:
    return str(datetime.timedelta(seconds=seconds))


def get_unix() -> int:
    return round(time.time())
