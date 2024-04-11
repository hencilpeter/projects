import json

import wx
import wx.grid
from data_models.common_model import CommonModel
from data_models.employee_model import EmployeeModel


class WindowSearchEmployee(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: SearchEmployee.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        sqlite_sqls = kwds["_sqlite_sqls"]
        self.employee_data_as_list = EmployeeModel.get_all_employee_details_as_list(_sql_connection=sqlite_sqls)
        self.employee_data_as_list_filtered = self.employee_data_as_list.copy()
        self.return_value = None
        del kwds["_sqlite_sqls"]
        wx.Dialog.__init__(self, *args, **kwds)
        self.selected_row_index = -1

        self.SetSize((660, 400))
        self.SetTitle("TODO:Search Employee Details")

        self.panel_1 = wx.Panel(self, wx.ID_ANY)

        sizer_2 = wx.BoxSizer(wx.VERTICAL)

        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(sizer_4, 1, wx.EXPAND, 0)

        self.search_department = wx.SearchCtrl(self.panel_1, wx.ID_ANY, "")
        self.search_department.ShowCancelButton(True)
        sizer_4.Add(self.search_department, 0, 1, 0)

        self.search_employee_number = wx.SearchCtrl(self.panel_1, wx.ID_ANY, "")
        self.search_employee_number.ShowCancelButton(True)
        sizer_4.Add(self.search_employee_number, 0, 1, 0)

        self.search_firstname = wx.SearchCtrl(self.panel_1, wx.ID_ANY, "")
        self.search_firstname.ShowCancelButton(True)
        sizer_4.Add(self.search_firstname, 0, 1, 0)

        self.search_lastname = wx.SearchCtrl(self.panel_1, wx.ID_ANY, "")
        self.search_lastname.ShowCancelButton(True)
        sizer_4.Add(self.search_lastname, 0, 1, 0)

        self.grid_employees = wx.grid.Grid(self.panel_1, wx.ID_ANY, size=(1, 1))
        self.grid_employees.CreateGrid(len(self.employee_data_as_list), 4)
        self.grid_employees.SetColLabelSize(40)
        self.grid_employees.SetRowLabelSize(60)
        self.grid_employees.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid_employees.SetColLabelValue(0, "Department")
        self.grid_employees.SetColSize(0, 160)
        self.grid_employees.SetColLabelValue(1, "Employee Number")
        self.grid_employees.SetColSize(1, 130)
        self.grid_employees.SetColLabelValue(2, "First Name")
        self.grid_employees.SetColSize(2, 130)
        self.grid_employees.SetColLabelValue(3, "Last Name")
        self.grid_employees.SetColSize(3, 130)
        sizer_2.Add(self.grid_employees, 4, wx.ALL | wx.EXPAND, 4)

        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(sizer_3, 1, wx.EXPAND, 0)

        self.btn_Ok = wx.Button(self.panel_1, wx.ID_ANY, "OK")
        sizer_3.Add(self.btn_Ok, 0, 1, 0)

        self.btn_Cancel = wx.Button(self.panel_1, wx.ID_ANY, "Cancel")
        sizer_3.Add(self.btn_Cancel, 0, 1, 0)

        sizer_3.Add((0, 0), 0, 0, 0)

        sizer_3.Add((0, 0), 0, 0, 0)

        sizer_3.Add((0, 0), 0, 0, 0)

        self.panel_1.SetSizer(sizer_2)

        self.Layout()

        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.handler_department_cancel, self.search_department)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.handler_department_search, self.search_department)
        self.Bind(wx.EVT_TEXT_ENTER, self.handler_department_enter, self.search_department)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.handler_identity_cancel, self.search_employee_number)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.handler_identity_search, self.search_employee_number)
        self.Bind(wx.EVT_TEXT_ENTER, self.handler_identity_enter, self.search_employee_number)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.handler_firstname_cancel, self.search_firstname)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.handler_firstname_search, self.search_firstname)
        self.Bind(wx.EVT_TEXT_ENTER, self.handler_firstname_enter, self.search_firstname)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.handler_lastname_cencel, self.search_lastname)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.handler_lastname_serach, self.search_lastname)
        self.Bind(wx.EVT_TEXT_ENTER, self.handler_lastname_enter, self.search_lastname)
        self.Bind(wx.grid.EVT_GRID_CMD_SELECT_CELL, self.handler_grid_select, self.grid_employees)
        self.Bind(wx.EVT_BUTTON, self.handler_Ok, self.btn_Ok)
        self.Bind(wx.EVT_BUTTON, self.handler_Cancel, self.btn_Cancel)
        # end wxGlade
        self.load_data_in_employee_grid(_employee_data_as_list=self.employee_data_as_list)

    def handler_department_cancel(self, event):  # wxGlade: SearchEmployee.<event_handler>
        self.apply_filter_on_grid()
        event.Skip()

    def handler_department_search(self, event):  # wxGlade: SearchEmployee.<event_handler>
        self.apply_filter_on_grid()
        event.Skip()

    def handler_department_enter(self, event):  # wxGlade: SearchEmployee.<event_handler>
        self.apply_filter_on_grid()
        event.Skip()

    def handler_identity_cancel(self, event):  # wxGlade: SearchEmployee.<event_handler>
        self.apply_filter_on_grid()
        event.Skip()

    def handler_identity_search(self, event):  # wxGlade: SearchEmployee.<event_handler>
        self.apply_filter_on_grid()
        event.Skip()

    def handler_identity_enter(self, event):  # wxGlade: SearchEmployee.<event_handler>
        self.apply_filter_on_grid()
        event.Skip()

    def handler_firstname_cancel(self, event):  # wxGlade: SearchEmployee.<event_handler>
        self.apply_filter_on_grid()
        event.Skip()

    def handler_firstname_search(self, event):  # wxGlade: SearchEmployee.<event_handler>
        self.apply_filter_on_grid()
        event.Skip()

    def handler_firstname_enter(self, event):  # wxGlade: SearchEmployee.<event_handler>
        self.apply_filter_on_grid()
        event.Skip()

    def handler_lastname_cencel(self, event):  # wxGlade: SearchEmployee.<event_handler>
        self.apply_filter_on_grid()
        event.Skip()

    def handler_lastname_serach(self, event):  # wxGlade: SearchEmployee.<event_handler>
        self.apply_filter_on_grid()
        event.Skip()

    def handler_lastname_enter(self, event):  # wxGlade: SearchEmployee.<event_handler>
        self.apply_filter_on_grid()
        event.Skip()

    def handler_grid_select(self, event):  # wxGlade: SearchEmployee.<event_handler>
        selected_rows = self.grid_employees.GetSelectedRows()
        self.selected_row_index = selected_rows[0]

    def handler_Ok(self, event):
        if self.selected_row_index != -1 and self.selected_row_index < len(self.employee_data_as_list_filtered):
            self.return_value = self.employee_data_as_list_filtered[self.selected_row_index]
        self.EndModal(wx.ID_OK)

    def handler_Cancel(self, event):
        self.Close()

    # end of class SearchEmployee

    def apply_filter_on_grid(self):
        # self.employee_data_as_list_filtered = self.employee_data_as_list.copy()
        department_name = self.search_department.GetValue()
        employee_number = self.search_employee_number.GetValue()
        firstname = self.search_firstname.GetValue()
        last_name = self.search_lastname.GetValue()

        filtered_data = []
        dict_filter_values = dict(
            {"department": department_name, "employee_number": employee_number, "first_name": firstname,
             "last_name": last_name})

        for employee_record in self.employee_data_as_list:
            employee_dict = json.loads(employee_record)
            skip_row = False
            for filter_key in dict_filter_values.keys():
                if dict_filter_values[filter_key] not in employee_dict[filter_key]:
                    skip_row = True
                    break

            if not skip_row:
                filtered_data.append(employee_record)

        self.employee_data_as_list_filtered = filtered_data
        self.load_data_in_employee_grid(_employee_data_as_list=self.employee_data_as_list_filtered)

    def load_data_in_employee_grid(self, _employee_data_as_list):
        self.grid_employees.ClearGrid()
        row_count = 0
        for employee in _employee_data_as_list:
            employee_dict = json.loads(employee)
            self.grid_employees.SetCellValue(row_count, 0, employee_dict["department"])
            self.grid_employees.SetCellValue(row_count, 1, employee_dict["employee_number"])
            self.grid_employees.SetCellValue(row_count, 2, employee_dict["first_name"])
            self.grid_employees.SetCellValue(row_count, 3, employee_dict["last_name"])
            row_count += 1

# class MenuBar(wx.App):
#     def OnInit(self):
#         self.search_employee = WindowSearchEmployee(None, wx.ID_ANY, "")
#         self.SetTopWindow(self.search_employee)
#         self.search_employee.ShowModal()
#         self.search_employee.Destroy()
#         return True
#
#     # end of class MenuBar
#
#
# if __name__ == "__main__":
#     menubar = MenuBar(0)
#     menubar.MainLoop()
