import wx


class UtilDefaultValue:
    @staticmethod
    def get_default_date():
        dt = wx.DateTime().Set(1, 0, 1800)
        return dt
