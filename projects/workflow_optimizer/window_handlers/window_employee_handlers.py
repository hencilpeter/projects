
import datetime

class WindowEmployeeHandlers:
    # def __init__(self, _window_employee):
    #     self.window_employee = _window_employee
    @staticmethod
    def handle_clear_all_controls(_window_employee):
        _window_employee.txt_emp_number.Clear()
        _window_employee.txt_first_name.Clear()
        _window_employee.txt_last_name.Clear()
        _window_employee.txt_father_name.Clear()
        _window_employee.rd_btn_male.SetValue(0)
        _window_employee.rd_btn_female.SetValue(0)
        _window_employee.cmb_qualification.Select(-1)
        _window_employee.datepicker_employment_start_date.SetValue(datetime.datetime.today().date())
        _window_employee.datepicker_employment_end_date.SetValue(datetime.datetime.today().date())
        _window_employee.cmd_department.Select(-1)
        _window_employee.cm_no_of_leaves.Select(-1)
        _window_employee.cmb_primary_duty.Select(-1)
        _window_employee.cmb_salary_type.Select(-1)
        _window_employee.txt_salary.Clear()
        #_window_employee.bitmap_employee_image.Clear()
        _window_employee.grid_address.ClearGrid()
        _window_employee.grid_contact.ClearGrid()
        _window_employee.grid_identity.ClearGrid()



    def handle_enable_disable_employee_number(self):
        pass

    # def handle_clear_all_controls(self):
    #     pass
