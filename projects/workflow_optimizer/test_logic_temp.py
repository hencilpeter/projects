import datetime

prefix="MF"
val = 1
res = "{}{:04d}".format(prefix, val)
print(res)

from collections import defaultdict
employee_id = '101'
def get_address_sql(_dict_existing, _dict_current):
    list_sql = []
    for existing_key in _dict_existing.keys():
        if _dict_existing[existing_key] == _dict_current[existing_key]:
            del _dict_current[existing_key]
            continue  # no change required

        if _dict_existing[existing_key] != _dict_current[existing_key]:  # update case
            list_sql.append(
                "update address set end_date={} where employee_id={} and address_type={} and end_date='9999-12-31'".format(
                    datetime.datetime.today(), employee_id
                    , _dict_current[existing_key],
                    existing_key))
            list_sql.append(
                "insert address(employee_id,address_type,address_value,start_date, end_date) values({},{},{},{}, '9999-12-31')".format(
                    employee_id, existing_key, _dict_current[existing_key],
                    datetime.datetime.now().date()))
            del _dict_current[existing_key]
            continue

        # delete case
        list_sql.append(
            "update address set end_date={} where employee_id={} and address_type={} and end_date='9999-12-31'".format(
                datetime.datetime.today(), employee_id
                , _dict_current[existing_key],
                existing_key))

    for current_key in _dict_current.keys():
        list_sql.append(
            "insert address(employee_id,address_type,address_value,start_date, end_date) values({},{},{},{}, '9999-12-31')".format(
                employee_id, current_key, _dict_current[current_key],
                datetime.datetime.now().date()))

    return list_sql


# employee_id
# address_type
# address_value
# start_date
# end_date




dict1 = defaultdict(lambda :-1)
dict1.update({"key1": "sample key value 1", "key2": "sample key value 2", "key3": "sample key value 3"})
# 1. key1 delete. i.e. update enddate as 9999, 2. key2 - no change.key, 3. key3: update key 3
dict2 =defaultdict(lambda :-1)
dict2.update({"key2": "sample key value 2", "key3": "sample key value 3 updated", "key4": "sample key value 4"})
# key2 - no change.  3. key3: update key  4. key4 insert

sql = get_address_sql(dict1, dict2)
print(sql)
