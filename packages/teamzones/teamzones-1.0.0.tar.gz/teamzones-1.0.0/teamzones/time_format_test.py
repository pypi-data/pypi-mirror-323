import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from teamzones.time_format import format_time, abbreviate_time_format


class TestTimeFormattingFunctions(unittest.TestCase):
    def setUp(self):
        self.test_time = datetime(2000, 1, 1, 0, 0, tzinfo=ZoneInfo("UTC"))

    def test_format_time_default_format(self):
        result = format_time(self.test_time)
        self.assertEqual(result, "12am UTC")

    def test_format_time_custom_format(self):
        custom_format = "%H:%M"
        result = format_time(self.test_time, custom_format)
        self.assertEqual(result, "00:00")

    def test_abbreviate_time_format_on_hour(self):
        on_hour_time = datetime(2000, 1, 1, 0, 0, tzinfo=ZoneInfo("UTC"))
        result = abbreviate_time_format(on_hour_time)
        self.assertEqual(result, "12am UTC")

    def test_abbreviate_time_format_on_one_digit_hour(self):
        on_hour_time = datetime(2000, 1, 1, 3, 0, tzinfo=ZoneInfo("UTC"))
        result = abbreviate_time_format(on_hour_time)
        self.assertEqual(result, "3am UTC")

    def test_abbreviate_time_format_on_two_digit_hour_minute(self):
        on_hour_time = datetime(2000, 1, 1, 10, 10, tzinfo=ZoneInfo("UTC"))
        result = abbreviate_time_format(on_hour_time)
        self.assertEqual(result, "10:10am UTC")

    def test_abbreviate_time_format_on_single_digit_hour_minute(self):
        on_hour_time = datetime(2000, 1, 1, 3, 3, tzinfo=ZoneInfo("UTC"))
        result = abbreviate_time_format(on_hour_time)
        self.assertEqual(result, "3:03am UTC")


if __name__ == "__main__":
    unittest.main()
