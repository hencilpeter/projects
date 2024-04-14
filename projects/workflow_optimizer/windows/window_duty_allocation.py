import wx
import json
# begin wxGlade: dependencies
import wx.adv
import wx.grid
from data_models.employee_model import EmployeeModel
from data_models.common_model import CommonModel
from util.util_duty_initializer import UtilDutyInitializer
from windows.window_insert_duty import WindowInsertDuty
from datetime import datetime
# end wxGlade

# begin wxGlade: extracode
# end wxGlade

from collections import defaultdict

class DutyAllocation(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: DutyAllocation.__init__

        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        self.sqlite_sqls = kwds['_sqlite_sqls']
        del kwds['_sqlite_sqls']

        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((1305, 897))
        self.SetTitle("TODO: Duty Allocation")

        self.employee_data_as_list = EmployeeModel.get_all_employee_details_as_list(_sql_connection=self.sqlite_sqls)
        self.employee_data_as_list_filtered = self.employee_data_as_list.copy()
        department_cursor = self.sqlite_sqls.get_table_data("select * from department;")
        self.department_names_as_list = CommonModel.get_table_data_as_list(_data_cursor=department_cursor)

        duty_catalog_cursor = self.sqlite_sqls.get_table_data("select * from duty_catalog;")
        self.duty_catalog_as_list = CommonModel.get_table_data_as_list(_data_cursor=duty_catalog_cursor)

        department_list = self.get_department_list(_department_list=self.department_names_as_list)

        self.employee_dict = CommonModel.get_dict_from_list( self.employee_data_as_list, "employee_number")
        self.duty_catalog_dict = CommonModel.get_dict_from_list( self.duty_catalog_as_list, "duty_code")

        self.company_holidays_list = self.sqlite_sqls.get_single_column_list("company_holidays", "holiday_date")
        self.start_date = ""
        self.end_date = ""
        self.dict_duty_schedule = defaultdict(lambda :-1)
        self.duty_count = 0
        self.dict_duty_schedule_filtered = defaultdict(lambda :-1)
        self.duty_count_filtered = 0

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

        self.search_control_employee_number = wx.SearchCtrl(self, wx.ID_ANY, "")
        self.search_control_employee_number.SetMinSize((130, 23))
        self.search_control_employee_number.ShowCancelButton(True)
        sizer_12.Add(self.search_control_employee_number, 0, 0, 0)

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
        self.grid_duty_detail.CreateGrid(0, 5)
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

        self.btn_load_duties = wx.Button(self, wx.ID_ANY, "Load Duties")
        sizer_11.Add(self.btn_load_duties, 0, 0, 0)

        self.btn_duty_delete = wx.Button(self, wx.ID_ANY, "Delete Duty")
        sizer_11.Add(self.btn_duty_delete, 0, 0, 0)
        self.btn_duty_insert = wx.Button(self, wx.ID_ANY, "Insert Duty")
        sizer_11.Add(self.btn_duty_insert, 0, 0, 0)
        self.btn_duty_swap = wx.Button(self, wx.ID_ANY, "Swap Duties")
        sizer_11.Add(self.btn_duty_swap, 0, 0, 0)


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
        self.Bind(wx.EVT_BUTTON, self.save_duties, self.btn_duty_save)
        self.Bind(wx.EVT_BUTTON, self.load_duties, self.btn_load_duties)
        self.Bind(wx.EVT_BUTTON, self.load_clean_duties, self.btn_duty_clear)

        #
        self.Bind(wx.EVT_BUTTON, self.delete_duty_handler, self.btn_duty_delete)
        self.Bind(wx.EVT_BUTTON, self.insert_duty_handler, self.btn_duty_insert)
        self.Bind(wx.EVT_BUTTON, self.swap_duty_handler, self.btn_duty_swap)


        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.handler_filter_duties_grid, self.search_control_department)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.handler_filter_duties_grid, self.search_control_department)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.handler_filter_duties_grid, self.search_control_employee_number)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.handler_filter_duties_grid, self.search_control_employee_number)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.handler_filter_duties_grid, self.search_control_name)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.handler_filter_duties_grid, self.search_control_name)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.handler_filter_duties_grid, self.search_control_duty_name)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.handler_filter_duties_grid, self.search_control_duty_name)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.handler_filter_duties_grid, self.search_control_duty_date)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.handler_filter_duties_grid, self.search_control_duty_date)

        # end wxGlade

    def get_department_list(self, _department_list):
        department_list = []
        for department in _department_list:
            dict_department = json.loads(department)
            department_list.append(dict_department["description"])
        return department_list

    def populate_employee_grid(self, _employee_data_as_list, _selected_department_list):
        # self.grid_employee_detail.ClearGrid()

        if self.grid_employee_detail.GetNumberRows() > 0:
            self.grid_employee_detail.DeleteRows(pos=0, numRows=self.grid_employee_detail.GetNumberRows())

        # self.grid_employee_detail.AppendRows(self.grid_employee_detail.GetNumberRows())

        row_count = 0
        for employee in _employee_data_as_list:
            employee_dict = json.loads(employee)
            if employee_dict["department"] in _selected_department_list:
                self.grid_employee_detail.AppendRows(1)
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

    # Duties section
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

        wx_start_date = self.datepicker_ctrl_start_date.GetValue()
        wx_end_date = self.datepicker_ctrl_end_date.GetValue()
        self.start_date = "{}{:02d}{:02d}".format(wx_start_date.GetYear(), wx_start_date.GetMonth() + 1,
                                                  wx_start_date.GetDay())
        self.end_date = "{}{:02d}{:02d}".format(wx_end_date.GetYear(), wx_end_date.GetMonth() + 1,
                                                wx_end_date.GetDay())

        # iterate employees list
        # list_company_holidays = ['20240402', '20240415', '20240419']

        dict_employee_duty_code = defaultdict(lambda: -1)
        for employee_number in employee_number_list:
            if dict_employee_duty_code[self.employee_dict[employee_number]["primary_duty_code"]] == -1:
                dict_employee_duty_code[self.employee_dict[employee_number]["primary_duty_code"]] = [employee_number]
            else:
                dict_employee_duty_code[self.employee_dict[employee_number]["primary_duty_code"]].append(
                    employee_number)

        dict_main_duty_schedule = defaultdict(lambda: -1)
        for duty_code in dict_employee_duty_code:
            current_duty_employee_number_list = dict_employee_duty_code[duty_code]
            current_duty_minimum_resource_count = int(self.duty_catalog_dict[duty_code]["default_resource_count"])

            # iterate employees list
            dict_duty_schedule, dict_emp_leaves = self.get_duties_and_leaves(_start_date=self.start_date,
                                                                             _end_date=self.end_date,
                                                                             _employee_number_list=current_duty_employee_number_list,
                                                                             _minimum_daily_required_resource_count=current_duty_minimum_resource_count,
                                                                             _list_company_holidays=self.company_holidays_list)

            dict_main_duty_schedule = UtilDutyInitializer.merge_two_duty_dictionaries(
                _dict_duty_schedule1=dict_main_duty_schedule,
                _dict_duty_schedule2=dict_duty_schedule)


        duty_count = self.get_duty_count(_dict_duty_schedule=dict_main_duty_schedule)
        self.update_duty_buffer(_dict_duty_schedule=dict_main_duty_schedule, _duty_count=duty_count)
        self.populate_duties_from_dict(_dict_duties=dict_main_duty_schedule,
                                       _duty_count=duty_count)



        # prepare dict with duty name as key
        # prepare new dict with employee list for each duty
        # for loop - for each duty type
        # read min number of resources from dict
        # merge the dicts
        #finally update the buffer and populate the dict


        # minimum_daily_required_resource_count = 2
        # wx_start_date = self.datepicker_ctrl_start_date.GetValue()
        # wx_end_date = self.datepicker_ctrl_end_date.GetValue()
        # self.start_date = "{}{:02d}{:02d}".format(wx_start_date.GetYear(), wx_start_date.GetMonth() + 1,
        #                                           wx_start_date.GetDay())
        # self.end_date = "{}{:02d}{:02d}".format(wx_end_date.GetYear(), wx_end_date.GetMonth() + 1,
        #                                         wx_end_date.GetDay())
        #
        # # iterate employees list
        # list_company_holidays = ['20240402', '20240415', '20240419']
        # dict_duty_schedule, dict_emp_leaves = self.get_duties_and_leaves(_start_date=self.start_date,
        #                                                                  _end_date=self.end_date,
        #                                                                  _employee_number_list=employee_number_list,
        #                                                                  _list_company_holidays = list_company_holidays,
        #                                                                  _minimum_daily_required_resource_count=minimum_daily_required_resource_count)
        # duty_count = self.get_duty_count(_dict_duty_schedule=dict_duty_schedule)
        # self.update_duty_buffer(_dict_duty_schedule=dict_duty_schedule, _duty_count=duty_count)
        # self.populate_duties_from_dict(_dict_duties=dict_duty_schedule,
        #                                _duty_count=duty_count)

        ############## old code
        # employee_number_list = []
        # for index in range(0, self.grid_employee_detail.GetNumberRows()):
        #     if self.grid_employee_detail.GetCellValue(index, 1) != "":
        #         employee_number_list.append(self.grid_employee_detail.GetCellValue(index, 1))
        #
        #
        # employees_list = []
        # for item in self.employee_data_as_list_filtered:
        #     dict_item = json.loads(item)
        #     if dict_item["employee_number"] in employee_number_list:
        #         employees_list.append(item)
        #
        # minimum_daily_required_resource_count = 2
        # wx_start_date = self.datepicker_ctrl_start_date.GetValue()
        # wx_end_date = self.datepicker_ctrl_end_date.GetValue()
        # self.start_date = "{}{:02d}{:02d}".format(wx_start_date.GetYear(), wx_start_date.GetMonth() + 1,
        #                                      wx_start_date.GetDay())
        # self.end_date = "{}{:02d}{:02d}".format(wx_end_date.GetYear(), wx_end_date.GetMonth() + 1,
        #                                    wx_end_date.GetDay())
        #
        # # iterate employees list
        # dict_duty_schedule, dict_emp_leaves = self.get_duties_and_leaves(_start_date=self.start_date, _end_date=self.end_date,
        #                                                                       _employee_number_list=employee_number_list,
        #                                                                  _minimum_daily_required_resource_count=minimum_daily_required_resource_count)
        # duty_count = self.get_duty_count(_dict_duty_schedule=dict_duty_schedule)
        # self.update_duty_buffer(_dict_duty_schedule=dict_duty_schedule, _duty_count=duty_count)
        # self.populate_duties_from_dict(_dict_duties=dict_duty_schedule,
        #                      _duty_count=duty_count)



    def save_duties(self, event):
        unique_employee_number_list = self.get_unique_employee_number_list()
        formatted_employee_numbers = "','".join(unique_employee_number_list)
        formatted_employee_numbers = "'" + formatted_employee_numbers + "'"
        # delete_sql = "delete from employee_duties where employee_number in ({}) and duty_date >= '{}' and duty_date <= '{}';" \
        #     .format(formatted_employee_numbers, datetime.strptime(self.start_date, '%Y%m%d').strftime('%Y-%m-%d'),
        #             datetime.strptime(self.end_date, '%Y%m%d').strftime('%Y-%m-%d'))
        delete_sql = "delete from employee_duties where employee_number in ({}) and duty_date >= '{}' and duty_date <= '{}';" \
            .format(formatted_employee_numbers, self.start_date, self.end_date)

        # delete the old records
        self.sqlite_sqls.execute_and_commit_sql(delete_sql)

        # insert new records
        insert_sql_list = []
        # for row_number in range(0, self.grid_duty_detail.GetNumberRows()):
        #     insert_sql_list.append(
        #         "insert into employee_duties (employee_number, duty_date, duty_description) values('{}','{}','{}');" \
        #         .format(self.grid_duty_detail.GetCellValue(row_number, 1),
        #                 self.grid_duty_detail.GetCellValue(row_number, 4),
        #                 ""))
        for duty_date in self.dict_duty_schedule.keys():
            for employee_number in self.dict_duty_schedule[duty_date]:
                insert_sql_list.append(
                        "insert into employee_duties (employee_number, duty_date, duty_description) values('{}','{}','{}');" \
                        .format(employee_number, duty_date,""))

        build_insert_sql = ''.join(insert_sql_list)
        self.sqlite_sqls.executescript_and_commit_sql(build_insert_sql)
        dial = wx.MessageDialog(self, "Duties Saved Successfully...", "Duties", wx.OK | wx.STAY_ON_TOP | wx.CENTRE)
        dial.ShowModal()

    def load_duties(self, event):
        employee_number_list = []
        for index in range(0, self.grid_employee_detail.GetNumberRows()):
            if self.grid_employee_detail.GetCellValue(index, 1) != "":
                employee_number_list.append(self.grid_employee_detail.GetCellValue(index, 1))
        wx_start_date = self.datepicker_ctrl_start_date.GetValue()
        wx_end_date = self.datepicker_ctrl_end_date.GetValue()
        self.start_date = "{}{:02d}{:02d}".format(wx_start_date.GetYear(), wx_start_date.GetMonth() + 1,
                                                  wx_start_date.GetDay())
        self.end_date = "{}{:02d}{:02d}".format(wx_end_date.GetYear(), wx_end_date.GetMonth() + 1,
                                                wx_end_date.GetDay())

        employee_number_str = "','".join(employee_number_list)
        employee_number_str = "'" + employee_number_str + "'"
        # sql = "select * from employee_duties where employee_number in ({}) and duty_date >= '{}' and duty_date <= '{}'"\
        #     .format(employee_number_str, datetime.strptime(self.start_date, '%Y%m%d').strftime('%Y-%m-%d'),
        #             datetime.strptime(self.end_date, '%Y%m%d').strftime('%Y-%m-%d'))
        sql = "select * from employee_duties where employee_number in ({}) and duty_date >= '{}' and duty_date <= '{}'" \
            .format(employee_number_str, self.start_date, self.end_date)

        employee_duties_cursor = self.sqlite_sqls.get_table_data(sql)
        employee_duties_list = CommonModel.get_table_data_as_list(_data_cursor=employee_duties_cursor)
        dict_duty_schedule, duty_count = self.get_duty_dict_from_table_records(_table_duties_list=employee_duties_list)
        self.update_duty_buffer(_dict_duty_schedule=dict_duty_schedule, _duty_count=duty_count)
        self.populate_duties_from_dict(_dict_duties= dict_duty_schedule, _duty_count= duty_count)


    def load_clean_duties(self, event):
        self.grid_duty_detail.ClearGrid()
        self.start_date = ""
        self.end_date = ""
        self.dict_duty_schedule = defaultdict(lambda :-1)
        self.dict_duty_schedule_filtered  = defaultdict(lambda :-1)

    def handler_filter_duties_grid(self, event):
        search_department_name = self.search_control_department.GetValue()
        search_employee_number = self.search_control_employee_number.GetValue()
        search_firstname = self.search_control_name.GetValue()
        search_duty_name = self.search_control_duty_name.GetValue()
        search_duty_date = self.search_control_duty_date.GetValue()

        self.dict_duty_schedule_filtered = self.dict_duty_schedule.copy()
        self.duty_count_filtered = self.duty_count

        for duty_date in self.dict_duty_schedule.keys():
            # duty date
            if search_duty_date != "" and search_duty_date not in duty_date:
                del self.dict_duty_schedule_filtered[duty_date]
                continue

            # employee number
            employee_number_list = self.dict_duty_schedule[duty_date].copy()
            for employee_number in self.dict_duty_schedule[duty_date]:
                # employee number
                if search_employee_number != "" and search_employee_number not in employee_number:
                    employee_number_list.remove(employee_number)
                # department
                elif search_department_name != "" and search_department_name not in self.employee_dict[employee_number][
                    "department"]:
                    employee_number_list.remove(employee_number)
                elif search_firstname != "" and search_firstname not in self.employee_dict[employee_number][
                    "first_name"]:
                    employee_number_list.remove(employee_number)
                elif search_duty_name != "":
                    primary_duty_code = self.employee_dict[employee_number]["primary_duty_code"]
                    duty_description = CommonModel.get_list_dict_value_from_key(_list_dict=self.duty_catalog_as_list,
                                                                                _key_column="duty_code",
                                                                                _expected_key_column_value=primary_duty_code,
                                                                                _value_column="duty_description"
                                                                                )

                    if search_duty_name not in duty_description:
                        employee_number_list.remove(employee_number)

            self.dict_duty_schedule_filtered[duty_date] = employee_number_list



        self.duty_count_filtered = self.get_duty_count(_dict_duty_schedule=self.dict_duty_schedule_filtered)
        self.populate_duties_from_dict(_dict_duties=self.dict_duty_schedule_filtered,
                                       _duty_count=self.duty_count_filtered)

    def delete_duty_handler(self, event):
        if len(self.dict_duty_schedule) == 0:
            self.show_message_dialog(_message_title="Delete Duty", _message="Unable to delete.  Empty duty schedule...")
            return

        selected_rows = self.grid_duty_detail.GetSelectedRows()
        if len(selected_rows) == 0:
            self.show_message_dialog(_message_title="Delete Duty", _message="Unable to delete. No duty selected...")
            return

        # delete the duty entries
        dict_duty_schedule_temp = self.dict_duty_schedule.copy()
        for row_index in selected_rows:
            employee_number = self.grid_duty_detail.GetCellValue(row_index, 1)
            duty_date = self.grid_duty_detail.GetCellValue(row_index, 4)
            employee_number_list = dict_duty_schedule_temp[duty_date]
            employee_number_list.remove(employee_number)
            dict_duty_schedule_temp[duty_date] = employee_number_list

        duty_count_temp = self.get_duty_count(_dict_duty_schedule=dict_duty_schedule_temp)
        # refresh the grid
        self.update_duty_buffer(_dict_duty_schedule=dict_duty_schedule_temp, _duty_count=duty_count_temp)
        self.populate_duties_from_dict(_dict_duties=self.dict_duty_schedule, _duty_count=self.duty_count)


    def insert_duty_handler(self, event):
        window_insert_duty = WindowInsertDuty(None, wx.ID_ANY, "", _sqlite_sqls=self.sqlite_sqls)
        window_insert_duty.ShowModal()

        employee_number = window_insert_duty.txt_employee_Number.GetValue()
        wx_duty_date = window_insert_duty.datepicker_ctrl_duty_date.GetValue()
        duty_date = "{}{:02d}{:02d}".format(wx_duty_date.GetYear(), wx_duty_date.GetMonth() + 1,
                                            wx_duty_date.GetDay())

        duty_employee_list = []
        dict_duty_schedule_temp = self.dict_duty_schedule.copy()
        if dict_duty_schedule_temp[duty_date] != -1:
            duty_employee_list = dict_duty_schedule_temp[duty_date]

        duty_employee_list.append(employee_number)
        dict_duty_schedule_temp[duty_date] = duty_employee_list
        duty_count = self.get_duty_count(_dict_duty_schedule=dict_duty_schedule_temp)
        # refresh the grid
        self.update_duty_buffer(_dict_duty_schedule=dict_duty_schedule_temp, _duty_count=duty_count)
        self.populate_duties_from_dict(_dict_duties=self.dict_duty_schedule, _duty_count=self.duty_count)
        self.show_message_dialog(_message_title="Insert Duty", _message="Insert Duty Successful...")


    def swap_duty_handler(self, event):
        if len(self.dict_duty_schedule) == 0:
            self.show_message_dialog(_message_title="Swap Duty", _message="Unable to Swap. Empty duty schedule...")
            return

        selected_rows = self.grid_duty_detail.GetSelectedRows()
        if len(selected_rows) != 2:
            self.show_message_dialog(_message_title="Swap Duty",
                                     _message="Unable to Swap. Select two duties to be swapped...")
            return

        employee1_number = self.grid_duty_detail.GetCellValue(selected_rows[0], 1)
        employee1_duty_date = self.grid_duty_detail.GetCellValue(selected_rows[0], 4)
        employee2_number = self.grid_duty_detail.GetCellValue(selected_rows[1], 1)
        employee2_duty_date = self.grid_duty_detail.GetCellValue(selected_rows[1], 4)

        if employee1_number == employee2_number:
            self.show_message_dialog(_message_title="Swap Duty",
                                     _message="Unable to Swap. Same employee numbers have been selected...")
            return

        if employee1_duty_date == employee2_duty_date:
            self.show_message_dialog(_message_title="Swap Duty",
                                     _message="Unable to Swap. Same duty dates have been selected...")
            return
        dict_duty_schedule_temp = self.dict_duty_schedule.copy()

        UtilDutyInitializer.swap_duties_version2(_dict_duty_schedule=dict_duty_schedule_temp, _swap_emp_id1=employee1_number,
                                                 _duty_date_emp_id1=employee1_duty_date,
                                                 _swap_emp_id2=employee2_number, _duty_date_emp_id2=employee2_duty_date)

        # refresh the grid
        self.update_duty_buffer(_dict_duty_schedule=dict_duty_schedule_temp, _duty_count=self.duty_count)
        self.populate_duties_from_dict(_dict_duties=self.dict_duty_schedule, _duty_count=self.duty_count)
        self.show_message_dialog(_message_title="Duty Swap", _message="Duty Swap Successful...")


    def show_message_dialog(self, _message_title, _message, _style=wx.OK | wx.STAY_ON_TOP | wx.CENTRE):
        message_dialog = wx.MessageDialog(self, _message, _message_title, _style)
        message_dialog.ShowModal()

    def update_duty_buffer(self, _dict_duty_schedule, _duty_count):
        self.dict_duty_schedule = _dict_duty_schedule.copy()
        self.duty_count = _duty_count
        self.dict_duty_schedule_filtered = _dict_duty_schedule.copy()
        self.duty_count_filtered = _duty_count


    def get_unique_employee_number_list(self):
        unique_employee_number_list = []
        dict_employee_number = defaultdict(lambda :-1)
        for duty_date in self.dict_duty_schedule.keys():
            for employee_number in self.dict_duty_schedule[duty_date]:
                dict_employee_number[employee_number] = 1

        for key in dict_employee_number.keys():
            unique_employee_number_list.append(key)

        return unique_employee_number_list

    def populate_duties_from_dict(self, _dict_duties, _duty_count):
        if len(_dict_duties.keys()) == 0:
            return

        if self.grid_duty_detail.GetNumberRows() > 0:
            self.grid_duty_detail.DeleteRows(pos=0, numRows=self.grid_duty_detail.GetNumberRows())

        self.grid_duty_detail.AppendRows(_duty_count)

        current_row = 0
        for date_key in _dict_duties.keys():
            for employee_number in _dict_duties[date_key]:
                self.grid_duty_detail.SetCellValue(current_row, 0, self.employee_dict[employee_number]["department"])
                self.grid_duty_detail.SetCellValue(current_row, 1, employee_number)
                self.grid_duty_detail.SetCellValue(current_row, 2, self.employee_dict[employee_number]["first_name"])
                duty_code = self.employee_dict[employee_number]["primary_duty_code"]
                duty_description = self.duty_catalog_dict[duty_code]["duty_description"]
                self.grid_duty_detail.SetCellValue(current_row, 3, duty_description)
                self.grid_duty_detail.SetCellValue(current_row, 4, date_key)

                current_row += 1

    def get_duty_dict_from_table_records(self, _table_duties_list):
        dict_duties = defaultdict(lambda: -1)
        duty_count = 0
        for item in _table_duties_list:
            dict_item = json.loads(item)
            if dict_duties[dict_item["duty_date"]] == -1:
                dict_duties[dict_item["duty_date"]] = [dict_item["employee_number"]]
            else:
                dict_duties[dict_item["duty_date"]].append(dict_item["employee_number"])
            duty_count += 1

        return dict_duties, duty_count

    def get_duty_count(self, _dict_duty_schedule):
        duty_count = 0
        for duty_date in _dict_duty_schedule.keys():
            duty_count += len(_dict_duty_schedule[duty_date])

        return duty_count

    def get_duties_and_leaves(self, _start_date, _end_date, _employee_number_list,
                              _list_company_holidays,
                              _minimum_daily_required_resource_count):

        #list_company_holidays = ['20240402', '20240415', '20240419']
        dict_duty_schedule, dict_emp_leaves = UtilDutyInitializer.assign_duty_round_robin(
            _list_emp_ids=_employee_number_list,
            _from_date=_start_date,
            _to_date=_end_date,
            _list_company_holidays=_list_company_holidays,
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
