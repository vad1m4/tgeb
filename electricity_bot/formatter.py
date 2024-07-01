from electricity_bot.time import unix_to_time


def format(unix: int) -> str:
    print(unix_to_time(unix))
    print(unix)
    hours, minutes, seconds = unix_to_time(unix).split(":")
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    if hours > 0 and minutes > 0 and seconds > 0:
        return f"{hours} годин(-и), {minutes} хвилин й {seconds} секунд"
    if hours > 0 and minutes > 0:
        return f"{hours} годин(-и) й {minutes} хвилин"
    if hours > 0:
        return f"{hours} годин(-и)"
    if minutes > 0 and seconds > 0:
        return f"{minutes} хвилин й {seconds} секунд"
    if minutes > 0:
        return f"{minutes} хвилин"
    if seconds > 0:
        return f"{seconds} секунд"
