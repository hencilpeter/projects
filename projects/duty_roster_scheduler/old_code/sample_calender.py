import wx
import wx.lib.calendar

class Calendar_Panel(wx.Panel):
    """ create a panel with a calendar on it"""
    def __init__(self, parent, id):
        # create a panel
        wx.Panel.__init__(self, parent, id)

        # create a label on the panel
        self.label1 = wx.StaticText(self, id, "", wx.Point(25, 220))

        # create the calendar
        self.cal = wx.lib.calendar.Calendar(self, id, pos=(25, 35), size=(200, 180), style=2)

        # get the current month & year
        start_month = self.cal.GetMonth()
        start_year = self.cal.GetYear()

        # set some of the colours
        self.SetBackgroundColour("yellow")
        self.cal.SetWeekColor('white', 'blue')
        self.cal.SetColor(wx.lib.calendar.COLOR_WEEKEND_FONT, 'green')
        self.cal.SetColor(wx.lib.calendar.COLOR_WEEKEND_BACKGROUND, 'white')
        self.cal.ShowWeekEnd()

        # colour holidays of current month
        self.set_days = holidays[start_month]
        self.cal.AddSelect(self.set_days, 'red', 'white')
        self.cal.Refresh()

        # mouse click on a day
        self.Bind(wx.lib.calendar.EVT_CALENDAR, self.OnCalSelected)

        # create year spin
        self.texty = wx.TextCtrl(self, -1, str(start_year), pos=(25, 10), size=(50, -1))
        h = self.texty.GetSize().height
        self.spiny = wx.SpinButton(self, -1, pos=(70, 10), size=(h*2, h))
        self.spiny.SetRange(1980, 2010)
        self.spiny.SetValue(start_year)
        self.Bind(wx.EVT_SPIN, self.OnSpiny, self.spiny)

        # create month spin
        self.textm = wx.TextCtrl(self, -1, str(start_month), pos=(130, 10), size=(50, -1))
        h = self.textm.GetSize().height
        self.spinm = wx.SpinButton(self, -1, pos=(170, 10), size=(h*2, h))
        self.spinm.SetRange(1, 12)
        self.spinm.SetValue(start_month)
        self.Bind(wx.EVT_SPIN, self.OnSpinm, self.spinm)

    def OnCalSelected(self, evt):
        text = "Date selected = %02d/%02d/%d" % (evt.month, evt.day, evt.year)
        self.label1.SetLabel(text)

    def OnSpiny(self, event):
        year = event.GetPosition()
        self.texty.SetValue(str(year))
        self.cal.SetYear(year)
        self.ResetDisplay()

    def OnSpinm(self, event):
        month = event.GetPosition()
        self.textm.SetValue(str(month))
        self.cal.SetMonth(month)
        self.ResetDisplay()

    def ResetDisplay(self):
        # reset holiday colour
        self.cal.AddSelect(self.set_days, 'black', 'white')
        # get number of the month
        month = self.cal.GetMonth()
        set_days = holidays[month]
        # set new holiday colour
        self.cal.AddSelect(set_days, 'red', 'white')
        self.cal.Refresh()
        # keep present list to reset colour
        self.set_days = set_days


# fill these dates out for the present year
# some could change with another year
# {month: list of holiday dates in month}
holidays = {
1: [1],
2: [13],
3: [22],
4: [3],
5: [29],
6: [15],
7: [4, 11],
8: [],
9: [3],
10: [],
11: [27, 26],
12: [24, 25]
}

app = wx.PySimpleApp()
# create a window/frame, no parent, -1 is default ID
frame = wx.Frame(None, -1, "Simple calendar", size = (260, 280))
# instanciate the class
Calendar_Panel(frame, -1)
frame.Show(1)
app.MainLoop()