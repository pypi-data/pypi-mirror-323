from datetime import datetime

DEFAULT_FORMAT = "%I:%M%p %Z"


def format_time(time: datetime, format: str = None):
    if format == None:
        return abbreviate_time_format(time)
    else:
        return time.strftime(format)


def abbreviate_time_format(time: datetime):
    hour = int(time.strftime("%I"))
    minute = time.strftime("%M")
    meridian = time.strftime("%p").lower()
    timezone = time.strftime("%Z")

    if time.minute == 0:
        return f"{hour}{meridian} {timezone}"
    else:
        return f"{hour}:{minute}{meridian} {timezone}"
