import datetime


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
