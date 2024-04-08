from collections import defaultdict


class AddressModel:
    def __init__(self, _window_employee, _should_load_from_table=False):
        self.dict_address = defaultdict(lambda: -1)
        if _should_load_from_table:
            self.dict_address = self.load_address_from_table()
        else:
            self.dict_address = self.load_address_from_controls(_window_employee=_window_employee)

    def load_address_from_controls(self, _window_employee):
        dict_address = defaultdict(lambda: -1)
        for index in range(0, _window_employee.grid_rows_count):
            if _window_employee.grid_address.GetCellValue(index,0) != "":
                self.dict_address[_window_employee.grid_address.GetCellValue(index,0)] \
                    = _window_employee.grid_address.GetCellValue(index, 1)

    def load_address_from_table(self):
        pass

    @staticmethod
    def get_address_sql(_dict_existing, _dict_current):
        list_sql = []
        for existing_key in _dict_existing.keys():
            if _dict_existing[existing_key]  == _dict_current[existing_key]:
                _dict_current.remove(existing_key)
                continue # no change required

            if  _dict_existing[existing_key]  != "" :
                pass

            if  _dict_current[existing_key]  != "" :
                pass
