import wx

# begin wxGlade: dependencies
import wx.adv
import wx.grid
# end wxGlade

# begin wxGlade: extracode
# end wxGlade
from data_models.employee_model import EmployeeModel
from data_models.employee_model import CommonModel
import json
from datetime import datetime, timedelta
from collections import defaultdict
from util.util_common import UtilCommon


class SalaryEntry(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: SalaryEntry.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE

        self.sqlite_sqls = kwds['_sqlite_sqls']
        del kwds['_sqlite_sqls']

        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((1009, 869))
        self.SetTitle("Salary Entry")

        self.employee_data_as_list = EmployeeModel.get_all_employee_details_as_list(_sql_connection=self.sqlite_sqls)
        self.employee_data_as_list_filtered = self.employee_data_as_list.copy()
        self.employee_dict = CommonModel.get_dict_from_list(self.employee_data_as_list, "employee_number")
        department_cursor = self.sqlite_sqls.get_table_data("select * from department;")
        self.department_names_as_list = CommonModel.get_table_data_as_list(_data_cursor=department_cursor)
        duty_catalog_cursor = self.sqlite_sqls.get_table_data("select * from duty_catalog;")
        self.duty_catalog_as_list = CommonModel.get_table_data_as_list(_data_cursor=duty_catalog_cursor)
        self.duty_catalog_dict = CommonModel.get_dict_from_list(self.duty_catalog_as_list, "duty_code")

        department_list = self.get_department_list(_department_list=self.department_names_as_list)

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)

        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(sizer_4, 1, wx.EXPAND, 0)

        label_1 = wx.StaticText(self, wx.ID_ANY, "Department")
        sizer_4.Add(label_1, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.list_ctrl_department = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT)
        # self.list_ctrl_department = wx.ListCtrl(self, wx.LC_REPORT )
        # style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        # self.list_ctrl_department.SetMinSize((400, 169))
        self.list_ctrl_department.SetSize((400, 100))
        self.list_ctrl_department.EnableCheckBoxes()
        self.list_ctrl_department.AppendColumn("Department Name", format=wx.LIST_FORMAT_LEFT, width=100)
        sizer_4.Add(self.list_ctrl_department, 0, wx.EXPAND | wx.SHAPED, 0)

        label_2 = wx.StaticText(self, wx.ID_ANY, "Month")
        sizer_4.Add(label_2, 0, wx.ALIGN_CENTER_VERTICAL | wx.SHAPED, 0)

        self.datepicker_ctrl_date = wx.adv.DatePickerCtrl(self, wx.ID_ANY,
                                                          style=wx.adv.DP_DEFAULT | wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        sizer_4.Add(self.datepicker_ctrl_date, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        self.grid_employees = wx.grid.Grid(self, wx.ID_ANY, size=(1, 1))
        self.grid_employees.CreateGrid(0, 5)
        self.grid_employees.SetRowLabelSize(30)
        self.grid_employees.SetColLabelSize(30)
        self.grid_employees.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid_employees.SetColLabelValue(0, "Department")
        self.grid_employees.SetColSize(0, 100)
        self.grid_employees.SetColLabelValue(1, "Employee Number")
        self.grid_employees.SetColSize(1, 100)
        self.grid_employees.SetColLabelValue(2, "Last Name")
        self.grid_employees.SetColSize(2, 100)
        self.grid_employees.SetColLabelValue(3, "First Name")
        self.grid_employees.SetColSize(3, 100)
        self.grid_employees.SetColLabelValue(4, "Duty Name")
        self.grid_employees.SetColSize(4, 100)
        # self.grid_employees.SetMinSize((889, 200))
        self.grid_employees.SetSize((100, 200))
        sizer_3.Add(self.grid_employees, 0, wx.EXPAND | wx.FIXED_MINSIZE, 0)

        self.grid_salary_detail = wx.grid.Grid(self, wx.ID_ANY, size=(1, 1))
        self.grid_salary_detail.CreateGrid(0, 8)
        self.grid_salary_detail.SetRowLabelSize(30)
        self.grid_salary_detail.SetColLabelSize(30)
        self.grid_salary_detail.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid_salary_detail.SetColLabelValue(0, "Department")
        self.grid_salary_detail.SetColSize(0, 100)
        self.grid_salary_detail.SetColLabelValue(1, "Employee Number")
        self.grid_salary_detail.SetColSize(1, 100)
        self.grid_salary_detail.SetColLabelValue(2, "First Name")
        self.grid_salary_detail.SetColSize(2, 100)
        self.grid_salary_detail.SetColLabelValue(3, "Last Name")
        self.grid_salary_detail.SetColSize(3, 100)
        self.grid_salary_detail.SetColLabelValue(4, "Description")
        self.grid_salary_detail.SetColSize(4, 200)
        self.grid_salary_detail.SetColLabelValue(5, "Earning/Deduction")
        self.grid_salary_detail.SetColSize(5, 120)
        self.grid_salary_detail.SetColLabelValue(6, "Amount")
        self.grid_salary_detail.SetColSize(6, 100)
        self.grid_salary_detail.SetColLabelValue(7, "Entry/Type")
        self.grid_salary_detail.SetColSize(7, 100)
        # self.grid_salary_detail.SetMinSize((993, 420))
        self.grid_salary_detail.SetMinSize((223, 420))
        sizer_3.Add(self.grid_salary_detail, 1, wx.EXPAND, 0)

        sizer_3.Add((0, 0), 0, 0, 0)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.btn_delete_employee = wx.Button(self, wx.ID_ANY, "Delete Employee(s)")
        sizer_2.Add(self.btn_delete_employee, 0, 0, 0)

        self.btn_calculate_salaries = wx.Button(self, wx.ID_ANY, "Calculate Salaries")
        sizer_2.Add(self.btn_calculate_salaries, 0, 0, 0)

        self.btn_add_earning_deduction = wx.Button(self, wx.ID_ANY, "Add Earning/Deduction")
        sizer_2.Add(self.btn_add_earning_deduction, 0, 0, 0)

        self.btn_save = wx.Button(self, wx.ID_ANY, "Save")
        sizer_2.Add(self.btn_save, 0, 0, 0)

        self.btn_clear = wx.Button(self, wx.ID_ANY, "Clear")
        sizer_2.Add(self.btn_clear, 0, 0, 0)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        sizer_2.Realize()

        self.SetSizer(sizer_1)

        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Layout()

        # end wxGlade
        for department in department_list:
            self.list_ctrl_department.Append([department])

        for index in range(0, self.list_ctrl_department.GetItemCount()):
            self.list_ctrl_department.CheckItem(item=index, check=True)

        self.department_select_handler(event=None)

        self.Bind(wx.EVT_BUTTON, self.delete_employee_handler, self.btn_delete_employee)
        self.Bind(wx.EVT_BUTTON, self.calculate_duty_salaries_handler, self.btn_calculate_salaries)

        self.Bind(wx.EVT_LIST_ITEM_CHECKED, self.department_select_handler, self.list_ctrl_department)
        self.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.department_select_handler, self.list_ctrl_department)

    def department_select_handler(self, event):
        selected_department_list = []
        for index in range(0, self.list_ctrl_department.GetItemCount()):
            if self.list_ctrl_department.IsItemChecked(item=index):
                item = self.list_ctrl_department.GetItem(itemIdx=index)
                selected_department_list.append(item.Text)

        self.populate_employee_grid(_employee_data_as_list=self.employee_data_as_list_filtered,
                                    _selected_department_list=selected_department_list)

    def calculate_duty_salaries_handler(self, event):
        wx_date = self.datepicker_ctrl_date.GetValue()

        start_date = datetime(wx_date.GetYear(), wx_date.GetMonth() + 1, 1)
        start_date_str = start_date.strftime("%Y%m%d")
        end_date_str = UtilCommon.get_end_month_date(_date_yyyymmdd=start_date_str)

        # get the filtered employees numbers
        employee_list = []
        for item in self.employee_data_as_list_filtered:
            dict_item = json.loads(item)
            employee_list.append(dict_item["employee_number"])

        employee_number_comma_separated = "','".join(employee_list)
        employee_number_comma_separated = "'" + employee_number_comma_separated + "'"
        duty_sql = "select * from employee_duties where employee_number in ({}) and duty_date >= '{}' and duty_date <= '{}'".format(
            employee_number_comma_separated, start_date_str, end_date_str)
        duty_cursor = self.sqlite_sqls.get_table_data(duty_sql)
        duty_data_list = CommonModel.get_table_data_as_list(_data_cursor=duty_cursor)

        # construct dict from duty data list
        dict_emp_duty = defaultdict(lambda: -1)
        for duty_item in duty_data_list:
            dict_temp = json.loads(duty_item)
            if dict_emp_duty[dict_temp["employee_number"]] == -1:
                dict_emp_duty[dict_temp["employee_number"]] = [dict_temp["duty_date"]]
            else:
                dict_emp_duty[dict_temp["employee_number"]].append(dict_temp["duty_date"])

        # duty date
        for employee_number in dict_emp_duty.keys():
            if self.employee_dict[employee_number]["primary_duty_code"] == "DT104":  # monthly
                week_no = \
                datetime.strptime(UtilCommon.get_end_month_date(_date_yyyymmdd=start_date_str), '%Y%m%d').isocalendar()[
                    1]
                print("Week No : {}, Monthly Basic Salary - {}".format(week_no,
                                                                       self.employee_dict[employee_number]["salary"]))
                continue
            elif self.employee_dict[employee_number]["primary_duty_code"] == "DT103":  # daily
                duty_date_list = dict_emp_duty[employee_number]
                dict_week_dates = defaultdict(lambda: -1)
                for duty_date in duty_date_list:
                    week_no = datetime.strptime(duty_date, '%Y%m%d').isocalendar()[1]
                    if dict_week_dates[week_no] == -1:
                        dict_week_dates[week_no] = [duty_date]
                    else:
                        dict_week_dates[week_no].append(duty_date)

                print(employee_number)
                for week_no in dict_week_dates.keys():
                    print("Week No:{}, Dates : {}, Work Days : {}, Day Sal : {}, Weekly Salary ({} X {}) : {}"
                          .format(week_no, dict_week_dates[week_no], len(dict_week_dates[week_no]),
                                  self.employee_dict[employee_number]["salary"], len(dict_week_dates[week_no]),
                                  self.employee_dict[employee_number]["salary"], (
                                              int(len(dict_week_dates[week_no])) * float(
                                          self.employee_dict[employee_number]["salary"]))))
            else:
                print("salary code not implemented - code {}".format(self.employee_dict[employee_number]
                                                                     ["primary_duty_code"]))

        #  prepare the description
        # populate the table
        pass

    def add_earning_deduction_handler(self, event):
        pass

    def save_handler(self, event):
        pass

    def clear_handler(self, event):
        pass

    def get_department_list(self, _department_list):
        department_list = []
        for department in _department_list:
            dict_department = json.loads(department)
            department_list.append(dict_department["description"])
        return department_list

    # duplicate code
    def delete_employee_handler(self, event):
        new_employee_list = self.get_selected_employees_list()
        self.employee_data_as_list_filtered = new_employee_list
        self.department_select_handler(event=None)

    def get_selected_employees_list(self):
        selected_rows = self.grid_employees.GetSelectedRows()

        new_employee_list = []

        if len(selected_rows) == 0:
            return new_employee_list

        employee_number_list = []
        for row_index in selected_rows:
            employee_number_list.append(self.grid_employees.GetCellValue(row_index, 1))

        for item in self.employee_data_as_list_filtered:
            dict_item = json.loads(item)
            if dict_item["employee_number"] not in employee_number_list:
                new_employee_list.append(item)
        return new_employee_list

    def populate_employee_grid(self, _employee_data_as_list, _selected_department_list):
        # self.grid_employee_detail.ClearGrid()

        if self.grid_employees.GetNumberRows() > 0:
            self.grid_employees.DeleteRows(pos=0, numRows=self.grid_employees.GetNumberRows())

        # self.grid_employee_detail.AppendRows(self.grid_employee_detail.GetNumberRows())

        row_count = 0
        for employee in _employee_data_as_list:
            employee_dict = json.loads(employee)
            if employee_dict["department"] in _selected_department_list:
                self.grid_employees.AppendRows(1)
                self.grid_employees.SetCellValue(row_count, 0, employee_dict["department"])
                self.grid_employees.SetCellValue(row_count, 1, employee_dict["employee_number"])
                self.grid_employees.SetCellValue(row_count, 2, employee_dict["first_name"])
                self.grid_employees.SetCellValue(row_count, 3, employee_dict["last_name"])
                primary_duty_code = employee_dict["primary_duty_code"]
                duty_description = CommonModel.get_list_dict_value_from_key(_list_dict=self.duty_catalog_as_list,
                                                                            _key_column="duty_code",
                                                                            _expected_key_column_value=primary_duty_code,
                                                                            _value_column="duty_description"
                                                                            )
                self.grid_employees.SetCellValue(row_count, 4, duty_description)

                row_count += 1

        self.grid_employees.ClearSelection()

# end of class SalaryEntry

# class MyApp(wx.App):
#     def OnInit(self):
#         self.dlgSalary = SalaryEntry(None, wx.ID_ANY, "")
#         self.SetTopWindow(self.dlgSalary)
#         self.dlgSalary.ShowModal()
#         self.dlgSalary.Destroy()
#         return True
#
# # end of class MyApp
#
# if __name__ == "__main__":
#     app = MyApp(0)
#     app.MainLoop()
