from electricity_bot.time import seconds_to_time


def format_time(time: int, measurement: str) -> str:
    if (time % 10) == 1 and time != 11:
        measurement += "у"
    if (time % 10) > 1 and (time % 10) < 5 and (time > 20 or time < 10):
        measurement += "и"
    return measurement


def format_days(days: int) -> str:
    if (days % 10) > 1 and (days % 10) < 5 and (days > 20 or days < 10):
        return "дні"
    if (days % 10) == 1 and days != 11:
        return "день"

    return "днів"


def format(unix: int) -> str:
    days, hours, minutes, seconds = seconds_to_time(unix).split(":")
    days = int(days)
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)

    components = []

    if days > 0:
        components.append(f"{days} {format_days(days)}")
    if hours > 0:
        components.append(f"{hours} {format_time(hours, 'годин')}")

    if minutes > 0:
        components.append(f"{minutes} {format_time(minutes, 'хвилин')}")

    if seconds > 0:
        components.append(f"{seconds} {format_time(seconds, 'секунд')}")

    if len(components) == 1:
        return components[0]
    else:
        return str(", ".join(components[:-1]) + f" й {components[-1]}")
