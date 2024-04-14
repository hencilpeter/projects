import wx

# begin wxGlade: dependencies
import wx.adv
# end wxGlade

# begin wxGlade: extracode
# end wxGlade
from windows.window_search_employee import WindowSearchEmployee
import json
from collections import defaultdict


class WindowInsertDuty(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: InsertDuty.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        self.sqlite_sqls = kwds['_sqlite_sqls']
        del kwds['_sqlite_sqls']

        wx.Dialog.__init__(self, *args, **kwds)
        self.SetTitle("Insert Duty...")

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        grid_sizer_1 = wx.GridSizer(5, 2, 0, 0)
        sizer_1.Add(grid_sizer_1, 1, wx.EXPAND, 0)

        label_1 = wx.StaticText(self, wx.ID_ANY, "Employee Number:")
        grid_sizer_1.Add(label_1, 0, 0, 0)

        self.txt_employee_Number = wx.TextCtrl(self, wx.ID_ANY, "")
        self.txt_employee_Number.SetMinSize((110, 23))
        self.txt_employee_Number.Enable(False)
        grid_sizer_1.Add(self.txt_employee_Number, 0, 0, 0)

        label_3 = wx.StaticText(self, wx.ID_ANY, "Employee First Name")
        grid_sizer_1.Add(label_3, 0, 0, 0)

        self.txt_employee_firstname = wx.TextCtrl(self, wx.ID_ANY, "")
        self.txt_employee_firstname.Enable(False)
        grid_sizer_1.Add(self.txt_employee_firstname, 0, 0, 0)

        label_2 = wx.StaticText(self, wx.ID_ANY, "Employee Last Name:")
        grid_sizer_1.Add(label_2, 0, 0, 0)

        self.txt_employee_lastname = wx.TextCtrl(self, wx.ID_ANY, "")
        self.txt_employee_lastname.Enable(False)
        grid_sizer_1.Add(self.txt_employee_lastname, 0, 0, 0)

        label_4 = wx.StaticText(self, wx.ID_ANY, "Department:")
        grid_sizer_1.Add(label_4, 0, 0, 0)

        self.txt_department = wx.TextCtrl(self, wx.ID_ANY, "")
        self.txt_department.Enable(False)
        grid_sizer_1.Add(self.txt_department, 0, 0, 0)

        label_5 = wx.StaticText(self, wx.ID_ANY, "Duty Date:")
        grid_sizer_1.Add(label_5, 0, 0, 0)

        self.datepicker_ctrl_duty_date = wx.adv.DatePickerCtrl(self, wx.ID_ANY,
                                                               style=wx.adv.DP_DEFAULT | wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        grid_sizer_1.Add(self.datepicker_ctrl_duty_date, 0, 0, 0)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_APPLY = wx.Button(self, wx.ID_APPLY, "")
        sizer_2.AddButton(self.button_APPLY)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        self.button_SEARCH = wx.Button(self, wx.ID_ANY, "Search Employee")
        sizer_2.Add(self.button_SEARCH, 0, 0, 0)

        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Layout()

        self.employee_dict = defaultdict(lambda: -1)

        self.Bind(wx.EVT_BUTTON, self.search_employee_handler, self.button_SEARCH)
        self.Bind(wx.EVT_BUTTON, self.apply_employee_handler, self.button_APPLY)
        # end wxGlade

    def search_employee_handler(self, event):
        search_employee = WindowSearchEmployee(None, wx.ID_ANY, "", _sqlite_sqls=self.sqlite_sqls)
        return_value = search_employee.ShowModal()
        if return_value == wx.ID_OK and search_employee.return_value is not None:
            self.employee_dict = json.loads(search_employee.return_value)
            self.populate_dialog_fields(_employee_dict=self.employee_dict)

    def populate_dialog_fields(self, _employee_dict):
        self.txt_employee_Number.SetValue(_employee_dict["employee_number"])
        self.txt_employee_firstname.SetValue(_employee_dict["first_name"])
        self.txt_employee_lastname.SetValue(_employee_dict["last_name"])
        self.txt_department.SetValue(_employee_dict["department"])

    def apply_employee_handler(self, event):
        self.EndModal(retCode=wx.ID_APPLY)

# end of class InsertDuty

# class MyApp(wx.App):
#     def OnInit(self):
#         self.dialog = InsertDuty(None, wx.ID_ANY, "")
#         self.SetTopWindow(self.dialog)
#         self.dialog.ShowModal()
#         self.dialog.Destroy()
#         return True
#
# # end of class MyApp
#
# if __name__ == "__main__":
#     app = MyApp(0)
#     app.MainLoop()
