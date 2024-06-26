import datetime
import json

from util.util_default_value import UtilDefaultValue
from data_models.employee_model import EmployeeModel
from data_models.address_model import AddressModel
from data_models.common_model import CommonModel
from db.sqlite_sqls import SqliteSqls
from util.util_config_reader import UtilConfigReader
from collections import defaultdict


class WindowEmployeeHandlers:
    @staticmethod
    def handle_clear_all_controls(_window_employee, _sqlite_connection):
        _window_employee.txt_emp_number.Clear()
        _window_employee.txt_first_name.Clear()
        _window_employee.txt_last_name.Clear()
        _window_employee.txt_father_name.Clear()
        _window_employee.rd_btn_male.SetValue(0)
        _window_employee.rd_btn_female.SetValue(0)
        _window_employee.datepicker_date_of_birth.SetValue(UtilDefaultValue.get_default_min_date_of_birth())
        _window_employee.cmb_qualification.SetItems(
            WindowEmployeeHandlers.get_qualification_list(sql_connection=_sqlite_connection))
        _window_employee.cmb_qualification.Select(0)
        _window_employee.datepicker_employment_start_date.SetValue(UtilDefaultValue.get_current_date())
        _window_employee.datepicker_employment_end_date.SetValue(UtilDefaultValue.get_default_emp_end_date())
        department_list = WindowEmployeeHandlers.get_department_list(sql_connection=_sqlite_connection)
        _window_employee.cmd_department.SetItems(department_list)
        _window_employee.cmd_department.Select(-1)

        _window_employee.cm_no_of_leaves.SetItems(
            WindowEmployeeHandlers.get_leaves_list(sql_connection=_sqlite_connection))
        _window_employee.cm_no_of_leaves.Select(0)

        duty_catalog = WindowEmployeeHandlers.get_duty_catalog(sql_connection=_sqlite_connection)
        duty_name_list = []
        for row in duty_catalog:
            dict_duty = json.loads(row)
            duty_name_list.append(dict_duty['duty_description'])

        _window_employee.cmb_primary_duty.SetItems(duty_name_list)
        _window_employee.cmb_primary_duty.Select(-1)
        _window_employee.cmb_salary_type.SetItems(
            WindowEmployeeHandlers.get_salary_type_list(sql_connection=_sqlite_connection))
        _window_employee.cmb_salary_type.Select(-1)
        _window_employee.txt_salary.Clear()
        # _window_employee.bitmap_employee_image.Clear()
        _window_employee.grid_address.ClearGrid()
        _window_employee.grid_contact.ClearGrid()
        _window_employee.grid_identity.ClearGrid()

    @staticmethod
    def handle_save_employee_details(_window_employee, _sqlite_sql):
        # get employee table detail
        model_employee = EmployeeModel(_window_employee=_window_employee)

        sqlite_sqls = SqliteSqls(db_file_name=UtilConfigReader.get_application_config("app_database_file_name"))
        employee_number = _window_employee.txt_emp_number.GetValue()
        # employee
        employees_count = _sqlite_sql.get_record_count(sql="select count(1) from employee where employee_number = '{}';"
                                                       .format(employee_number))
        if employees_count > 0:
            employee_sql = model_employee.get_update_sql()
        else:
            employee_sql = model_employee.get_insert_sql()

        # address
        address = AddressModel(_window_employee=_window_employee, _sql_connection=_sqlite_sql)
        dict_current_address, dict_existing_address = address.get_current_and_existing_address(
            _employee_number=employee_number)

        # contact

        # identity

        # save
        sqlite_sqls.execute_and_commit_sql(sql=employee_sql)
        print("employee details saved.")

        address_sql_list = CommonModel.get_scd2_sql(_dict_existing=dict_existing_address,
                                                    _dict_current=dict_current_address,
                                                    _employee_id=employee_number,
                                                    _column_type="address_type", _column_value="address_value",
                                                    _table_name="address")
        address_sql = ";".join(address_sql_list)

        print(address_sql)
        sqlite_sqls.executescript_and_commit_sql(sql=address_sql)

    @staticmethod
    def load_employee_data(sql_connection, employee_number):
        sql = "select * from employee where employee_number = '{}'".format(employee_number)
        cursor = sql_connection.get_table_data(query=sql)
        dict_employee = defaultdict(lambda: -1)
        column_names = [description[0] for description in cursor.description]

        for row in cursor:
            for col_name in column_names:
                dict_employee[col_name] = row[column_names.index(col_name)]
            break

        return dict_employee

    @staticmethod
    def populate_employee_data(_window_employee, _employee_dict):
        # "id": "17", "employee_number": "MF0003", "first_name": "Prathima ", "last_name": "Venati", "father_name": "Anand", "sex": "F", "date_of_birth": "1990-01-30",
        # "education": "High School", "employment_start_date": "2024-04-11", "employment_end_date": "9999-12-31", "department": "Production", "leaves_per_month": "0",
        # "primary_duty_code": "DT102", "salary_type_code": "Daily", "salary": "300.0"}
        _employee_dict = json.loads(_employee_dict)
        _window_employee.txt_emp_number.SetValue(_employee_dict["employee_number"])
        _window_employee.txt_first_name.SetValue(_employee_dict["first_name"])
        _window_employee.txt_last_name.SetValue(_employee_dict["last_name"])
        _window_employee.txt_father_name.SetValue(_employee_dict["father_name"])
        if _employee_dict["sex"] == "F":
            _window_employee.rd_btn_female.SetValue(1)
        else:
            _window_employee.rd_btn_female.SetValue(1)
        _window_employee.datepicker_date_of_birth.SetValue(
            datetime.datetime.strptime(_employee_dict["date_of_birth"], "%Y-%m-%d"))

        _window_employee.cmb_qualification.SetValue(_employee_dict["education"])
        _window_employee.datepicker_employment_start_date.SetValue(
            datetime.datetime.strptime(_employee_dict["employment_start_date"], "%Y-%m-%d"))
        _window_employee.datepicker_employment_end_date.SetValue(
            datetime.datetime.strptime(_employee_dict["employment_end_date"], "%Y-%m-%d"))

        _window_employee.cmd_department.SetValue(_employee_dict["department"])
        _window_employee.cm_no_of_leaves.SetValue(_employee_dict["leaves_per_month"])

        duty_description = CommonModel.get_list_dict_value_from_key(_list_dict=_window_employee.duty_catalog_list,
                                                                    _key_column="duty_code",
                                                                    _expected_key_column_value=_employee_dict[
                                                                        "primary_duty_code"],
                                                                    _value_column="duty_description")

        _window_employee.cmb_primary_duty.SetValue(duty_description)

        _window_employee.cmb_salary_type.SetValue(_employee_dict["salary_type_code"])
        _window_employee.txt_salary.SetValue(_employee_dict["salary"])


        # duty_catalog = WindowEmployeeHandlers.get_duty_catalog(sql_connection=_sqlite_connection)
        # duty_name_list = []
        # for row in duty_catalog:
        #     dict_duty = json.loads(row)
        #     duty_name_list.append(dict_duty['duty_description'])

        # # _window_employee.bitmap_employee_image.Clear()
        # _window_employee.grid_address.ClearGrid()
        # _window_employee.grid_contact.ClearGrid()
        # _window_employee.grid_identity.ClearGrid()

    @staticmethod
    def get_qualification_list(sql_connection):
        dict_qualification = sql_connection.get_mnemonic_table_data('qualification')
        qualification_list = []
        for key in dict_qualification.keys():
            qualification_list.append(dict_qualification[key])

        return qualification_list

    @staticmethod
    def get_leaves_list(sql_connection):
        dict_leaves = sql_connection.get_mnemonic_table_data('number_of_leaves')
        leave_list = []
        for key in dict_leaves.keys():
            leave_list.append(dict_leaves[key])

        return leave_list

    @staticmethod
    def get_salary_type_list(sql_connection):
        dict_salary_types = sql_connection.get_mnemonic_table_data('salary_type')
        salary_list = []
        for key in dict_salary_types.keys():
            salary_list.append(dict_salary_types[key])

        return salary_list

    @staticmethod
    def get_department_list(sql_connection):
        department_list = sql_connection.get_single_column_list(table_name='department', column_name='department_name')
        return department_list

    @staticmethod
    def get_duty_catalog(sql_connection):
        duty_catalog_cursor = sql_connection.get_table_data("select * from duty_catalog")
        column_names = [description[0] for description in duty_catalog_cursor.description]
        result = []
        for row in duty_catalog_cursor:
            str_row = ""
            list_current_row_columns = []
            for col_name in column_names:
                list_current_row_columns.append("\"" + str(col_name) + "\":\"" + str(row[column_names.index(col_name)])
                                                + "\"")
            str_row = "{" + ','.join(list_current_row_columns) + "}"
            result.append(str_row)
        return result

    @staticmethod
    def get_next_employee_number(_sql_connection):
        employee_count_cursor = _sql_connection.get_table_data("select employee_number from employee;")
        row_count = len(employee_count_cursor.fetchall())
        employee_count = row_count + 1
        employee_number = str(UtilConfigReader.get_application_config("employee_id_format_template")).format(
            UtilConfigReader.get_application_config("employee_id_prefix"),
            employee_count)
        return employee_number
