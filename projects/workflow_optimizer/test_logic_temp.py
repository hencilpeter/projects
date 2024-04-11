import datetime

prefix = "MF"
val = 1
res = "{}{:04d}".format(prefix, val)
print(res)

from collections import defaultdict

employee_id = '101'


def get_scd2_sql(_dict_existing, _dict_current, _employee_id, _column_type, _column_value, _table_name):
    list_sql = []
    for existing_key in _dict_existing.keys():
        if _dict_existing[existing_key] == _dict_current[existing_key]:
            del _dict_current[existing_key]
            continue  # no change required

        list_sql.append(
            "update {} set end_date='{}' where employee_id='{}' and {}='{}' and end_date='9999-12-31'".format(
                _table_name, datetime.datetime.today().strftime('%Y-%m-%d'), employee_id, _column_type, existing_key))

        if _dict_current[existing_key] != -1:
            list_sql.append(
                "insert {}(employee_id,{},{},start_date, end_date) values('{}','{}','{}','{}', '9999-12-31')".format(
                    _table_name, _column_type, _column_value,
                    employee_id, existing_key, _dict_current[existing_key],
                    datetime.datetime.today().strftime('%Y-%m-%d')))
            del _dict_current[existing_key]

    for current_key in _dict_current.keys():
        if _dict_current[current_key] != -1:
            list_sql.append(
                "insert {}(employee_id,{},{},start_date, end_date) values('{}','{}','{}','{}', '9999-12-31')".format(
                    _table_name, _column_type, _column_value,
                    employee_id, current_key, _dict_current[current_key],
                    datetime.datetime.today().strftime('%Y-%m-%d')))

    return list_sql


dict1 = defaultdict(lambda: -1)
dict1.update({"key1": "sample key value 1", "key2": "sample key value 2", "key3": "sample key value 3"})
# 1. key1 delete. i.e. update enddate as 9999, 2. key2 - no change.key, 3. key3: update key 3
dict2 = defaultdict(lambda: -1)
dict2.update({"key2": "sample key value 2", "key3": "sample key value 3 updated", "key4": "sample key value 4"})
# key2 - no change.  3. key3: update key  4. key4 insert

sql = get_scd2_sql(_dict_existing=dict1, _dict_current=dict2, _employee_id=employee_id, _table_name="address",
                   _column_type="address_type", _column_value="address_value")
for item in sql:
    print(item)

from datetime import datetime
date_str = '09-19-2022'
date_object = datetime.strptime(date_str, '%m-%d-%Y').date()
print(date_object)
test_date = "2014-12-12"
sample_date = datetime.strptime(test_date, '%Y-%m-%d').date()
print(sample_date)
