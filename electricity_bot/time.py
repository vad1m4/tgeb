from datetime import datetime
import time


def get_date():
    current_datetime = datetime.now()
    date = current_datetime.strftime("%d-%m-%Y")
    return date


def get_time(hyphen_type: str = ":"):
    t = time.localtime()
    current_time = time.strftime(f"%H{hyphen_type}%M{hyphen_type}%S", t)
    return current_time


def unix_to_date(date_unix):
    return datetime.fromtimestamp(date_unix + 7200).strftime("%Y-%m-%d")


def unix_to_time(date_unix):
    return datetime.fromtimestamp(date_unix + 7200).strftime("%H:%M:%S")


def get_unix(date_unix):
    return round(time.time())
