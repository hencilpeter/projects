import wx
import datetime


class UtilDefaultValue:
    @staticmethod
    def get_default_min_date_of_birth():
        dt = wx.DateTime().Set(1, 0, 1950)
        return dt

    @staticmethod
    def get_current_date():
        dt = datetime.datetime.today().date()
        return dt

    @staticmethod
    def get_default_emp_end_date():
        dt = wx.DateTime().Set(31, 11, 9999)
        return dt
