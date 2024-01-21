from datetime import datetime as dt
import datetime


class DateTimeUtil:
    @staticmethod
    def days_between(_date1, _date2):
        date1 = dt.strptime(_date1, "%Y%m%d")
        date2 = dt.strptime(_date2, "%Y%m%d")
        return abs((date2 - date1).days) + 1

    @staticmethod
    def is_monday(_current_date):
        return _current_date.isoweekday() == 1
