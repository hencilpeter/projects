import datetime
from datetime import  timedelta
from datetime import datetime as dt


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

# date_str = '09-19-2022'
# date_object = datetime.strptime(date_str, '%m-%d-%Y').date()
# print(date_object)
# test_date = "2014-12-12"
# sample_date = datetime.strptime(test_date, '%Y-%m-%d').date()
# print(sample_date)

# _from_date = '20240101'
# for day_count in range(0, 2):
#     current_date = dt.strptime(_from_date, "%Y%m%d") + datetime.timedelta(days=day_count)
#     print(current_date)
#     current_date = current_date.strftime("%Y%m%d")
#     print(current_date)


input_dt = datetime.datetime(2022, 9, 13)

first = input_dt.replace(day=1)
print('first day of a month:', first.date())
modified = input_dt.replace(month=10, day=1)
print(modified)
res = modified - timedelta(days=1)
val = res.strftime("%Y%m%d")
print(val)
#print('Last day of a previous month is:', res.date())

# test_date = datetime.datetime.strptime('20241216', '%Y%m%d')
# test_date = test_date.replace(month=test_date.month+1, day=1)
# print(test_date)
# res = test_date - timedelta(days=1)
# print("last date : {}".format(res))
# initializing date
test_date = datetime.datetime(2018, 12, 4)

# printing original date
print("The original date is : " + str(test_date))

# getting next month
# using replace to get to last day + offset
# to reach next month
nxt_mnth = test_date.replace(day=28) + datetime.timedelta(days=4)

# subtracting the days from next month date to
# get last date of current Month
res = nxt_mnth - datetime.timedelta(days=nxt_mnth.day)

# printing result
print("Last date of month : " + str(res))
print(res.strftime("%Y%m%d"))


temp_str = 'Week No:14, Dates : [20240401, 20240403, 20240405, 20240406], Work Days : 4, Day Sal : 200.0, Weekly Salary (4 X 200.0) : 800.0'
chunk_length = 70
number_of_chunks = len(temp_str)/chunk_length
chunk_list = []
for start_location in range(0, len(temp_str), chunk_length):
    end_location= len(temp_str) if start_location+chunk_length > len(temp_str) else start_location+chunk_length
    chunk_list.append(temp_str[start_location:end_location])

    #print(temp_str[start_location:end_location])
print(chunk_list)

#mydate = datetime.datetime.now()
import datetime
mydate = datetime.datetime.strptime("20240514", "%Y%m%d")
print(mydate.strftime("%B")+" " + str(mydate.year))
