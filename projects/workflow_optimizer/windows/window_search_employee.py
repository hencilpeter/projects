import wx
import wx.grid


class WindowSearchEmployee(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: SearchEmployee.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((660, 400))
        self.SetTitle("TODO:Search Employee Details")

        self.panel_1 = wx.Panel(self, wx.ID_ANY)

        sizer_2 = wx.BoxSizer(wx.VERTICAL)

        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(sizer_4, 1, wx.EXPAND, 0)

        self.search_department = wx.SearchCtrl(self.panel_1, wx.ID_ANY, "")
        self.search_department.ShowCancelButton(True)
        sizer_4.Add(self.search_department, 0, 1, 0)

        self.search_identity = wx.SearchCtrl(self.panel_1, wx.ID_ANY, "")
        self.search_identity.ShowCancelButton(True)
        sizer_4.Add(self.search_identity, 0, 1, 0)

        self.search_firstname = wx.SearchCtrl(self.panel_1, wx.ID_ANY, "")
        self.search_firstname.ShowCancelButton(True)
        sizer_4.Add(self.search_firstname, 0, 1, 0)

        self.search_lastname = wx.SearchCtrl(self.panel_1, wx.ID_ANY, "")
        self.search_lastname.ShowCancelButton(True)
        sizer_4.Add(self.search_lastname, 0, 1, 0)

        self.grid_employees = wx.grid.Grid(self.panel_1, wx.ID_ANY, size=(1, 1))
        self.grid_employees.CreateGrid(10, 4)
        self.grid_employees.SetColLabelSize(40)
        self.grid_employees.SetRowLabelSize(60)
        self.grid_employees.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid_employees.SetColLabelValue(0, "Department")
        self.grid_employees.SetColSize(0, 160)
        self.grid_employees.SetColLabelValue(1, "Identity")
        self.grid_employees.SetColSize(1, 130)
        self.grid_employees.SetColLabelValue(2, "First Name")
        self.grid_employees.SetColSize(2, 130)
        self.grid_employees.SetColLabelValue(3, "Last Name")
        self.grid_employees.SetColSize(3, 130)
        sizer_2.Add(self.grid_employees, 4, wx.ALL | wx.EXPAND, 4)

        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(sizer_3, 1, wx.EXPAND, 0)

        self.btn_Ok = wx.Button(self.panel_1, wx.ID_ANY, "OK")
        sizer_3.Add(self.btn_Ok, 0, 1, 0)

        self.btn_Cancel = wx.Button(self.panel_1, wx.ID_ANY, "Cancel")
        sizer_3.Add(self.btn_Cancel, 0,1, 0)

        sizer_3.Add((0, 0), 0, 0, 0)

        sizer_3.Add((0, 0), 0, 0, 0)

        sizer_3.Add((0, 0), 0, 0, 0)

        self.panel_1.SetSizer(sizer_2)

        self.Layout()

        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.handler_department_cancel, self.search_department)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.handler_department_search, self.search_department)
        self.Bind(wx.EVT_TEXT, self.handler_department_text, self.search_department)
        self.Bind(wx.EVT_TEXT_ENTER, self.handler_department_enter, self.search_department)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.handler_identity_cancel, self.search_identity)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.handler_identity_search, self.search_identity)
        self.Bind(wx.EVT_TEXT, self.handler_identity_text, self.search_identity)
        self.Bind(wx.EVT_TEXT_ENTER, self.handler_identity_enter, self.search_identity)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.handler_firstname_cancel, self.search_firstname)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.handler_firstname_search, self.search_firstname)
        self.Bind(wx.EVT_TEXT, self.handler_firstname_text, self.search_firstname)
        self.Bind(wx.EVT_TEXT_ENTER, self.handler_firstname_enter, self.search_firstname)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.handler_lastname_cencel, self.search_lastname)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.handler_lastname_serach, self.search_lastname)
        self.Bind(wx.EVT_TEXT, self.handler_lastname_text, self.search_lastname)
        self.Bind(wx.EVT_TEXT_ENTER, self.handler_lastname_enter, self.search_lastname)
        self.Bind(wx.grid.EVT_GRID_CMD_SELECT_CELL, self.handler_grid_select, self.grid_employees)
        self.Bind(wx.EVT_BUTTON, self.handler_Ok, self.btn_Ok)
        self.Bind(wx.EVT_BUTTON, self.handler_Cancel, self.btn_Cancel)
        # end wxGlade

    def handler_department_cancel(self, event):  # wxGlade: SearchEmployee.<event_handler>
        print("Event handler 'handler_department_cancel' not implemented!")
        event.Skip()

    def handler_department_search(self, event):  # wxGlade: SearchEmployee.<event_handler>
        print("Event handler 'handler_department_search' not implemented!")
        event.Skip()

    def handler_department_text(self, event):  # wxGlade: SearchEmployee.<event_handler>
        print("Event handler 'handler_department_text' not implemented!")
        event.Skip()

    def handler_department_enter(self, event):  # wxGlade: SearchEmployee.<event_handler>
        print("Event handler 'handler_department_enter' not implemented!")
        event.Skip()

    def handler_identity_cancel(self, event):  # wxGlade: SearchEmployee.<event_handler>
        print("Event handler 'handler_identity_cancel' not implemented!")
        event.Skip()

    def handler_identity_search(self, event):  # wxGlade: SearchEmployee.<event_handler>
        print("Event handler 'handler_identity_search' not implemented!")
        event.Skip()

    def handler_identity_text(self, event):  # wxGlade: SearchEmployee.<event_handler>
        print("Event handler 'handler_identity_text' not implemented!")
        event.Skip()

    def handler_identity_enter(self, event):  # wxGlade: SearchEmployee.<event_handler>
        print("Event handler 'handler_identity_enter' not implemented!")
        event.Skip()

    def handler_firstname_cancel(self, event):  # wxGlade: SearchEmployee.<event_handler>
        print("Event handler 'handler_firstname_cancel' not implemented!")
        event.Skip()

    def handler_firstname_search(self, event):  # wxGlade: SearchEmployee.<event_handler>
        print("Event handler 'handler_firstname_search' not implemented!")
        event.Skip()

    def handler_firstname_text(self, event):  # wxGlade: SearchEmployee.<event_handler>
        print("Event handler 'handler_firstname_text' not implemented!")
        event.Skip()

    def handler_firstname_enter(self, event):  # wxGlade: SearchEmployee.<event_handler>
        print("Event handler 'handler_firstname_enter' not implemented!")
        event.Skip()

    def handler_lastname_cencel(self, event):  # wxGlade: SearchEmployee.<event_handler>
        print("Event handler 'handler_lastname_cencel' not implemented!")
        event.Skip()

    def handler_lastname_serach(self, event):  # wxGlade: SearchEmployee.<event_handler>
        print("Event handler 'handler_lastname_serach' not implemented!")
        event.Skip()

    def handler_lastname_text(self, event):  # wxGlade: SearchEmployee.<event_handler>
        print("Event handler 'handler_lastname_text' not implemented!")
        event.Skip()

    def handler_lastname_enter(self, event):  # wxGlade: SearchEmployee.<event_handler>
        print("Event handler 'handler_lastname_enter' not implemented!")
        event.Skip()

    def handler_grid_select(self, event):  # wxGlade: SearchEmployee.<event_handler>
        print("Event handler 'handler_grid_select' not implemented!")
        event.Skip()

    def handler_Ok(self, event):  # wxGlade: SearchEmployee.<event_handler>
        print("Event handler 'handler_Ok' not implemented!")
        event.Skip()

    def handler_Cancel(self, event):  # wxGlade: SearchEmployee.<event_handler>
        self.Close()

    # end of class SearchEmployee


# class MenuBar(wx.App):
#     def OnInit(self):
#         self.search_employee = WindowSearchEmployee(None, wx.ID_ANY, "")
#         self.SetTopWindow(self.search_employee)
#         self.search_employee.ShowModal()
#         self.search_employee.Destroy()
#         return True
#
#     # end of class MenuBar
#
#
# if __name__ == "__main__":
#     menubar = MenuBar(0)
#     menubar.MainLoop()
