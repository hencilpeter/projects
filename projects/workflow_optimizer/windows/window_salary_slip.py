
import wx

# begin wxGlade: dependencies
import wx.adv
import wx.grid
from windows.window_search_employee import WindowSearchEmployee
import json
from datetime import datetime, timedelta
from collections import defaultdict
from util.util_common import UtilCommon
from util.util_payslip import UtilPayslip
from data_models.employee_model import EmployeeModel
from data_models.common_model import CommonModel
# end wxGlade

# begin wxGlade: extracode
# end wxGlade

# self.sqlite_sqls = kwds['_sqlite_sqls']
# del kwds['_sqlite_sqls']
class SalaryAdvice(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: SalaryAdvice.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE

        self.sqlite_sqls = kwds['_sqlite_sqls']
        del kwds['_sqlite_sqls']

        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((816, 558))
        self.SetTitle("dialog")

        #self.employee_data_as_list = EmployeeModel.get_all_employee_details_as_list(_sql_connection=self.sqlite_sqls)
        #self.employee_data_as_list_filtered = self.employee_data_as_list.copy()
        # self.employee_dict = CommonModel.get_dict_from_list(self.employee_data_as_list, "employee_number")
        # # department_cursor = self.sqlite_sqls.get_table_data("select * from department;")
        # # self.department_names_as_list = CommonModel.get_table_data_as_list(_data_cursor=department_cursor)
        # # duty_catalog_cursor = self.sqlite_sqls.get_table_data("select * from duty_catalog;")
        # # self.duty_catalog_as_list = CommonModel.get_table_data_as_list(_data_cursor=duty_catalog_cursor)
        # # self.duty_catalog_dict = CommonModel.get_dict_from_list(self.duty_catalog_as_list, "duty_code")

        #department_list = self.get_department_list(_department_list=self.department_names_as_list)


        self.employee_salary_dict = defaultdict(lambda :-1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        sizer_4 = wx.BoxSizer(wx.VERTICAL)
        sizer_3.Add(sizer_4, 1, wx.EXPAND | wx.SHAPED, 0)

        label_1 = wx.StaticText(self, wx.ID_ANY, "Salary Advice", style=wx.ALIGN_CENTER_HORIZONTAL)
        label_1.SetMinSize((790, 45))
        label_1.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        sizer_4.Add(label_1, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND | wx.SHAPED, 0)

        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(sizer_5, 1, wx.EXPAND, 0)

        label_2 = wx.StaticText(self, wx.ID_ANY, "Select Salary Month:")
        label_2.SetMinSize((107, 16))
        sizer_5.Add(label_2, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.datepicker_ctrl_salary_month = wx.adv.DatePickerCtrl(self, wx.ID_ANY, style=wx.adv.DP_DEFAULT | wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        self.datepicker_ctrl_salary_month.SetMinSize((100, 25))
        sizer_5.Add(self.datepicker_ctrl_salary_month, 0, wx.ALL, 1)

        self.grid_salary_slip = wx.grid.Grid(self, wx.ID_ANY, size=(1, 1))
        self.grid_salary_slip.CreateGrid(10, 6)
        self.grid_salary_slip.SetRowLabelSize(30)
        self.grid_salary_slip.SetColLabelSize(30)
        self.grid_salary_slip.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid_salary_slip.SetColLabelValue(0, "Department")
        self.grid_salary_slip.SetColSize(0, 126)
        self.grid_salary_slip.SetColLabelValue(1, "Employee Number")
        self.grid_salary_slip.SetColSize(1, 137)
        self.grid_salary_slip.SetColLabelValue(2, "First Name")
        self.grid_salary_slip.SetColSize(2, 135)
        self.grid_salary_slip.SetColLabelValue(3, "Last Name")
        self.grid_salary_slip.SetColSize(3, 100)
        self.grid_salary_slip.SetColLabelValue(4, "Salary Month")
        self.grid_salary_slip.SetColSize(4, 100)
        self.grid_salary_slip.SetColLabelValue(5, "Salary Data Available?")
        self.grid_salary_slip.SetColSize(5, 141)
        self.grid_salary_slip.SetMinSize((300, 420))
        sizer_3.Add(self.grid_salary_slip, 0, wx.EXPAND , 0)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.btn_add_employee = wx.Button(self, wx.ID_ANY, "Add Employee(s)")
        sizer_2.Add(self.btn_add_employee, 0, 0, 0)

        self.btn_delete_employee = wx.Button(self, wx.ID_ANY, "Delete Employee(s)")
        sizer_2.Add(self.btn_delete_employee, 0, 0, 0)

        self.btn_refresh_grid = wx.Button(self, wx.ID_ANY, "Refresh Grid")
        sizer_2.Add(self.btn_refresh_grid, 0, 0, 0)

        self.btn_save_salary_slip = wx.Button(self, wx.ID_ANY, "Save Salary Slip")
        sizer_2.Add(self.btn_save_salary_slip, 0, 0, 0)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        sizer_2.Realize()

        self.SetSizer(sizer_1)

        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.add_employee_handler, self.btn_add_employee)
        self.Bind(wx.EVT_BUTTON, self.delete_employee_handler, self.btn_delete_employee)
        self.Bind(wx.EVT_BUTTON, self.refresh_grid_handler, self.btn_refresh_grid)
        self.Bind(wx.EVT_BUTTON, self.save_salary_handler, self.btn_save_salary_slip)
        # end wxGlade

    def add_employee_handler(self, event):  # wxGlade: SalaryAdvice.<event_handler>
        search_employee = WindowSearchEmployee(None, wx.ID_ANY, "", _sqlite_sqls=self.sqlite_sqls)
        return_value = search_employee.ShowModal()
        if return_value == wx.ID_OK and search_employee.return_value is not None:
            self.add_update_employee_salary_dict(_employee_dict=search_employee.return_value)
            self.refresh_grid_handler(None)
        search_employee.Destroy()

    def delete_employee_handler(self, event):  # wxGlade: SalaryAdvice.<event_handler>
        print("Event handler 'delete_employee_handler' not implemented!")
        event.Skip()

    def refresh_grid_handler(self, event):  # wxGlade: SalaryAdvice.<event_handler>
        if len(self.employee_salary_dict.keys()) == 0:
            return

        if self.grid_salary_slip.GetNumberRows() > 0:
            self.grid_salary_slip.DeleteRows(pos=0, numRows=self.grid_salary_slip.GetNumberRows())

        current_row = 0
        for employee_number in self.employee_salary_dict.keys():
            self.grid_salary_slip.AppendRows(1)
            self.grid_salary_slip.SetCellValue(current_row, 0, self.employee_salary_dict[employee_number]["department"])
            self.grid_salary_slip.SetCellValue(current_row, 1, employee_number)
            self.grid_salary_slip.SetCellValue(current_row, 2, self.employee_salary_dict[employee_number]["first_name"])
            self.grid_salary_slip.SetCellValue(current_row, 3, self.employee_salary_dict[employee_number]["last_name"])
            self.grid_salary_slip.SetCellValue(current_row, 4, self.employee_salary_dict[employee_number]["salary_month"])
            self.grid_salary_slip.SetCellValue(current_row, 5, str(self.employee_salary_dict[employee_number]["is_salary_data_available"]))
            current_row += 1

    def save_salary_handler(self, event):  # wxGlade: SalaryAdvice.<event_handler>
        salary_month = self.get_selected_month()
        UtilPayslip.generate_payslip(_salary_dict=self.employee_salary_dict, _sql_connection=self.sqlite_sqls,
                                     _salary_month=salary_month)
        event.Skip()

    def add_update_employee_salary_dict(self, _employee_dict):
        _employee_dict = json.loads(_employee_dict)
        salary_month = self.get_selected_month()
        is_salary_data_available = self.is_salary_data_available( _employee_number=_employee_dict["employee_number"], _salary_month=salary_month)
        self.employee_salary_dict[_employee_dict["employee_number"]] = {"department":_employee_dict["department"],
                                                                        "first_name":_employee_dict["first_name"],
                                                                        "last_name":_employee_dict["last_name"],
                                                                        "employment_start_date": _employee_dict["employment_start_date"],
                                                                        "salary_month":salary_month,
                                                                        "is_salary_data_available":is_salary_data_available}

    def is_salary_data_available(self,_employee_number, _salary_month):
        sql_salary_data_available = "select count(*) from employee_salary_data where employee_number = '{}' and salary_month='{}';".format(_employee_number, _salary_month)
        salary_record_count = self.sqlite_sqls.get_record_count(sql_salary_data_available)
        return (True if salary_record_count > 0 else False)

    def get_selected_month(self):
        wx_date = self.datepicker_ctrl_salary_month.GetValue()
        start_date = datetime(wx_date.GetYear(), wx_date.GetMonth() + 1, 1)
        start_date_str = start_date.strftime("%Y%m%d")
        end_date_str = UtilCommon.get_end_month_date(_date_yyyymmdd=start_date_str)
        return end_date_str

# end of class SalaryAdvice

# class MyApp(wx.App):
#     def OnInit(self):
#         self.dialog = SalaryAdvice(None, wx.ID_ANY, "")
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
