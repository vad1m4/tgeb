from datetime import datetime
import time
import pytz

tz = pytz.timezone("Europe/Kiev")


def get_date():
    current_datetime = datetime.now()
    date = current_datetime.strftime("%d-%m-%Y")
    return date


def get_time(hyphen_type: str = ":") -> str:
    t = time.localtime()
    current_time = time.strftime(f"%H{hyphen_type}%M{hyphen_type}%S", t)
    return current_time


def unix_to_date(date_unix: int) -> time.struct_time:
    return datetime.fromtimestamp(date_unix, tz).strftime("%Y-%m-%d")


def unix_to_time(date_unix: int) -> time.struct_time:
    return datetime.fromtimestamp(date_unix, tz).strftime("%H:%M:%S")

def seconds_to_time(seconds: int):
    


def get_unix() -> int:
    return round(time.time())
