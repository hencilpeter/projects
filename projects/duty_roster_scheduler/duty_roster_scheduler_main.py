from scheduler.duty_initializer import DutyInitializer


# from util.date_time_util import DateTimeUtil


def create_schedule():
    pass


if __name__ == '__main__':
    duty_initializer = DutyInitializer()
    #
    # # start and end date
    # from_date = '20240101'
    # to_date = '20240131'
    #
    # # duty assignments
    # # consideration- 1. Leave ( given weekly/monthly/till date Leave, availability, willingness, and leave assignment type)
    # # 2. schedule type
    # # 3. required number of resources
    # duty_types = ['Night', 'Morning', "Evening"]
    # employees = ["r1", "r2", "r3", "r4"]
    #
    # days_between =  days_between(from_date, to_date)
    # dict_duty_schedule =  defaultdict(lambda : -1)
    # # iterate resources
    # for emp_number in employees:
    #     # iterate dates
    #     for day_count in range(0, days_between):
    #         current_date =    dt.strptime(from_date, "BY*m*a") + datetime.timedelta(days=day_count)
    #         add_duty(dict_duty_schedule=dict_duty_schedule, emp_number=emp_number, current_date=current_date)
    duty_types = ['Night', 'Morning', "Evening"]
    employee_numbers = ["r1", "r2", "r3", "r4"]
    public_holidays = ["20230101"]
    weekend_holidays = {"r1": ["sunday"]}


    duty_initializer.assign_default_duty('20240101','20240131', duty_types, employee_numbers)
    print('PyCharm')
