import wx

class UtilCommon:
    @staticmethod
    def show_message_dialog(_message_title, _message, _style=wx.OK | wx.STAY_ON_TOP | wx.CENTRE):
        message_dialog = wx.MessageDialog(None, _message, _message_title, _style)
        message_dialog.ShowModal()