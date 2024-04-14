import wx

# begin wxGlade: dependencies
import wx.adv
import wx.grid
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class ViewPrintDutyAllocation(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: ViewPrintDutyAllocation.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE

        self.sqlite_sqls = kwds['_sqlite_sqls']
        del kwds['_sqlite_sqls']

        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((724, 542))
        self.SetTitle("View/Print Duty Allocations")

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND | wx.FIXED_MINSIZE, 0)

        grid_sizer_1 = wx.GridSizer(3, 4, 0, 0)
        sizer_3.Add(grid_sizer_1, 1, wx.EXPAND, 0)

        label_1 = wx.StaticText(self, wx.ID_ANY, "Start Date:")
        label_1.SetMinSize((54, 16))
        grid_sizer_1.Add(label_1, 0, 0, 0)

        self.datepicker_ctrl_start_date = wx.adv.DatePickerCtrl(self, wx.ID_ANY, style=wx.adv.DP_DEFAULT | wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        grid_sizer_1.Add(self.datepicker_ctrl_start_date, 0, 0, 0)

        label_2 = wx.StaticText(self, wx.ID_ANY, "End Date:")
        grid_sizer_1.Add(label_2, 0, 0, 0)

        self.datepicker_ctrl_end_date = wx.adv.DatePickerCtrl(self, wx.ID_ANY, style=wx.adv.DP_DEFAULT | wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        self.datepicker_ctrl_end_date.SetMinSize((80, 25))
        grid_sizer_1.Add(self.datepicker_ctrl_end_date, 0, 0, 0)

        label_3 = wx.StaticText(self, wx.ID_ANY, "Department:")
        grid_sizer_1.Add(label_3, 0, 0, 0)

        self.combo_box_department = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN)
        self.combo_box_department.SetMinSize((111, 23))
        grid_sizer_1.Add(self.combo_box_department, 0, 0, 0)

        label_4 = wx.StaticText(self, wx.ID_ANY, "Duty:")
        grid_sizer_1.Add(label_4, 0, 0, 0)

        self.combo_box_duty = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN)
        self.combo_box_duty.SetMinSize((111, 23))
        grid_sizer_1.Add(self.combo_box_duty, 0, 0, 0)

        label_5 = wx.StaticText(self, wx.ID_ANY, "Employee Name:")
        grid_sizer_1.Add(label_5, 0, 0, 0)

        self.combo_box_employee_name = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN)
        self.combo_box_employee_name.SetMinSize((111, 23))
        grid_sizer_1.Add(self.combo_box_employee_name, 0, 0, 0)

        # grid_sizer_1.Add((0, 0), 0, 0, 0)
        #
        # grid_sizer_1.Add((0, 0), 0, 0, 0)
        #
        # sizer_3.Add((0, 0), 0, 0, 0)

        self.grid_duties = wx.grid.Grid(self, wx.ID_ANY, size=(1, 1))
        self.grid_duties.CreateGrid(0, 5)
        self.grid_duties.SetRowLabelSize(30)
        self.grid_duties.SetColLabelSize(30)
        self.grid_duties.EnableEditing(0)
        self.grid_duties.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid_duties.SetColLabelValue(0, "Department")
        self.grid_duties.SetColSize(0, 100)
        self.grid_duties.SetColLabelValue(1, "Employee Number")
        self.grid_duties.SetColSize(1, 117)
        self.grid_duties.SetColLabelValue(2, "First Name")
        self.grid_duties.SetColSize(2, 125)
        self.grid_duties.SetColLabelValue(3, "Last Name")
        self.grid_duties.SetColSize(3, 100)
        self.grid_duties.SetColLabelValue(4, "Duty Name")
        self.grid_duties.SetColSize(4, 100)
        self.grid_duties.SetMinSize((600, 620))
        #sizer_1.Add(self.grid_duties, 0, wx.EXPAND | wx.FIXED_MINSIZE | wx.SHAPED, 0)
        sizer_1.Add(self.grid_duties, 1, wx.EXPAND, 0)

        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_4, 0, wx.FIXED_MINSIZE | wx.SHAPED, 0)

        sizer_5 = wx.FlexGridSizer(1, 3, 0, 0)
        sizer_4.Add(sizer_5, 0, wx.ALIGN_BOTTOM | wx.FIXED_MINSIZE, 0)

        self.btn_load_duties = wx.Button(self, wx.ID_ANY, "Load Duties")
        sizer_5.Add(self.btn_load_duties, 0, 0, 0)

        self.btn_save_as_html = wx.Button(self, wx.ID_ANY, "Save Duties as HTML")
        sizer_5.Add(self.btn_save_as_html, 0, 0, 0)

        self.btn_clear_duties = wx.Button(self, wx.ID_ANY, "Clear")
        sizer_5.Add(self.btn_clear_duties, 0, 0, 0)

        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        sizer_4.Add(sizer_6, 1, wx.FIXED_MINSIZE, 0)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        self.button_CANCEL.SetMinSize((75, 23))
        sizer_6.Add(self.button_CANCEL, 0, wx.FIXED_MINSIZE, 0)

        self.SetSizer(sizer_1)

        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.load_duties_handler, self.btn_load_duties)
        self.Bind(wx.EVT_BUTTON, self.save_as_html_handler, self.btn_save_as_html)
        self.Bind(wx.EVT_BUTTON, self.handler_cancel, self.button_CANCEL)
        # end wxGlade

    def load_duties_handler(self, event):  # wxGlade: ViewPrintDutyAllocation.<event_handler>
        print("Event handler 'load_duties_handler' not implemented!")
        event.Skip()

    def save_as_html_handler(self, event):  # wxGlade: ViewPrintDutyAllocation.<event_handler>
        print("Event handler 'save_as_html_handler' not implemented!")
        event.Skip()

    def handler_cancel(self, event):  # wxGlade: ViewPrintDutyAllocation.<event_handler>
        print("Event handler 'handler_cancel' not implemented!")
        event.Skip()

# end of class ViewPrintDutyAllocation

# class MyApp(wx.App):
#     def OnInit(self):
#         self.view_print_duty_allocation = ViewPrintDutyAllocation(None, wx.ID_ANY, "")
#         self.SetTopWindow(self.view_print_duty_allocation)
#         self.view_print_duty_allocation.ShowModal()
#         self.view_print_duty_allocation.Destroy()
#         return True
#
# # end of class MyApp
#
# if __name__ == "__main__":
#     app = MyApp(0)
#     app.MainLoop()
