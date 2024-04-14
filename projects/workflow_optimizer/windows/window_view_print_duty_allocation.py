import os.path

import wx

# begin wxGlade: dependencies
import wx.adv
import wx.grid
# end wxGlade

# begin wxGlade: extracode
# end wxGlade
from data_models.employee_model import EmployeeModel
from data_models.common_model import CommonModel
import json
from collections import defaultdict
from html.html_duty_viewer import HtmlDutyViewer
from util.util_config_reader import UtilConfigReader
from datetime import datetime
from util.util_common import UtilCommon

class ViewPrintDutyAllocation(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: ViewPrintDutyAllocation.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE

        self.sqlite_sqls = kwds['_sqlite_sqls']
        del kwds['_sqlite_sqls']

        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((724, 542))
        self.SetTitle("View/Print Duty Allocations")

        self.employee_data_as_list = EmployeeModel.get_all_employee_details_as_list(_sql_connection=self.sqlite_sqls)
        department_cursor = self.sqlite_sqls.get_table_data("select * from department;")
        self.department_names_as_list = CommonModel.get_table_data_as_list(_data_cursor=department_cursor)
        self.employee_dict = CommonModel.get_dict_from_list(self.employee_data_as_list, "employee_number")

        duty_catalog_cursor = self.sqlite_sqls.get_table_data("select * from duty_catalog;")
        self.duty_catalog_as_list = CommonModel.get_table_data_as_list(_data_cursor=duty_catalog_cursor)
        self.duty_catalog_dict = CommonModel.get_dict_from_list(self.duty_catalog_as_list, "duty_code")
        self.dict_duty_schedule = defaultdict(lambda: -1)
        self.duty_count = 0

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND | wx.FIXED_MINSIZE, 0)

        grid_sizer_1 = wx.GridSizer(3, 4, 0, 0)
        sizer_3.Add(grid_sizer_1, 1, wx.EXPAND, 0)

        label_1 = wx.StaticText(self, wx.ID_ANY, "Start Date:")
        label_1.SetMinSize((54, 16))
        grid_sizer_1.Add(label_1, 0, 0, 0)

        self.datepicker_ctrl_start_date = wx.adv.DatePickerCtrl(self, wx.ID_ANY,
                                                                style=wx.adv.DP_DEFAULT | wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        grid_sizer_1.Add(self.datepicker_ctrl_start_date, 0, 0, 0)

        label_2 = wx.StaticText(self, wx.ID_ANY, "End Date:")
        grid_sizer_1.Add(label_2, 0, 0, 0)

        self.datepicker_ctrl_end_date = wx.adv.DatePickerCtrl(self, wx.ID_ANY,
                                                              style=wx.adv.DP_DEFAULT | wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
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
        self.grid_duties.CreateGrid(0, 6)
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
        self.grid_duties.SetColSize(4, 120)
        self.grid_duties.SetColLabelValue(5, "Date")
        self.grid_duties.SetColSize(5, 100)
        self.grid_duties.SetMinSize((600, 620))
        # sizer_1.Add(self.grid_duties, 0, wx.EXPAND | wx.FIXED_MINSIZE | wx.SHAPED, 0)
        sizer_1.Add(self.grid_duties, 1, wx.EXPAND, 0)

        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(sizer_4, 0, wx.FIXED_MINSIZE | wx.SHAPED, 0)

        sizer_5 = wx.FlexGridSizer(1, 4, 0, 0)
        sizer_4.Add(sizer_5, 0, wx.ALIGN_BOTTOM | wx.FIXED_MINSIZE, 0)

        self.btn_load_duties = wx.Button(self, wx.ID_ANY, "Load Duties")
        sizer_5.Add(self.btn_load_duties, 0, 0, 0)

        self.btn_refresh_duties = wx.Button(self, wx.ID_ANY, "Refresh Duties")
        sizer_5.Add(self.btn_refresh_duties, 0, 0, 0)

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
        self.Bind(wx.EVT_BUTTON, self.handler_refresh_duties, self.btn_refresh_duties)
        # end wxGlade
        self.populate_default_values()

    def load_duties_handler(self, event):  # wxGlade: ViewPrintDutyAllocation.<event_handler>
        self.load_duties()

        event.Skip()

    def save_as_html_handler(self, event):  # wxGlade: ViewPrintDutyAllocation.<event_handler>
        dict_grid_duties = self.get_duties_from_grid()
        # self.start_date = "{}{:02d}{:02d}".format(wx_start_date.GetYear(), wx_start_date.GetMonth() + 1,
        #                                           wx_start_date.GetDay())
        # self.end_date = "{}{:02d}{:02d}".format(wx_end_date.GetYear(), wx_end_date.GetMonth() + 1,
        #                                         wx_end_date.GetDay())

        self.save_duty_schedule_as_html(_dict_duty_schedule=dict_grid_duties, _start_date=self.start_date,
                                        _end_date=self.end_date)
        event.Skip()

    def handler_cancel(self, event):  # wxGlade: ViewPrintDutyAllocation.<event_handler>
        print("Event handler 'handler_cancel' not implemented!")
        event.Skip()

    def handler_refresh_duties(self, event):
        self.populate_duties_from_dict(_dict_duties=self.dict_duty_schedule, _duty_count=self.duty_count)

    def get_department_list(self, _department_list):
        department_list = []
        for department in _department_list:
            dict_department = json.loads(department)
            department_list.append(dict_department["description"])
        return department_list

    def populate_default_values(self):
        # department
        self.combo_box_department.Append("All")
        department_list = self.get_department_list(_department_list=self.department_names_as_list)
        for department in department_list:
            self.combo_box_department.Append(department)

        # duties
        self.combo_box_duty.Append("All")
        for duty_code in self.duty_catalog_dict.keys():
            duty_name = self.duty_catalog_dict[duty_code]["duty_description"]
            self.combo_box_duty.Append(duty_name)

    def populate_duties_from_dict(self, _dict_duties, _duty_count):
        if len(_dict_duties.keys()) == 0:
            return

        if self.grid_duties.GetNumberRows() > 0:
            self.grid_duties.DeleteRows(pos=0, numRows=self.grid_duties.GetNumberRows())

        self.grid_duties.AppendRows(_duty_count)

        current_row = 0
        filter_department_name = self.combo_box_department.GetValue()
        filter_duty_name = self.combo_box_duty.GetValue()
        for date_key in _dict_duties.keys():
            for employee_number in _dict_duties[date_key]:
                department_name = self.employee_dict[employee_number]["department"]
                duty_code = self.employee_dict[employee_number]["primary_duty_code"]
                duty_description = self.duty_catalog_dict[duty_code]["duty_description"]
                if not (filter_department_name == 'All' or filter_department_name in department_name):
                    continue

                if not (filter_duty_name == 'All' or filter_duty_name in duty_description):
                    continue
                self.grid_duties.SetCellValue(current_row, 0, department_name)
                self.grid_duties.SetCellValue(current_row, 1, employee_number)
                self.grid_duties.SetCellValue(current_row, 2, self.employee_dict[employee_number]["first_name"])
                self.grid_duties.SetCellValue(current_row, 3, self.employee_dict[employee_number]["last_name"])

                self.grid_duties.SetCellValue(current_row, 4, duty_description)
                self.grid_duties.SetCellValue(current_row, 5, date_key)
                current_row += 1

    # DUPLICATE CODE
    def load_duties(self):
        wx_start_date = self.datepicker_ctrl_start_date.GetValue()
        wx_end_date = self.datepicker_ctrl_end_date.GetValue()
        self.start_date = "{}{:02d}{:02d}".format(wx_start_date.GetYear(), wx_start_date.GetMonth() + 1,
                                                  wx_start_date.GetDay())
        self.end_date = "{}{:02d}{:02d}".format(wx_end_date.GetYear(), wx_end_date.GetMonth() + 1,
                                                wx_end_date.GetDay())

        sql = "select * from employee_duties where duty_date >= '{}' and duty_date <= '{}'" \
            .format(self.start_date, self.end_date)

        employee_duties_cursor = self.sqlite_sqls.get_table_data(sql)
        employee_duties_list = CommonModel.get_table_data_as_list(_data_cursor=employee_duties_cursor)
        dict_duty_schedule, duty_count = self.get_duty_dict_from_table_records(_table_duties_list=employee_duties_list)
        # self.update_duty_buffer(_dict_duty_schedule=dict_duty_schedule, _duty_count=duty_count)
        self.dict_duty_schedule = dict_duty_schedule
        self.duty_count = duty_count
        self.populate_duties_from_dict(_dict_duties=dict_duty_schedule, _duty_count=duty_count)

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

    def get_duties_from_grid(self):
        dict_duties = defaultdict(lambda: -1)
        for row_number in range(0, self.grid_duties.GetNumberRows()):
            employee_number = self.grid_duties.GetCellValue(row_number, 1)
            if employee_number == "":
                continue
            duty_date = self.grid_duties.GetCellValue(row_number, 5)
            if dict_duties[duty_date] == -1:
                dict_duties[duty_date] = [employee_number]
            else:
                dict_duties[duty_date].append(employee_number)

        return dict_duties

    def save_duty_schedule_as_html(self, _dict_duty_schedule, _start_date, _end_date):
        html_duty_viewer = HtmlDutyViewer(
            _header_name="Duty Schedule  ( {} - {}) ".format(_start_date, _end_date), _footer="End of the Document")

        html_duty_viewer.add_table_row_header_with_two_column(_col1_header="Date", _col2_header="Employee Name(s)")

        for business_date in _dict_duty_schedule:
            list_emp_ids = _dict_duty_schedule[business_date]
            list_emp_ids.sort()
            formatted_employees = ""
            count = 1
            for employee_number in list_emp_ids:
                formatted_employees = formatted_employees + "{}.{}, {} ({}) ".format(count, self.employee_dict[
                    employee_number]["first_name"],
                                                                                     self.employee_dict[
                                                                                         employee_number]["last_name"],
                                                                                     employee_number)
                count += 1
            html_duty_viewer.add_table_row_values_with_two_column(_col1_value=business_date,
                                                                  _col2_value=formatted_employees)

        html_duty_viewer.save_html_file(self.get_result_filename())
        UtilCommon.show_message_dialog(_message_title="Duty Schedule",
                                       _message="Duty Schedule has been created and saved...")



    def get_result_filename(self):
        file_path = UtilConfigReader.get_application_config(configuration_name="out_schedule_files_path")
        timestamp = datetime.today().strftime('%Y%m%d%H%M%S')
        file_full_path = os.path.join(file_path, "duty_schedule_"+timestamp+".html")
        return file_full_path


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
