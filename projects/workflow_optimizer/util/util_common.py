import wx
from datetime import datetime as dt
import datetime
from datetime import  timedelta
import decimal

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

    @staticmethod
    def assign_or_append_dict(_dict, _dict_key, _dict_value):
        if _dict[_dict_key] == -1:
            _dict[_dict_key] = [_dict_value]
        else:
            _dict[_dict_key].append(_dict_value)

    @staticmethod
    def NumToWords(num):
        num = decimal.Decimal(num)
        decimal_part = num - int(num)
        num = int(num)

        if decimal_part:
            # return num2words(num) + " point " + (" ".join(num2words(i) for i in str(decimal_part)[2:]))
            return "Rupees " + UtilCommon.NumToWords(num) + " And " + (UtilCommon.NumToWords(str(decimal_part)[2:])) + " paisa only"

        under_20 = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven',
                    'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        above_100 = {100: 'Hundred', 1000: 'Thousand', 100000: 'Lakhs', 10000000: 'Crores'}

        if num < 20:
            return under_20[num]

        if num < 100:
            return tens[num // 10 - 2] + ('' if num % 10 == 0 else ' ' + under_20[num % 10])

        # find the appropriate pivot - 'Million' in 3,603,550, or 'Thousand' in 603,550
        pivot = max([key for key in above_100.keys() if key <= num])

        return UtilCommon.NumToWords(num // pivot) + ' ' + above_100[pivot] + (
            '' if num % pivot == 0 else ' ' + UtilCommon.NumToWords(num % pivot))
