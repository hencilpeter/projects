from collections import defaultdict
from data_models.common_model import CommonModel
from db.sqlite_sqls import SqliteSqls


class AddressModel:
    def __init__(self, _window_employee, _sql_connection):
        self.sql_connection = _sql_connection
        self.dict_address = defaultdict(lambda: -1)
        self.load_address_from_controls(_window_employee=_window_employee)

    def load_address_from_controls(self, _window_employee):
        for index in range(0, _window_employee.grid_rows_count):
            if _window_employee.grid_address.GetCellValue(index, 0) != "":
                self.dict_address[_window_employee.grid_address.GetCellValue(index, 0)] \
                    = _window_employee.grid_address.GetCellValue(index, 1)

    def get_existing_address_dict(self, _employee_number):
        address_query = "select address_type, address_value from address where employee_number = '{}' and  end_date = '9999-12-31' ;".format(
            _employee_number)
        address_cursor = self.sql_connection.get_table_data(query=address_query)
        dict_address = defaultdict(lambda: -1)
        for row in address_cursor:
            dict_address[row[0]] = row[1]

        return dict_address

    def get_current_and_existing_address(self, _employee_number):
        existing_address_dict = self.get_existing_address_dict(_employee_number)
        return self.dict_address, existing_address_dict
