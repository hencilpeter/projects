from old_code.util.date_time_util import DateTimeUtil

from datetime import datetime as dt
import datetime
from collections import defaultdict
from collections import OrderedDict
from collections import deque
import random


class UtilDutyInitializer:
    @staticmethod
    def get_previous_day_shift(current_duty_schedule):
        last_item = current_duty_schedule[next(reversed(current_duty_schedule))]
        return last_item

    @staticmethod
    def get_shift_type(dict_duty_schedule, emp_number, schedule_type, current_date, dict_schedule_history):
        if "weekly" == schedule_type:
            # current_date = dt.strptime(current_date)
            if DateTimeUtil.is_monday(current_date):
                # TODO look at history and decide
                if -1 == dict_duty_schedule[emp_number]:
                    return "night"
                previous_day_shift = UtilDutyInitializer.get_previous_day_shift(dict_duty_schedule[emp_number])
                if "night" == previous_day_shift:
                    return "morning"
                elif "morning" == previous_day_shift:
                    return "evening"
                else:
                    return "night"
            else:
                return UtilDutyInitializer.get_previous_day_shift(dict_duty_schedule[emp_number])

        raise Exception("not implemented exception")

    @staticmethod
    def add_duty(dict_duty_schedule, emp_number, current_date):
        dict_schedule_history = defaultdict(lambda: -1)
        shift_type = UtilDutyInitializer.get_shift_type(dict_duty_schedule=dict_duty_schedule, emp_number=emp_number,
                                                    schedule_type="weekly", current_date=current_date,
                                                    dict_schedule_history=dict_schedule_history)

        if -1 == dict_duty_schedule[emp_number]:
            dict_duty_schedule[emp_number] = OrderedDict()
        current_date_in_yyyymmdd_form = current_date.strftime("%Y%m%d")
        dict_duty_schedule[emp_number][current_date_in_yyyymmdd_form] = shift_type

    @staticmethod
    def assign_default_duty(_from_date, _to_date, _duty_types, emp_numbers):
        # duty assignments
        # consideration- 1. Leave ( given weekly/monthly/till date Leave, availability, willingness, and leave assignment type)
        # 2. schedule type
        # 3. required number of resources
        # duty_types = ['Night', 'Morning', "Evening"]
        # employees = ["r1", "r2", "r3", "r4"]
        days_between = DateTimeUtil.days_between(_from_date, _to_date)
        dict_duty_schedule = defaultdict(lambda: -1)
        # iterate resources
        for emp_number in emp_numbers:
            # iterate dates
            for day_count in range(0, days_between):
                current_date = dt.strptime(_from_date, "%Y%m%d") + datetime.timedelta(days=day_count)
                UtilDutyInitializer.add_duty(dict_duty_schedule=dict_duty_schedule, emp_number=emp_number,
                                         current_date=current_date)

        return dict_duty_schedule

    @staticmethod
    def assign_normal_holidays(dict_duty_schedule, dict_holidays):
        for employee_number in dict_duty_schedule:
            employee_schedule = dict_duty_schedule[employee_number]
            for holiday_date, holiday_name in dict_holidays.items():
                employee_schedule[holiday_date] = holiday_name

        return dict_duty_schedule

    @staticmethod
    def assign_weekly_holidays(dict_duty_schedule, weekly_holidays):
        for employee_number in dict_duty_schedule:
            employee_schedule = dict_duty_schedule[employee_number]
            if -1 == weekly_holidays[employee_number]:
                continue

            weekly_holiday_list = weekly_holidays[employee_schedule]

            # get all the weekdays for the given day (e.g. Wednesday ) and assign leave

    @staticmethod
    def assign_rotation_holidays(dict_duty_schedule, rotation_holidays):
        pass

    @staticmethod
    def assign_leaves(dict_duty_schedule, employee_planned_leaves):
        pass

    # hencil changes - 20240324
    @staticmethod
    def assign_duty_round_robin(_list_emp_ids, _from_date, _to_date, _list_company_holidays,
                                _minimum_daily_required_resource_count):
        days_between = DateTimeUtil.days_between(_from_date, _to_date)
        dict_duty_schedule = defaultdict(lambda: -1)
        dict_emp_leaves = defaultdict(lambda: -1)

        count_daily_leave_emp = len(_list_emp_ids) - _minimum_daily_required_resource_count
        # shuffle the employee ids
        random.shuffle(_list_emp_ids)
        dqueue_emp_ids = deque(_list_emp_ids)

        # holidays list
        list_company_holidays = [str(dt.strptime(holiday, "%Y%m%d")) for holiday in _list_company_holidays]

        for day_count in range(0, days_between):
            current_date = dt.strptime(_from_date, "%Y%m%d") + datetime.timedelta(days=day_count)
            # dict_duty_schedule[current_date] = defaultdict(lambda: -1)
            str_current_date = str(current_date)
            if str_current_date in list_company_holidays:
                # skip duty assignment for public holidays
                continue

            if count_daily_leave_emp > 0:
                dict_duty_schedule[str_current_date] = list(dqueue_emp_ids)[0:_minimum_daily_required_resource_count]
                dict_emp_leaves[str_current_date] = list(dqueue_emp_ids)[_minimum_daily_required_resource_count:]
                dqueue_emp_ids.rotate(count_daily_leave_emp)
            else:
                dict_duty_schedule[str_current_date] = list(dqueue_emp_ids)

        return dict_duty_schedule, dict_emp_leaves

    @staticmethod
    def adjust_duties(dict_employee_details, minimum_daily_required_resource_count):
        pass

    @staticmethod
    def get_leave_dates_dict_by_employee_id(_list_emp_ids, _dict_emp_leaves):
        dict_emp_leaves_dates_by_id = defaultdict(lambda: -1)

        for business_date in _dict_emp_leaves.keys():
            for emp_id in _dict_emp_leaves[business_date]:
                if dict_emp_leaves_dates_by_id[emp_id] == -1:
                    dict_emp_leaves_dates_by_id[emp_id] = list()

                dict_emp_leaves_dates_by_id[emp_id].append(business_date)

        return dict_emp_leaves_dates_by_id

    @staticmethod
    def swap_duties(_dict_duty_schedule, _dict_emp_leaves, _swap_emp_id1, _duty_date_emp_id1, _swap_emp_id2,
                    _duty_date_emp_id2):

        formatted_duty_date_emp_id1 = str(dt.strptime(_duty_date_emp_id1, "%Y%m%d"))
        formatted_duty_date_emp_id2 = str(dt.strptime(_duty_date_emp_id2, "%Y%m%d"))

        # validation
        if _swap_emp_id1 not in _dict_duty_schedule[formatted_duty_date_emp_id1]:
            print("invalid swap duty. employee {} does not have duty on {}.".format(_swap_emp_id1, _duty_date_emp_id1))
            return

        if _swap_emp_id2 not in _dict_duty_schedule[formatted_duty_date_emp_id2]:
            print("invalid swap duty. employee {} does not have duty on {}.".format(_swap_emp_id2, _duty_date_emp_id2))
            return

        if _swap_emp_id1 in _dict_duty_schedule[formatted_duty_date_emp_id1] and _swap_emp_id2 in _dict_duty_schedule[
            formatted_duty_date_emp_id1]:
            print("invalid swap duty. employee {}  and employee has duty on the same date : {}.".format(_swap_emp_id1,
                                                                                                        _swap_emp_id2,
                                                                                                        _duty_date_emp_id1))
            return

        if _swap_emp_id1 in _dict_duty_schedule[formatted_duty_date_emp_id2] and _swap_emp_id2 in _dict_duty_schedule[
            formatted_duty_date_emp_id2]:
            print("invalid swap duty. employee {}  and employee has duty on the same date : {}.".format(_swap_emp_id1,
                                                                                                        _swap_emp_id2,
                                                                                                        formatted_duty_date_emp_id2))
            return

        # swap duties
        UtilDutyInitializer.swap_dict_key_values(_dict=_dict_duty_schedule, _key1=formatted_duty_date_emp_id1,
                                             _value1=_swap_emp_id1,
                                             _key2=formatted_duty_date_emp_id2, _value2=_swap_emp_id2)

        # swap leaves
        UtilDutyInitializer.swap_dict_key_values(_dict=_dict_emp_leaves, _key1=formatted_duty_date_emp_id1,
                                             _value1=_swap_emp_id2,
                                             _key2=formatted_duty_date_emp_id2, _value2=_swap_emp_id1)

    @staticmethod
    def swap_dict_key_values(_dict, _key1, _value1, _key2, _value2):
        # re-assign the value of key 1
        updated_duty_list = _dict[_key1]
        updated_duty_list.remove(_value1)
        updated_duty_list.append(_value2)
        _dict[_key1] = updated_duty_list

        # re-assign the value of key 2
        updated_duty_list = _dict[_key2]
        updated_duty_list.remove(_value2)
        updated_duty_list.append(_value1)
        _dict[_key2] = updated_duty_list

    @staticmethod
    def assign_duty(_dict_duty_schedule, _dict_emp_leaves, _duty_date, _emp_id):
        formatted_duty_date = str(dt.strptime(_duty_date, "%Y%m%d"))

        # assign the duty to the emp id for the given date
        UtilDutyInitializer.assign_dict_list_value(_dict=_dict_duty_schedule, _key=formatted_duty_date, _value=_emp_id)
        # remove the leave for the employee from the given date
        UtilDutyInitializer.remove_dict_list_value(_dict=_dict_emp_leaves, _key=formatted_duty_date, _value=_emp_id)

    @staticmethod
    def assign_leave(_dict_duty_schedule, _dict_emp_leaves, _leave_date, _emp_id):
        formatted_leave_date = str(dt.strptime(_leave_date, "%Y%m%d"))

        # add leave to the emp id for the given date
        UtilDutyInitializer.assign_dict_list_value(_dict=_dict_emp_leaves, _key=formatted_leave_date, _value=_emp_id)

        # remove duty of emp id for the given date if any
        UtilDutyInitializer.remove_dict_list_value(_dict=_dict_duty_schedule, _key=formatted_leave_date, _value=_emp_id)

    @staticmethod
    def assign_dict_list_value(_dict, _key, _value):
        if _dict[_key] == -1:
            _dict[_key] = list()

        if _value not in _dict[_key]:
            _dict[_key].append(_value)

    @staticmethod
    def remove_dict_list_value(_dict, _key, _value):
        if _dict[_key] == -1:
            # print("dictionary does not have the key : {}".format(_key))
            return

        if _value in _dict[_key]:
            _dict[_key].remove(_value)
