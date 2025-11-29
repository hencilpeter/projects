import datetime

import wx
import wx.adv
# Press the green button in the gutter to run the script.
class MainWindow:
    # application object
    def __init__(self):
        self.application = wx.App()

        # frame object
        self.frame = wx.Frame(None, title="TODO: Marania Filaments Office Application", size=(800, 600))
        self.panel = wx.Panel(self.frame)

        date_date_of_birth = wx.adv.DatePickerCtrl(self.panel, wx.ID_ANY, wx.DefaultDateTime, pos=(180, 185), size=(150, 23))
        dt = wx.DateTime()
        dt.Set(1, 0, 1800)

        date_date_of_birth.SetValue(dt)



    def ShowWindow(self):
      self.frame.Show()
      self.application.MainLoop()


if __name__ == '__main__':
    main_window = MainWindow()
    main_window.ShowWindow()


    print("Test")
