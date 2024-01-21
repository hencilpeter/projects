from util.date_time_util import DateTimeUtil

from datetime import datetime as dt
import datetime
from collections import defaultdict
from collections import OrderedDict

class DutyInitializer:
    @staticmethod
    def get_previous_day_shift(current_duty_schedule):
        last_item = current_duty_schedule[next(reversed(current_duty_schedule))]
        return last_item
        #length_duty_schedule = len(current_duty_schedule)
        #return current_duty_schedule[length_duty_schedule - 1][1]

    @staticmethod
    def get_shift_type(dict_duty_schedule, emp_number, schedule_type, current_date, dict_schedule_history):
        if "weekly" == schedule_type:
            # current_date = dt.strptime(current_date)
            if DateTimeUtil.is_monday(current_date):
                # TODO look at history and decide
                if -1 == dict_duty_schedule[emp_number]:
                    return "night"
                previous_day_shift = DutyInitializer.get_previous_day_shift(dict_duty_schedule[emp_number])
                if "night" == previous_day_shift:
                    return "morning"
                elif "morning" == previous_day_shift:
                    return "evening"
                else:
                    return "night"
            else:
                return DutyInitializer.get_previous_day_shift(dict_duty_schedule[emp_number])

        raise Exception("not implemented exception")

    @staticmethod
    def add_duty(dict_duty_schedule, emp_number, current_date):
        dict_schedule_history = defaultdict(lambda: -1)
        shift_type = DutyInitializer.get_shift_type(dict_duty_schedule=dict_duty_schedule, emp_number=emp_number,
                                                    schedule_type="weekly", current_date=current_date,
                                                    dict_schedule_history=dict_schedule_history)

        if -1 == dict_duty_schedule[emp_number]:
            dict_duty_schedule[emp_number] = OrderedDict()
        #     dict_duty_schedule[emp_number] = {[current_date, shift_type]}
        # else:
        #     dict_duty_schedule[emp_number].append([current_date, shift_type])
        dict_duty_schedule[emp_number][current_date] = shift_type



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
                DutyInitializer.add_duty(dict_duty_schedule=dict_duty_schedule, emp_number=emp_number,
                                         current_date=current_date)

        return dict_duty_schedule
        #print(dict_duty_schedule)

    @staticmethod
    def assign_public_holidays(dict_duty_schedule, public_holidays):
        pass

    @staticmethod
    def assign_weekend_holidays(dict_duty_schedule, weekend_holidays):
        pass

    @staticmethod
    def assign_rotation_holidays(dict_duty_schedule, rotation_holidays):
        pass

    @staticmethod
    def assign_leaves(dict_duty_schedule, employee_planned_leaves):
        pass

    @staticmethod
    def adjust_duties(dict_duty_schedule, employee_planned_leaves):
        pass


