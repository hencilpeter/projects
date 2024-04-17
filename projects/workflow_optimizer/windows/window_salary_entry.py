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

        self.salary_dict = defaultdict(lambda: -1)

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

        self.Bind(wx.EVT_BUTTON, self.save_handler, self.btn_save)
        self.Bind(wx.EVT_BUTTON, self.clear_handler, self.btn_clear)

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

        salary_dict = defaultdict(lambda: -1)
        # duty date
        for employee_number in dict_emp_duty.keys():
            inesrt_sql_list = []
            duty_code = self.employee_dict[employee_number]["primary_duty_code"]
            salary_type = self.duty_catalog_dict[duty_code]["salary_type"]
            # duty_name =
            if salary_type == "Monthly":  # monthly
                print("implemented code : {}".format(self.employee_dict[employee_number]["primary_duty_code"]))
                week_no = \
                    datetime.strptime(UtilCommon.get_end_month_date(_date_yyyymmdd=start_date_str),
                                      '%Y%m%d').isocalendar()[
                        1]
                salary = float(self.employee_dict[employee_number]["salary"])
                description = "Basic Monthly Salary - {}".format(self.employee_dict[employee_number]["salary"])

                # inesrt_sql_list.append("INSERT INTO  employee_salary_data(employee_number, salary_month, week_number,"
                #                        "description, earning_type, amount) VALUES('{}','{}', {}, '{}', '{}',{});".format(
                #     employee_number, end_date_str, week_no, description, "auto", self.employee_dict[employee_number]["salary"]))
                dict_entry = self.get_salary_entry_dict(_salary_entry_key=week_no, _salary_month=end_date_str,
                                                        _description=description, _calculation_type="auto",
                                                        _entry_type="earning",
                                                        _amount=salary)
                UtilCommon.assign_or_append_dict(_dict=salary_dict, _dict_key=employee_number, _dict_value=dict_entry)
            elif salary_type == "Daily":  # daily
                print("implemented code : {}".format(self.employee_dict[employee_number]["primary_duty_code"]))
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
                    number_of_days = len(dict_week_dates[week_no])
                    salary = float(self.employee_dict[employee_number]["salary"])
                    description = "Week No:{}, Dates : {}, Work Days : {}, Day Sal : {}, Weekly Salary ({} X {}) : {}" \
                        .format(week_no, dict_week_dates[week_no], number_of_days,
                                self.employee_dict[employee_number]["salary"], number_of_days,
                                self.employee_dict[employee_number]["salary"], (number_of_days * salary))
                    description = description.replace("'","")
                    # print(description)
                    # inesrt_sql_list.append("INSERT INTO  employee_salary_data(employee_number, salary_month, week_number, " \
                    #              "description, earning_type, amount) VALUES('{}','{}', {}, '{}', '{}',{});".format(employee_number, end_date_str, week_no, description, "auto", (number_of_days * salary)))
                    dict_entry = self.get_salary_entry_dict(_salary_entry_key=week_no, _salary_month=end_date_str,
                                                            _description=description, _calculation_type="auto",
                                                            _entry_type="earning",
                                                            _amount=number_of_days * salary)
                    UtilCommon.assign_or_append_dict(_dict=salary_dict, _dict_key=employee_number,
                                                     _dict_value=dict_entry)
            else:
                print("salary code not implemented - code {}".format(self.employee_dict[employee_number]
                                                                     ["primary_duty_code"]))

        self.salary_dict = salary_dict
        self.populate_duties_grid(_salary_dict=salary_dict)

    def add_earning_deduction_handler(self, event):

        pass

    def save_handler(self, event):
        if len(self.salary_dict.keys()) == 0:
            return

        employee_numbers = "','".join(self.salary_dict.keys())
        employee_numbers = "'" + employee_numbers + "'"
        wx_date = self.datepicker_ctrl_date.GetValue()
        start_date = datetime(wx_date.GetYear(), wx_date.GetMonth() + 1, 1)
        start_date_str = start_date.strftime("%Y%m%d")
        end_date_str = UtilCommon.get_end_month_date(_date_yyyymmdd=start_date_str)

        # delete the old data if any
        delete_sql = "delete from employee_salary_data where employee_number in ({}) and salary_month = '{}';"\
            .format(employee_numbers, end_date_str)
        self.sqlite_sqls.execute_and_commit_sql(delete_sql)

        # save new data
        insert_salary_data_sql = []
        for employee_number in self.salary_dict.keys():
            salary_entry_list = self.salary_dict[employee_number]
            for salary_entry in salary_entry_list:
                for salary_id_key in salary_entry.keys():
                    insert_salary_data_sql.append("insert into employee_salary_data(employee_number,salary_month,week_number,description,calculation_type,entry_type,amount) "
                                                  "values('{}', '{}', {}, '{}', '{}', '{}', {});".format(employee_number,end_date_str, salary_id_key,
                                                                                                               salary_entry[salary_id_key]["description"],
                                                                                                               salary_entry[salary_id_key]["calculation_type"],
                                                                                                               salary_entry[salary_id_key]["entry_type"],
                                                                                                               salary_entry[salary_id_key]["amount"] ))

        build_insert_sql = ''.join(insert_salary_data_sql)
        print(build_insert_sql)
        self.sqlite_sqls.executescript_and_commit_sql(build_insert_sql)
        dial = wx.MessageDialog(self, "Salary Data Saved Successfully...", "Salary Data", wx.OK | wx.STAY_ON_TOP | wx.CENTRE)
        dial.ShowModal()

        pass

    def clear_handler(self, event):
        if self.grid_salary_detail.GetNumberRows() > 0:
            self.grid_salary_detail.DeleteRows(pos=0, numRows=self.grid_salary_detail.GetNumberRows())

        if len(self.salary_dict.keys()) != 0:
            self.salary_dict.clear()

        self.populate_duties_grid(_salary_dict=self.salary_dict)


    def get_salary_entry_dict(self, _salary_entry_key, _salary_month, _description, _calculation_type, _entry_type,
                              _amount):
        salary_entry_dict = defaultdict(lambda: -1)
        salary_entry_dict[_salary_entry_key] = {"salary_month": _salary_month, "description": _description,
                                                "calculation_type": _calculation_type,
                                                "entry_type": _entry_type, "amount": _amount}
        return salary_entry_dict

    def populate_duties_grid(self, _salary_dict):
        if len(_salary_dict.keys()) == 0:
            return
        if self.grid_salary_detail.GetNumberRows() > 0:
            self.grid_salary_detail.DeleteRows(pos=0, numRows=_salary_dict.GetNumberRows())

        current_row = 0
        for employee_number in _salary_dict.keys():
            salary_entry_list = _salary_dict[employee_number]
            for salary_entry in salary_entry_list:
                for salary_id_key in salary_entry.keys():
                    self.grid_salary_detail.AppendRows(1)
                    self.grid_salary_detail.SetCellValue(current_row, 0,
                                                         self.employee_dict[employee_number]["department"])
                    self.grid_salary_detail.SetCellValue(current_row, 1, employee_number)
                    self.grid_salary_detail.SetCellValue(current_row, 2,
                                                         self.employee_dict[employee_number]["first_name"])
                    self.grid_salary_detail.SetCellValue(current_row, 3,
                                                         self.employee_dict[employee_number]["last_name"])
                    self.grid_salary_detail.SetCellValue(current_row, 4,
                                                         salary_entry[salary_id_key]["description"])
                    self.grid_salary_detail.SetCellValue(current_row, 5, salary_entry[salary_id_key]["entry_type"])

                    self.grid_salary_detail.SetCellValue(current_row, 6, str(salary_entry[salary_id_key]["amount"]))

                    self.grid_salary_detail.SetCellValue(current_row, 7,
                                                         str(salary_entry[salary_id_key]["calculation_type"]))
                    current_row += 1

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
