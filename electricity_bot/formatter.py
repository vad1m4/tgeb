from electricity_bot.time import seconds_to_time


def format_text(time: int, measurement: str) -> str:
    if time > 20 or time < 10:
        if (time % 10) == 1:
            measurement += "у"
        elif (time % 10) > 1 and (time % 10) < 5:
            measurement += "и"
    return measurement


def format(unix: int) -> str:
    hours, minutes, seconds = seconds_to_time(unix).split(":")
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)

    components = []

    if hours > 0:
        components.append(f"{hours} {format_text(hours, 'годин')}")

    if minutes > 0:
        components.append(f"{minutes} {format_text(minutes, 'хвилин')}")

    if seconds > 0:
        components.append(f"{seconds} {format_text(seconds, 'секунд')}")

    if len(components) == 1:
        return components[0]
    else:
        return str(", ".join(components[:-1]) + f" й {components[-1]}")
