import datetime
from util.util_default_value import UtilDefaultValue
from data_models.employee_model import EmployeeModel
from db.sqlite_sqls import SqliteSqls
from util.util_config_reader import UtilConfigReader
from collections import  defaultdict

class WindowEmployeeHandlers:
    @staticmethod
    def handle_clear_all_controls(_window_employee):
        _window_employee.txt_emp_number.Clear()
        _window_employee.txt_first_name.Clear()
        _window_employee.txt_last_name.Clear()
        _window_employee.txt_father_name.Clear()
        _window_employee.rd_btn_male.SetValue(0)
        _window_employee.rd_btn_female.SetValue(0)
        _window_employee.datepicker_date_of_birth.SetValue(UtilDefaultValue.get_default_date())
        _window_employee.cmb_qualification.Select(-1)
        # datetime.datetime.today().date()
        _window_employee.datepicker_employment_start_date.SetValue(UtilDefaultValue.get_default_date())
        _window_employee.datepicker_employment_end_date.SetValue(UtilDefaultValue.get_default_date())
        _window_employee.cmd_department.Select(-1)
        _window_employee.cm_no_of_leaves.Select(-1)
        _window_employee.cmb_primary_duty.Select(-1)
        _window_employee.cmb_salary_type.Select(-1)
        _window_employee.txt_salary.Clear()
        # _window_employee.bitmap_employee_image.Clear()
        _window_employee.grid_address.ClearGrid()
        _window_employee.grid_contact.ClearGrid()
        _window_employee.grid_identity.ClearGrid()

    @staticmethod
    def handle_enable_disable_employee_number(_window_employee, should_enable=True):
        _window_employee.txt_emp_number.Enable(enable=should_enable)

    @staticmethod
    def handle_save_employee_details(_window_employee):
        # get employee table detail
        model = EmployeeModel(_window_employee=_window_employee)

        sqlite_sqls = SqliteSqls(db_file_name=UtilConfigReader.get_application_config("app_database_file_name"))
        employee_number = _window_employee.txt_emp_number.GetValue()
        is_existing_employee = WindowEmployeeHandlers.is_existing_employee(sql_connection=sqlite_sqls,
                                                                           employee_number=employee_number)
        if is_existing_employee:
            sql = model.get_update_sql()
        else:
            sql = model.get_insert_sql()
        sqlite_sqls.execute_and_commit_sql(sql=sql)
        WindowEmployeeHandlers.handle_enable_disable_employee_number(_window_employee, should_enable=False)
        # del sqlite_sqls

    @staticmethod
    def is_existing_employee(sql_connection, employee_number):
        sql = "select 1 from employee where employee_number = '{}'".format(employee_number)
        cursor = sql_connection.get_table_data(query=sql)
        return True if cursor.rowcount > -1 else False

    @staticmethod
    def load_employee_data(sql_connection, employee_number):
        sql = "select * from employee where employee_number = '{}'".format(employee_number)
        cursor = sql_connection.get_table_data(query=sql)
        dict_employee = defaultdict(lambda :-1)
        if cursor.rowcount != 1:
            return dict_employee
        column_names = [description[0] for description in cursor.description]

        for row in cursor:
            for col_name in column_names:
                dict_employee[col_name] = row[column_names.index(col_name)]
            break

        return dict_employee
