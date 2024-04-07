import wx

import wx.adv
import wx.grid

from window_handlers.window_employee_handlers import WindowEmployeeHandlers
import datetime

class WindowEmployee(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: AddUpdateEmployee.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((1156, 650))
        self.SetTitle("Add_Update Employee")

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        grid_sizer_2 = wx.GridSizer(7, 2, 0, 0)
        sizer_3.Add(grid_sizer_2, 1, wx.EXPAND, 0)

        label_1 = wx.StaticText(self, wx.ID_ANY, "Employee Number:")
        label_1.SetMinSize((150, 16))
        grid_sizer_2.Add(label_1, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.txt_emp_number = wx.TextCtrl(self, wx.ID_ANY, "")
        self.txt_emp_number.SetMinSize((170, 23))
        grid_sizer_2.Add(self.txt_emp_number, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        label_2 = wx.StaticText(self, wx.ID_ANY, "First Name:")
        label_2.SetMinSize((150, 16))
        grid_sizer_2.Add(label_2, 0, 0, 0)

        self.txt_first_name = wx.TextCtrl(self, wx.ID_ANY, "")
        self.txt_first_name.SetMinSize((170, 23))
        grid_sizer_2.Add(self.txt_first_name, 0, 0, 0)

        label_3 = wx.StaticText(self, wx.ID_ANY, "Last Name:")
        label_3.SetMinSize((150, 16))
        grid_sizer_2.Add(label_3, 0, 0, 0)

        self.txt_last_name = wx.TextCtrl(self, wx.ID_ANY, "")
        self.txt_last_name.SetMinSize((170, 23))
        grid_sizer_2.Add(self.txt_last_name, 0, 0, 0)

        label_4 = wx.StaticText(self, wx.ID_ANY, "Father Name:")
        label_4.SetMinSize((150, 16))
        grid_sizer_2.Add(label_4, 0, 0, 0)

        self.txt_father_name = wx.TextCtrl(self, wx.ID_ANY, "")
        self.txt_father_name.SetMinSize((170, 23))
        grid_sizer_2.Add(self.txt_father_name, 0, 0, 0)

        label_5 = wx.StaticText(self, wx.ID_ANY, "Sex:")
        label_5.SetMinSize((150, 16))
        grid_sizer_2.Add(label_5, 0, 0, 0)

        sizer_11 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_2.Add(sizer_11, 1, wx.EXPAND, 0)

        self.rd_btn_male = wx.RadioButton(self, wx.ID_ANY, "Male")
        sizer_11.Add(self.rd_btn_male, 0, 0, 0)

        self.rd_btn_female = wx.RadioButton(self, wx.ID_ANY, "Female")
        sizer_11.Add(self.rd_btn_female, 0, 0, 0)

        label_6 = wx.StaticText(self, wx.ID_ANY, "Date of Birth:")
        grid_sizer_2.Add(label_6, 0, 0, 0)

        self.datepicker_date_of_birth = wx.adv.DatePickerCtrl(self, wx.ID_ANY, style=wx.adv.DP_DROPDOWN)
        self.datepicker_date_of_birth.SetMinSize((111, 23))
        grid_sizer_2.Add(self.datepicker_date_of_birth, 0, 0, 0)

        label_7 = wx.StaticText(self, wx.ID_ANY, "Highest Qualification")
        grid_sizer_2.Add(label_7, 0, 0, 0)

        self.cmb_qualification = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN)
        grid_sizer_2.Add(self.cmb_qualification, 0, 0, 0)

        grid_sizer_1 = wx.GridSizer(7, 2, 0, 0)
        sizer_3.Add(grid_sizer_1, 1, wx.EXPAND, 0)

        label_8 = wx.StaticText(self, wx.ID_ANY, "Employment Start Date:")
        grid_sizer_1.Add(label_8, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.datepicker_employment_start_date = wx.adv.DatePickerCtrl(self, wx.ID_ANY, style=wx.adv.DP_DROPDOWN)
        self.datepicker_employment_start_date.SetMinSize((111, 23))
        grid_sizer_1.Add(self.datepicker_employment_start_date, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        label_9 = wx.StaticText(self, wx.ID_ANY, "Employment End Date:")
        grid_sizer_1.Add(label_9, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.datepicker_employment_end_date = wx.adv.DatePickerCtrl(self, wx.ID_ANY, style=wx.adv.DP_DROPDOWN)
        self.datepicker_employment_end_date.SetMinSize((111, 23))
        grid_sizer_1.Add(self.datepicker_employment_end_date, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        label_10 = wx.StaticText(self, wx.ID_ANY, "Department")
        grid_sizer_1.Add(label_10, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.cmd_department = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN)
        self.cmd_department.SetMinSize((111, 23))
        grid_sizer_1.Add(self.cmd_department, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        label_11 = wx.StaticText(self, wx.ID_ANY, "No. of leaves (per month):")
        grid_sizer_1.Add(label_11, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.cm_no_of_leaves = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN)
        grid_sizer_1.Add(self.cm_no_of_leaves, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        label_12 = wx.StaticText(self, wx.ID_ANY, "Primary Duty:")
        grid_sizer_1.Add(label_12, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.cmb_primary_duty = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN)
        grid_sizer_1.Add(self.cmb_primary_duty, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        label_13 = wx.StaticText(self, wx.ID_ANY, "Salary Type:")
        grid_sizer_1.Add(label_13, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.cmb_salary_type = wx.ComboBox(self, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN)
        grid_sizer_1.Add(self.cmb_salary_type, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        label_14 = wx.StaticText(self, wx.ID_ANY, "Salary:")
        grid_sizer_1.Add(label_14, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.txt_salary = wx.TextCtrl(self, wx.ID_ANY, "")
        grid_sizer_1.Add(self.txt_salary, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        bitmap_employee_image = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap("C:\\Users\\User\\Documents\\GitHub\\projects\\workflow_optimizer\\data\\HencilPhoto.jpg", wx.BITMAP_TYPE_ANY))
        sizer_3.Add(bitmap_employee_image, 0, 0, 0)

        sizer_12 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_12, 1, wx.EXPAND, 0)

        self.grid_address = wx.grid.Grid(self, wx.ID_ANY, size=(1, 1))
        self.grid_address.CreateGrid(10, 2)
        self.grid_address.SetRowLabelSize(30)
        self.grid_address.SetColLabelSize(30)
        self.grid_address.SetGridLineColour(wx.Colour(85, 128, 240))
        self.grid_address.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid_address.SetColLabelValue(0, "Address Type")
        self.grid_address.SetColSize(0, 120)
        self.grid_address.SetColLabelValue(1, "Detail")
        self.grid_address.SetColSize(1, 220)
        self.grid_address.SetMinSize((300, 250))
        sizer_12.Add(self.grid_address, 0, wx.ALL | wx.RESERVE_SPACE_EVEN_IF_HIDDEN, 3)

        self.grid_contact = wx.grid.Grid(self, wx.ID_ANY, size=(1, 1))
        self.grid_contact.CreateGrid(10, 2)
        self.grid_contact.SetRowLabelSize(30)
        self.grid_contact.SetColLabelSize(30)
        self.grid_contact.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid_contact.SetColLabelValue(0, "Contact Type")
        self.grid_contact.SetColSize(0, 130)
        self.grid_contact.SetColLabelValue(1, "Detail")
        self.grid_contact.SetColSize(1, 150)
        self.grid_contact.SetMinSize((300, 250))
        sizer_12.Add(self.grid_contact, 0, wx.ALL, 3)

        self.grid_identity = wx.grid.Grid(self, wx.ID_ANY, size=(1, 1))
        self.grid_identity.CreateGrid(10, 3)
        self.grid_identity.SetRowLabelSize(30)
        self.grid_identity.SetColLabelSize(30)
        self.grid_identity.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid_identity.SetColLabelValue(0, "Identity Type")
        self.grid_identity.SetColSize(0, 80)
        self.grid_identity.SetColLabelValue(1, "Number/ID")
        self.grid_identity.SetColSize(1, 100)
        self.grid_identity.SetColLabelValue(2, "Path")
        self.grid_identity.SetColSize(2, 170)
        self.grid_identity.SetMinSize((400, 250))
        sizer_12.Add(self.grid_identity, 0, wx.ALL, 3)

        self.grid_sizer_3 = wx.GridSizer(1, 2, 1, 1)
        sizer_1.Add(self.grid_sizer_3, 1, wx.ALIGN_RIGHT | wx.ALL | wx.FIXED_MINSIZE | wx.SHAPED, 0)

        sizer_13 = wx.StdDialogButtonSizer()
        self.grid_sizer_3.Add(sizer_13, 1, wx.EXPAND | wx.TOP, 0)

        self.btn_search = wx.Button(self, wx.ID_ANY, "Search")
        sizer_13.Add(self.btn_search, 0, wx.ALL, 12)

        sizer_14 = wx.StdDialogButtonSizer()
        self.grid_sizer_3.Add(sizer_14, 0, wx.ALIGN_RIGHT | wx.TOP, 8)

        self.btn_new = wx.Button(self, wx.ID_ANY, "&New")
        sizer_14.Add(self.btn_new, 0, 0, 0)

        self.btn_save = wx.Button(self, wx.ID_ANY, "&Save")
        sizer_14.Add(self.btn_save, 0, 0, 0)

        self.btn_cancel = wx.Button(self, wx.ID_ANY, "Cancel")
        sizer_14.Add(self.btn_cancel, 0, 0, 0)

        sizer_14.Realize()

        sizer_13.Realize()

        self.SetSizer(sizer_1)

        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.handler_cancel, self.btn_cancel)
        self.Bind(wx.EVT_BUTTON, self.handler_new, self.btn_new)

        # initialize handlers
        WindowEmployeeHandlers.handle_clear_all_controls(self)

    def handler_new(self, event):
        WindowEmployeeHandlers.handle_clear_all_controls(self)

    def handler_cancel(self, event):
        self.Close()




    # end of class AddUpdateEmployee


# class MyApp(wx.App):
#     def OnInit(self):
#         self.dlg_employee = WindowEmployee(None, wx.ID_ANY, "")
#         self.SetTopWindow(self.dlg_employee)
#         self.dlg_employee.ShowModal()
#         self.dlg_employee.Destroy()
#         return True


# # end of class MyApp
#
# if __name__ == "__main__":
#     app = MyApp(0)
#     app.MainLoop()
