from data_models.common_model import CommonModel
class EmployeeModel:
    def __init__(self, _window_employee, _should_load_from_table=False):
        if _should_load_from_table:
            pass
        else:
            self.employee_number = _window_employee.txt_emp_number.GetValue()
            self.employee_firstname = _window_employee.txt_first_name.GetValue()
            self.employee_lastname = _window_employee.txt_last_name.GetValue()
            self.employee_fathername = _window_employee.txt_father_name.GetValue()
            self.sex = "M" if _window_employee.rd_btn_male.GetValue() == 1 else "F"
            self.date_of_birth = _window_employee.datepicker_date_of_birth.GetValue()
            self.education = _window_employee.cmb_qualification.GetValue()
            self.employment_start_date = _window_employee.datepicker_employment_start_date.GetValue()
            self.employment_end_date = _window_employee.datepicker_employment_end_date.GetValue()

    def get_insert_sql(self):
        if self.employee_number == "":
            return None

        insert_statement = """
        insert into
        employee(employee_number, first_name, last_name, father_name, sex, date_of_birth, education,
                 employment_start_date, employment_end_date)
        values('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')
        """.format(self.employee_number, self.employee_firstname,
                   self.employee_lastname, self.employee_fathername, self.sex, self.date_of_birth, self.education,
                   self.employment_start_date, self.employment_end_date)
        print(insert_statement)
        return insert_statement

    def get_update_sql(self):
        if self.employee_number == "":
            return None

        update_statement = """
               update employee set first_name='{}', last_name='{}', father_name='{}', sex='{}', date_of_birth='{}', education='{}',
                        employment_start_date='{}', employment_end_date='{}' where employee_number = '{}'
               """.format(self.employee_firstname,
                          self.employee_lastname, self.employee_fathername, self.sex, self.date_of_birth,
                          self.education, self.employment_start_date, self.employment_end_date, self.employee_number, )
        print(update_statement)
        return update_statement

    @staticmethod
    def get_all_employee_details_as_list(_sql_connection):
        sql = "select * from employee;"
        employee_cursor = _sql_connection.get_table_data(query=sql)
        employee_data_as_list = CommonModel.get_table_data_as_list(_data_cursor=employee_cursor)
        return employee_data_as_list

