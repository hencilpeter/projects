import wx
import datetime


class Calendar(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.NO_BORDER):
        super(Calendar, self).__init__(parent, id, pos, size, style)

        self.current_date = datetime.datetime.now()

        self.InitUI()

    def InitUI(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Header with navigation buttons
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        prev_month_btn = wx.Button(self, wx.ID_ANY, "<<")
        prev_month_btn.Bind(wx.EVT_BUTTON, self.OnPrevMonth)
        hbox.Add(prev_month_btn, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)

        self.month_year_label = wx.StaticText(self, wx.ID_ANY, "")
        hbox.Add(self.month_year_label, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)

        next_month_btn = wx.Button(self, wx.ID_ANY, ">>")
        next_month_btn.Bind(wx.EVT_BUTTON, self.OnNextMonth)
        hbox.Add(next_month_btn, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)

        vbox.Add(hbox, flag=wx.ALIGN_CENTER)

        # Days of the week labels
        days_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        hbox_days = wx.BoxSizer(wx.HORIZONTAL)
        for name in days_names:
            day_label = wx.StaticText(self, wx.ID_ANY, name)
            hbox_days.Add(day_label, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        vbox.Add(hbox_days, flag=wx.ALIGN_CENTER)

        # Calendar grid
        self.grid = wx.GridSizer(6, 7, 0, 0)
        vbox.Add(self.grid, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        self.SetSizer(vbox)
        self.Layout()

        self.UpdateCalendar()

    def UpdateCalendar(self):
        # Clear previous content
        for item in self.grid.GetChildren():
            item.GetWindow().Destroy()

        # Set month and year label
        self.month_year_label.SetLabel(self.current_date.strftime("%B %Y"))

        # Get the first day of the month
        first_day = datetime.datetime(self.current_date.year, self.current_date.month, 1)

        # Get the number of days in the month
        num_days = (first_day + datetime.timedelta(days=32)).replace(day=1) - first_day

        # Set starting position for the first day
        start_pos = first_day.weekday()

        # Populate the calendar grid
        for i in range(start_pos):
            self.grid.Add(wx.Panel(self), 0, wx.EXPAND)

        day = 1
        for i in range(num_days.days):
            btn = wx.Button(self, wx.ID_ANY, str(day))
            self.grid.Add(btn, 0, wx.EXPAND)
            btn.Bind(wx.EVT_BUTTON, self.OnDateClicked)
            btn.SetBackgroundColour(colour='GREEN')
            day += 1

        while self.grid.GetItemCount() < 42:
            self.grid.Add(wx.Panel(self), 0, wx.EXPAND)

        self.Layout()

    def OnPrevMonth(self, event):
        self.current_date -= datetime.timedelta(days=1)
        self.current_date = datetime.datetime(self.current_date.year, self.current_date.month, 1)
        self.UpdateCalendar()

    def OnNextMonth(self, event):
        self.current_date += datetime.timedelta(days=32)
        self.current_date = datetime.datetime(self.current_date.year, self.current_date.month, 1)
        self.UpdateCalendar()

    def OnDateClicked(self, event):
        btn = event.GetEventObject()
        day = int(btn.GetLabel())

        selected_date = datetime.datetime(self.current_date.year, self.current_date.month, day)
        print("Selected date:", selected_date)


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Customizable Calendar View', size=(400, 300))
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Add the Calendar widget
        self.calendar = Calendar(panel)
        vbox.Add(self.calendar, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        panel.SetSizer(vbox)
        self.Show()


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()

# import wx
# import datetime
#
#
# class Calendar(wx.Panel):
#     def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.NO_BORDER):
#         super(Calendar, self).__init__(parent, id, pos, size, style)
#
#         self.current_date = datetime.datetime.now()
#
#         self.InitUI()
#
#     def InitUI(self):
#         vbox = wx.BoxSizer(wx.VERTICAL)
#
#         # Header with navigation buttons
#         hbox = wx.BoxSizer(wx.HORIZONTAL)
#
#         prev_month_btn = wx.Button(self, wx.ID_ANY, "<<")
#         prev_month_btn.Bind(wx.EVT_BUTTON, self.OnPrevMonth)
#         hbox.Add(prev_month_btn, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
#
#         self.month_year_label = wx.StaticText(self, wx.ID_ANY, "")
#         hbox.Add(self.month_year_label, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
#
#         next_month_btn = wx.Button(self, wx.ID_ANY, ">>")
#         next_month_btn.Bind(wx.EVT_BUTTON, self.OnNextMonth)
#         hbox.Add(next_month_btn, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
#
#         vbox.Add(hbox, flag=wx.ALIGN_CENTER)
#
#         # Calendar grid
#         self.grid = wx.GridSizer(6, 7, 0, 0)
#         vbox.Add(self.grid, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
#
#         self.SetSizer(vbox)
#         self.Layout()
#
#         self.UpdateCalendar()
#
#     def UpdateCalendar(self):
#         # Clear previous content
#         for item in self.grid.GetChildren():
#             item.GetWindow().Destroy()
#
#         # Set month and year label
#         self.month_year_label.SetLabel(self.current_date.strftime("%B %Y"))
#
#         # Get the first day of the month
#         first_day = datetime.datetime(self.current_date.year, self.current_date.month, 1)
#
#         # Get the number of days in the month
#         num_days = (first_day + datetime.timedelta(days=32)).replace(day=1) - first_day
#
#         # Set starting position for the first day
#         start_pos = first_day.weekday()
#
#         # Populate the calendar grid
#         for i in range(start_pos):
#             self.grid.Add(wx.Panel(self), 0, wx.EXPAND)
#
#         day = 1
#         for i in range(num_days.days):
#             btn = wx.Button(self, wx.ID_ANY, str(day))
#             self.grid.Add(btn, 0, wx.EXPAND)
#             btn.Bind(wx.EVT_BUTTON, self.OnDateClicked)
#             day += 1
#
#         while self.grid.GetItemCount() < 42:
#             self.grid.Add(wx.Panel(self), 0, wx.EXPAND)
#
#         self.Layout()
#
#     def OnPrevMonth(self, event):
#         self.current_date -= datetime.timedelta(days=1)
#         self.current_date = datetime.datetime(self.current_date.year, self.current_date.month, 1)
#         self.UpdateCalendar()
#
#     def OnNextMonth(self, event):
#         self.current_date += datetime.timedelta(days=32)
#         self.current_date = datetime.datetime(self.current_date.year, self.current_date.month, 1)
#         self.UpdateCalendar()
#
#     def OnDateClicked(self, event):
#         btn = event.GetEventObject()
#         day = int(btn.GetLabel())
#         selected_date = datetime.datetime(self.current_date.year, self.current_date.month, day)
#         print("Selected date:", selected_date)
#
#
# class MyFrame(wx.Frame):
#     def __init__(self):
#         super().__init__(parent=None, title='Customizable Calendar View', size=(400, 300))
#         panel = wx.Panel(self)
#         vbox = wx.BoxSizer(wx.VERTICAL)
#
#         # Add the Calendar widget
#         self.calendar = Calendar(panel)
#         vbox.Add(self.calendar, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
#
#         panel.SetSizer(vbox)
#         self.Show()
#
#
# if __name__ == '__main__':
#     app = wx.App()
#     frame = MyFrame()
#     app.MainLoop()
