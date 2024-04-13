import wx
import json
# begin wxGlade: dependencies
import wx.adv
import wx.grid
from data_models.employee_model import EmployeeModel
from data_models.common_model import CommonModel
from util.util_duty_initializer import UtilDutyInitializer
from datetime import datetime
# end wxGlade

# begin wxGlade: extracode
# end wxGlade

from collections import defaultdict

class DutyAllocation(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: DutyAllocation.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        sqlite_sqls = kwds['_sqlite_sqls']
        del kwds['_sqlite_sqls']

        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((1305, 897))
        self.SetTitle("TODO: Duty Allocation")

        self.employee_data_as_list = EmployeeModel.get_all_employee_details_as_list(_sql_connection=sqlite_sqls)
        self.employee_data_as_list_filtered = self.employee_data_as_list.copy()
        department_cursor = sqlite_sqls.get_table_data("select * from department;")
        self.department_names_as_list = CommonModel.get_table_data_as_list(_data_cursor=department_cursor)

        duty_catalog_cursor = sqlite_sqls.get_table_data("select * from duty_catalog;")
        self.duty_catalog_as_list = CommonModel.get_table_data_as_list(_data_cursor=duty_catalog_cursor)

        department_list = self.get_department_list(_department_list=self.department_names_as_list)

        self.employee_dict = CommonModel.get_dict_from_list( self.employee_data_as_list, "employee_number")
        self.duty_catalog_dict = CommonModel.get_dict_from_list( self.duty_catalog_as_list, "duty_code")

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND | wx.SHAPED, 0)

        sizer_4 = wx.BoxSizer(wx.VERTICAL)
        sizer_3.Add(sizer_4, 1, wx.EXPAND, 0)

        label_1 = wx.StaticText(self, wx.ID_ANY, "Employee Details")
        label_1.SetMinSize((150, 16))
        label_1.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        sizer_4.Add(label_1, 0, 0, 0)

        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(sizer_5, 0, wx.SHAPED, 0)

        label_2 = wx.StaticText(self, wx.ID_ANY, "Department(Filter)")
        sizer_5.Add(label_2, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.check_list_box_control = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT)
        self.check_list_box_control.SetMinSize((151, 90))
        self.check_list_box_control.EnableCheckBoxes()
        self.check_list_box_control.AppendColumn("Department Name", format=wx.LIST_FORMAT_LEFT, width=120)
        for department in department_list:
            self.check_list_box_control.Append([department])

        sizer_5.Add(self.check_list_box_control, 0, wx.ALIGN_CENTER_VERTICAL, 0)

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

        self.datepicker_ctrl_start_date = wx.adv.DatePickerCtrl(self, wx.ID_ANY,
                                                                style=wx.adv.DP_DEFAULT | wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        self.datepicker_ctrl_start_date.SetMinSize((120, 25))
        grid_sizer_1.Add(self.datepicker_ctrl_start_date, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        label_5 = wx.StaticText(self, wx.ID_ANY, "End Date:")
        grid_sizer_1.Add(label_5, 6, 0, 0)

        self.datepicker_ctrl_end_date = wx.adv.DatePickerCtrl(self, wx.ID_ANY,
                                                              style=wx.adv.DP_DEFAULT | wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        self.datepicker_ctrl_end_date.SetMinSize((120, 25))
        grid_sizer_1.Add(self.datepicker_ctrl_end_date, 0, 0, 0)

        sizer_12 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, ""), wx.HORIZONTAL)
        sizer_7.Add(sizer_12, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM | wx.SHAPED, 0)

        self.search_control_department = wx.SearchCtrl(self, wx.ID_ANY, "")
        self.search_control_department.SetMinSize((130, 23))
        self.search_control_department.ShowCancelButton(True)
        sizer_12.Add(self.search_control_department, 0, 0, 0)

        self.search_control_identity = wx.SearchCtrl(self, wx.ID_ANY, "")
        self.search_control_identity.SetMinSize((130, 23))
        self.search_control_identity.ShowCancelButton(True)
        sizer_12.Add(self.search_control_identity, 0, 0, 0)

        self.search_control_name = wx.SearchCtrl(self, wx.ID_ANY, "")
        self.search_control_name.SetMinSize((130, 23))
        self.search_control_name.ShowCancelButton(True)
        sizer_12.Add(self.search_control_name, 0, 0, 0)

        self.search_control_duty_name = wx.SearchCtrl(self, wx.ID_ANY, "")
        self.search_control_duty_name.SetMinSize((130, 23))
        self.search_control_duty_name.ShowCancelButton(True)
        sizer_12.Add(self.search_control_duty_name, 0, 0, 0)

        self.search_control_duty_date = wx.SearchCtrl(self, wx.ID_ANY, "")
        self.search_control_duty_date.SetMinSize((130, 23))
        self.search_control_duty_date.ShowCancelButton(True)
        sizer_12.Add(self.search_control_duty_date, 0, 0, 0)

        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_8, 1, wx.EXPAND | wx.RESERVE_SPACE_EVEN_IF_HIDDEN, 0)

        self.grid_employee_detail = wx.grid.Grid(self, wx.ID_ANY, size=(1, 1))
        self.grid_employee_detail.CreateGrid(10, 5)
        self.grid_employee_detail.SetRowLabelSize(30)
        self.grid_employee_detail.SetColLabelSize(30)
        self.grid_employee_detail.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid_employee_detail.SetColLabelValue(0, "Department")
        self.grid_employee_detail.SetColSize(0, 100)
        self.grid_employee_detail.SetColLabelValue(1, "Employee Number")
        self.grid_employee_detail.SetColSize(1, 120)
        self.grid_employee_detail.SetColLabelValue(2, "First Name")
        self.grid_employee_detail.SetColSize(2, 100)
        self.grid_employee_detail.SetColLabelValue(3, "Last Name")
        self.grid_employee_detail.SetColSize(3, 100)
        self.grid_employee_detail.SetMinSize((634, 575))
        self.grid_employee_detail.SetColLabelValue(4, "Duty")
        self.grid_employee_detail.SetColSize(4, 120)
        self.grid_employee_detail.SetMinSize((634, 575))
        sizer_8.Add(self.grid_employee_detail, 1, wx.EXPAND, 0)

        self.grid_duty_detail = wx.grid.Grid(self, wx.ID_ANY, size=(1, 1))
        self.grid_duty_detail.CreateGrid(10, 5)
        self.grid_duty_detail.SetRowLabelSize(30)
        self.grid_duty_detail.SetColLabelSize(30)
        self.grid_duty_detail.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid_duty_detail.SetColLabelValue(0, "Department")
        self.grid_duty_detail.SetColSize(0, 110)
        self.grid_duty_detail.SetColLabelValue(1, "Employee Number")
        self.grid_duty_detail.SetColSize(1, 120)
        self.grid_duty_detail.SetColLabelValue(2, "Name")
        self.grid_duty_detail.SetColSize(2, 180)
        self.grid_duty_detail.SetColLabelValue(3, "Duty Name")
        self.grid_duty_detail.SetColSize(3, 110)
        self.grid_duty_detail.SetColLabelValue(4, "Duty Date")
        self.grid_duty_detail.SetColSize(4, 110)
        self.grid_duty_detail.SetMinSize((650, 575))
        sizer_8.Add(self.grid_duty_detail, 1, wx.EXPAND, 0)

        sizer_9 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_9, 1, wx.SHAPED, 0)

        sizer_10 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Employees"), wx.HORIZONTAL)
        sizer_9.Add(sizer_10, 1, wx.FIXED_MINSIZE, 0)

        self.btn_clear = wx.Button(self, wx.ID_ANY, "Clear")
        sizer_10.Add(self.btn_clear, 0, 0, 0)

        self.btn_delete_employee = wx.Button(self, wx.ID_ANY, "Delete")
        sizer_10.Add(self.btn_delete_employee, 0, 0, 0)

        self.btn_reload_all_employees = wx.Button(self, wx.ID_ANY, "Reload All")
        sizer_10.Add(self.btn_reload_all_employees, 0, 0, 0)

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
        for index in range(0, self.check_list_box_control.GetItemCount()):
            self.check_list_box_control.CheckItem(item=index, check=True)

        self.department_select_handler(event=None)

        self.Bind(wx.EVT_LIST_ITEM_CHECKED, self.department_select_handler, self.check_list_box_control)
        self.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.department_select_handler, self.check_list_box_control)
        self.Bind(wx.EVT_BUTTON, self.delete_employee_handler, self.btn_delete_employee)
        self.Bind(wx.EVT_BUTTON, self.reload_all_employees_handler, self.btn_reload_all_employees)

        self.Bind(wx.EVT_BUTTON, self.allocate_duties, self.btn_duty_generate)
        # end wxGlade

    def get_department_list(self, _department_list):
        department_list = []
        for department in _department_list:
            dict_department = json.loads(department)
            department_list.append(dict_department["description"])
        return department_list

    def populate_employee_grid(self, _employee_data_as_list, _selected_department_list):
        self.grid_employee_detail.ClearGrid()
        row_count = 0
        for employee in _employee_data_as_list:
            employee_dict = json.loads(employee)
            if employee_dict["department"] in _selected_department_list:
                self.grid_employee_detail.SetCellValue(row_count, 0, employee_dict["department"])
                self.grid_employee_detail.SetCellValue(row_count, 1, employee_dict["employee_number"])
                self.grid_employee_detail.SetCellValue(row_count, 2, employee_dict["first_name"])
                self.grid_employee_detail.SetCellValue(row_count, 3, employee_dict["last_name"])
                primary_duty_code = employee_dict["primary_duty_code"]
                duty_description = CommonModel.get_list_dict_value_from_key(_list_dict=self.duty_catalog_as_list,
                                                                            _key_column="duty_code",
                                                                            _expected_key_column_value=primary_duty_code,
                                                                            _value_column="duty_description"
                                                                            )
                self.grid_employee_detail.SetCellValue(row_count, 4, duty_description)

                row_count += 1

        self.grid_employee_detail.ClearSelection()

    def department_select_handler(self, event):
        selected_department_list = []
        for index in range(0, self.check_list_box_control.GetItemCount()):
            if self.check_list_box_control.IsItemChecked(item=index):
                item = self.check_list_box_control.GetItem(itemIdx=index)
                selected_department_list.append(item.Text)

        self.populate_employee_grid(_employee_data_as_list=self.employee_data_as_list_filtered,
                                    _selected_department_list=selected_department_list)

    def delete_employee_handler(self, event):
        new_employee_list = self.get_selected_employees_list()
        self.employee_data_as_list_filtered = new_employee_list
        self.department_select_handler(event=None)

    def get_selected_employees_list(self):
        selected_rows = self.grid_employee_detail.GetSelectedRows()

        new_employee_list = []

        if len(selected_rows) == 0:
            return new_employee_list

        employee_number_list = []
        for row_index in selected_rows:
            employee_number_list.append(self.grid_employee_detail.GetCellValue(row_index, 1))

        for item in self.employee_data_as_list_filtered:
            dict_item = json.loads(item)
            if dict_item["employee_number"] not in employee_number_list:
                new_employee_list.append(item)
        return new_employee_list

    def reload_all_employees_handler(self, event):
        for index in range(0, self.check_list_box_control.GetItemCount()):
            self.check_list_box_control.CheckItem(item=index, check=True)

        self.employee_data_as_list_filtered = self.employee_data_as_list
        self.department_select_handler(event=None)

    def allocate_duties(self, event):
        employee_number_list = []
        for index in range(0, self.grid_employee_detail.GetNumberRows()):
            if self.grid_employee_detail.GetCellValue(index, 1) != "":
                employee_number_list.append(self.grid_employee_detail.GetCellValue(index, 1))

        employees_list = []
        for item in self.employee_data_as_list_filtered:
            dict_item = json.loads(item)
            if dict_item["employee_number"] in employee_number_list:
                employees_list.append(item)

        minimum_daily_required_resource_count = 2
        dict_duty_schedule, dict_emp_leaves = self.get_duties_and_leaves(_employee_number_list=employee_number_list,
                                                                         _minimum_daily_required_resource_count=minimum_daily_required_resource_count)
        self.populate_duties(_dict_duties=dict_duty_schedule,
                             _minimum_daily_required_resource_count=minimum_daily_required_resource_count)

    def populate_duties(self, _dict_duties, _minimum_daily_required_resource_count):
        print(_dict_duties)
        if len(_dict_duties.keys()) == 0:
            return

        if self.grid_duty_detail.GetNumberRows() > 0:
            self.grid_duty_detail.DeleteRows(pos=0, numRows=self.grid_duty_detail.GetNumberRows())

        grid_rows_count = len(_dict_duties.keys()) * _minimum_daily_required_resource_count

        self.grid_duty_detail.AppendRows(grid_rows_count)

        current_row = 0
        for date_key in _dict_duties.keys():
            for employee_number in _dict_duties[date_key]:
                self.grid_duty_detail.SetCellValue(current_row, 0, self.employee_dict[employee_number]["department"])
                self.grid_duty_detail.SetCellValue(current_row, 1, employee_number)
                self.grid_duty_detail.SetCellValue(current_row, 2, self.employee_dict[employee_number]["first_name"])
                duty_code = self.employee_dict[employee_number]["primary_duty_code"]
                duty_description  = self.duty_catalog_dict[duty_code]["duty_description"]
                self.grid_duty_detail.SetCellValue(current_row, 3, duty_description)
                self.grid_duty_detail.SetCellValue(current_row, 4, date_key)

                current_row += 1



    def get_duties_and_leaves(self, _employee_number_list, _minimum_daily_required_resource_count):
        wx_start_date = self.datepicker_ctrl_start_date.GetValue()
        wx_end_date = self.datepicker_ctrl_end_date.GetValue()
        start_date = "{}{:02d}{:02d}".format(wx_start_date.GetYear(), wx_start_date.GetMonth() + 1,
                                             wx_start_date.GetDay())
        end_date = "{}{:02d}{:02d}".format(wx_end_date.GetYear(), wx_end_date.GetMonth() + 1,
                                           wx_end_date.GetDay())
        list_company_holidays = ['20240402', '20240415', '20240419']
        dict_duty_schedule, dict_emp_leaves = UtilDutyInitializer.assign_duty_round_robin(
            _list_emp_ids=_employee_number_list,
            _from_date=start_date,
            _to_date=end_date,
            _list_company_holidays=list_company_holidays,
            _minimum_daily_required_resource_count=_minimum_daily_required_resource_count)

        return dict_duty_schedule, dict_emp_leaves


    # def get_duty_name_from_duty_code(self, ):
    #     pass
    #

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
