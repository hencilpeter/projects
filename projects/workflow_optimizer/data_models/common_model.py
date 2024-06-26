import datetime
import json
from collections import defaultdict

class CommonModel:
    @staticmethod
    def get_scd2_sql(_dict_existing, _dict_current, _employee_id, _column_type, _column_value, _table_name):
        list_sql = []
        for existing_key in _dict_existing.keys():
            if _dict_existing[existing_key] == _dict_current[existing_key]:
                del _dict_current[existing_key]
                continue  # no change required

            list_sql.append(
                "update {} set end_date='{}' where employee_number='{}' and {}='{}' and end_date='9999-12-31'".format(
                    _table_name, datetime.datetime.today().strftime('%Y-%m-%d'), _employee_id, _column_type,
                    existing_key))

            if _dict_current[existing_key] != -1:
                list_sql.append(
                    "insert into {}(employee_number,{},{},start_date, end_date) values('{}','{}','{}','{}', '9999-12-31')".format(
                        _table_name, _column_type, _column_value,
                        _employee_id, existing_key, _dict_current[existing_key],
                        datetime.datetime.today().strftime('%Y-%m-%d')))
                del _dict_current[existing_key]

        for current_key in _dict_current.keys():
            if _dict_current[current_key] != -1:
                list_sql.append(
                    "insert into {}(employee_number,{},{},start_date, end_date) values('{}','{}','{}','{}', '9999-12-31')".format(
                        _table_name, _column_type, _column_value,
                        _employee_id, current_key, _dict_current[current_key],
                        datetime.datetime.today().strftime('%Y-%m-%d')))

        return list_sql

    @staticmethod
    def get_table_data_as_list(_data_cursor):
        column_names = [description[0] for description in _data_cursor.description]
        result = []
        for row in _data_cursor:
            str_row = ""
            list_current_row_columns = []
            for col_name in column_names:
                list_current_row_columns.append("\"" + str(col_name) + "\":\"" + str(row[column_names.index(col_name)])
                                                + "\"")
            str_row = "{" + ','.join(list_current_row_columns) + "}"
            result.append(str_row)
        return result

    @staticmethod
    def get_list_dict_value_from_key(_list_dict, _key_column, _expected_key_column_value, _value_column):
        for dict_str in _list_dict:
            dict_temp = json.loads(dict_str)
            if dict_temp[_key_column] == _expected_key_column_value:
                return dict_temp[_value_column]

        return None

    @staticmethod
    def get_dict_from_list(_list_dict, _key_column):
        dict_result = defaultdict(lambda: -1)
        for dict_str in _list_dict:
            dict_temp = json.loads(dict_str)
            if _key_column in dict_temp.keys():
                dict_result[dict_temp[_key_column]] = dict_temp

        return dict_result
