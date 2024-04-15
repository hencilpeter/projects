import wx
from datetime import datetime as dt
import datetime
from datetime import  timedelta

class UtilCommon:
    @staticmethod
    def show_message_dialog(_message_title, _message, _style=wx.OK | wx.STAY_ON_TOP | wx.CENTRE):
        message_dialog = wx.MessageDialog(None, _message, _message_title, _style)
        message_dialog.ShowModal()

    @staticmethod
    def get_start_month_date(_date_yyyymmdd):
        pass

    @staticmethod
    def get_end_month_date(_date_yyyymmdd):
        typecasted_date = datetime.datetime.strptime(_date_yyyymmdd, "%Y%m%d")
        # getting next month
        # using replace to get to last day + offset
        # to reach next month
        nxt_mnth = typecasted_date.replace(day=28) + datetime.timedelta(days=4)

        # subtracting the days from next month date to
        # get last date of current Month
        last_date = nxt_mnth - datetime.timedelta(days=nxt_mnth.day)
        last_date_yyyymmdd = last_date.strftime("%Y%m%d")
        return last_date_yyyymmdd
