
import wx

# begin wxGlade: dependencies
import wx.adv
import wx.grid
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class DutyAllocation(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: DutyAllocation.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((1305, 884))
        self.SetTitle("dialog")

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        sizer_4 = wx.BoxSizer(wx.VERTICAL)
        sizer_3.Add(sizer_4, 1, wx.EXPAND, 0)

        label_1 = wx.StaticText(self, wx.ID_ANY, "Employee Details")
        label_1.SetMinSize((150, 16))
        label_1.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        sizer_4.Add(label_1, 0, 0, 0)

        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(sizer_5, 1, wx.EXPAND, 0)

        label_2 = wx.StaticText(self, wx.ID_ANY, "Department(Filter)")
        sizer_5.Add(label_2, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.check_list_box_department = wx.CheckListBox(self, wx.ID_ANY, choices=["choice 1"])
        self.check_list_box_department.SetMinSize((151, 55))
        sizer_5.Add(self.check_list_box_department, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        sizer_3.Add(sizer_6, 1, wx.EXPAND, 0)

        label_3 = wx.StaticText(self, wx.ID_ANY, "Duty Details")
        label_3.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        sizer_6.Add(label_3, 0, 0, 0)

        sizer_7 = wx.BoxSizer(wx.VERTICAL)
        sizer_6.Add(sizer_7, 1, wx.EXPAND, 0)

        grid_sizer_1 = wx.GridSizer(2, 2, 4, 165)
        sizer_7.Add(grid_sizer_1, 1, wx.EXPAND, 0)

        label_4 = wx.StaticText(self, wx.ID_ANY, "Start Date:")
        grid_sizer_1.Add(label_4, 18, wx.ALIGN_CENTER_VERTICAL, 0)

        self.datepicker_ctrl_start_date = wx.adv.DatePickerCtrl(self, wx.ID_ANY, style=wx.adv.DP_DEFAULT | wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        self.datepicker_ctrl_start_date.SetMinSize((120, 25))
        grid_sizer_1.Add(self.datepicker_ctrl_start_date, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        label_5 = wx.StaticText(self, wx.ID_ANY, "End Date:")
        grid_sizer_1.Add(label_5, 6, 0, 0)

        self.datepicker_ctrl_end_date = wx.adv.DatePickerCtrl(self, wx.ID_ANY, style=wx.adv.DP_DEFAULT | wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        self.datepicker_ctrl_end_date.SetMinSize((120, 25))
        grid_sizer_1.Add(self.datepicker_ctrl_end_date, 0, 0, 0)

        sizer_12 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_7.Add(sizer_12, 1, wx.BOTTOM, 0)

        self.search_control_department = wx.SearchCtrl(self, wx.ID_ANY, "")
        self.search_control_department.ShowCancelButton(True)
        sizer_12.Add(self.search_control_department, 0, 0, 0)

        self.search_control_identity = wx.SearchCtrl(self, wx.ID_ANY, "")
        self.search_control_identity.ShowCancelButton(True)
        sizer_12.Add(self.search_control_identity, 0, 0, 0)

        self.search_control_name = wx.SearchCtrl(self, wx.ID_ANY, "")
        self.search_control_name.ShowCancelButton(True)
        sizer_12.Add(self.search_control_name, 0, 0, 0)

        self.search_control_duty_code = wx.SearchCtrl(self, wx.ID_ANY, "")
        self.search_control_duty_code.ShowCancelButton(True)
        sizer_12.Add(self.search_control_duty_code, 0, 0, 0)

        self.search_control_duty_name = wx.SearchCtrl(self, wx.ID_ANY, "")
        self.search_control_duty_name.ShowCancelButton(True)
        sizer_12.Add(self.search_control_duty_name, 0, 0, 0)

        self.search_control_duty_date = wx.SearchCtrl(self, wx.ID_ANY, "")
        self.search_control_duty_date.ShowCancelButton(True)
        sizer_12.Add(self.search_control_duty_date, 0, 0, 0)

        sizer_12.Add((0, 0), 0, 0, 0)

        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_8, 1, wx.EXPAND | wx.RESERVE_SPACE_EVEN_IF_HIDDEN, 0)

        self.grid_employee_detail = wx.grid.Grid(self, wx.ID_ANY, size=(1, 1))
        self.grid_employee_detail.CreateGrid(10, 4)
        self.grid_employee_detail.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid_employee_detail.SetColLabelValue(0, "Department")
        self.grid_employee_detail.SetColSize(0, 100)
        self.grid_employee_detail.SetColLabelValue(1, "Identity")
        self.grid_employee_detail.SetColSize(1, 75)
        self.grid_employee_detail.SetColLabelValue(2, "First Name")
        self.grid_employee_detail.SetColSize(2, 100)
        self.grid_employee_detail.SetColLabelValue(3, "Last Name")
        self.grid_employee_detail.SetColSize(3, 100)
        sizer_8.Add(self.grid_employee_detail, 1, wx.EXPAND, 0)

        self.grid_duty_detail = wx.grid.Grid(self, wx.ID_ANY, size=(1, 1))
        self.grid_duty_detail.CreateGrid(10, 6)
        self.grid_duty_detail.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid_duty_detail.SetColLabelValue(0, "Department")
        self.grid_duty_detail.SetColSize(0, 120)
        self.grid_duty_detail.SetColLabelValue(1, "Identity")
        self.grid_duty_detail.SetColSize(1, 100)
        self.grid_duty_detail.SetColLabelValue(2, "Name")
        self.grid_duty_detail.SetColSize(2, 100)
        self.grid_duty_detail.SetColLabelValue(3, "Duty Code")
        self.grid_duty_detail.SetColSize(3, 100)
        self.grid_duty_detail.SetColLabelValue(4, "Duty Name")
        self.grid_duty_detail.SetColSize(4, 100)
        self.grid_duty_detail.SetColLabelValue(5, "Duty Date")
        self.grid_duty_detail.SetColSize(5, 100)
        sizer_8.Add(self.grid_duty_detail, 1, wx.EXPAND, 0)

        sizer_9 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_9, 1, wx.SHAPED, 0)

        sizer_10 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Employees"), wx.HORIZONTAL)
        sizer_9.Add(sizer_10, 1, wx.FIXED_MINSIZE, 0)

        self.btn_clear = wx.Button(self, wx.ID_ANY, "Clear")
        sizer_10.Add(self.btn_clear, 0, 0, 0)

        self.btn_delete = wx.Button(self, wx.ID_ANY, "Delete")
        sizer_10.Add(self.btn_delete, 0, 0, 0)

        sizer_11 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Duty"), wx.HORIZONTAL)
        sizer_9.Add(sizer_11, 0, wx.EXPAND | wx.FIXED_MINSIZE | wx.SHAPED, 0)

        self.btn_duty_generate = wx.Button(self, wx.ID_ANY, "Generate")
        sizer_11.Add(self.btn_duty_generate, 0, 0, 0)

        self.btn_duty_save = wx.Button(self, wx.ID_ANY, "Save")
        sizer_11.Add(self.btn_duty_save, 0, 0, 0)

        self.btn_duty_delete = wx.Button(self, wx.ID_ANY, "Delete")
        sizer_11.Add(self.btn_duty_delete, 0, 0, 0)

        self.btn_duty_clear = wx.Button(self, wx.ID_ANY, "Clear")
        sizer_11.Add(self.btn_duty_clear, 0, 0, 0)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_OK = wx.Button(self, wx.ID_OK, "")
        self.button_OK.SetDefault()
        sizer_2.AddButton(self.button_OK)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        sizer_2.Realize()

        self.SetSizer(sizer_1)

        self.SetAffirmativeId(self.button_OK.GetId())
        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Layout()
        # end wxGlade

# # end of class DutyAllocation
#
# class MyApp(wx.App):
#     def OnInit(self):
#         self.dialog = DutyAllocation(None, wx.ID_ANY, "")
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
