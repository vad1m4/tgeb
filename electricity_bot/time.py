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
