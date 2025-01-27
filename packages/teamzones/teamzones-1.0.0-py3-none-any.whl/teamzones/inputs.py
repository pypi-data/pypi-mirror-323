from zoneinfo import ZoneInfo
from dateutil import parser
from datetime import datetime


def timezones_csv_to_zone_info_list(timezones: str):
    timezones_list = timezones.split(",")
    return list(map((lambda tz: ZoneInfo(tz)), timezones_list))


def time_input_to_datetime(time: str = None):
    return datetime.now() if time == None else parser.parse(time)
