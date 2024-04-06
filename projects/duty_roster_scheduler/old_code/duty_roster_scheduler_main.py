from old_code.scheduler.duty_initializer import DutyInitializer
from old_code.util import DictUtil

from old_code.util.date_time_util import DateTimeUtil
from collections import defaultdict


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
    employee_numbers = ["r1", "r2", "r3", "r4","r5", "r6"]
    public_holidays = {"20240101": "holiday_new_year"}
    weekly_holidays = defaultdict(lambda: -1)
    weekly_holidays.update({"r1": ["sunday"], "r2": ["saturday", "sunday"]})



    # # 1. assign default duty to all the employees
    # dict_duty_schedule = duty_initializer.assign_default_duty('20240101', '20240131', duty_types, employee_numbers)
    #
    # # 2. assign public holidays
    # dict_duty_schedule_public_holidays = duty_initializer.assign_normal_holidays(dict_duty_schedule=dict_duty_schedule,
    #                                                                              dict_holidays=public_holidays)

    # new round-robin approach
    list_company_holidays = ['20240402', '20240415', '20240419']
    dict_duty_schedule, dict_emp_leaves = DutyInitializer.assign_duty_round_robin(_list_emp_ids=employee_numbers,
                                                                                   _from_date='20240401',
                                                                                   _to_date='20240430',
                                                                                   _list_company_holidays=list_company_holidays,
                                                                                   _minimum_daily_required_resource_count=3)


    dict_emp_leaves_dates_by_id = DutyInitializer.get_leave_dates_dict_by_employee_id(
        _list_emp_ids=employee_numbers, _dict_emp_leaves=dict_emp_leaves)


    # DictUtil.write_dict_to_csv(_dict=dict_duty_schedule,
    #                            _csv_file_name="C:\\Users\\User\\Documents\\GitHub\\projects\\duty_roster_scheduler\\csv\\emp_duty_schedule.csv")
    #
    # DictUtil.write_dict_to_csv(_dict=dict_emp_leaves,
    #                            _csv_file_name="C:\\Users\\User\\Documents\\GitHub\\projects\\duty_roster_scheduler\\csv\\emp_leaves.csv")
    #
    # DictUtil.write_dict_to_csv(_dict=dict_emp_leaves_dates_by_id,
    #                            _csv_file_name="C:\\Users\\User\\Documents\\GitHub\\projects\\duty_roster_scheduler\\csv\\emp_leaves_dates_by_ids.csv")

    # load test dictionaries
    test_dict_duty_schedule = DictUtil.read_dict_from_csv(
        _csv_file_name="csv/emp_duty_schedule.csv")
    test_dict_emp_leaves = DictUtil.read_dict_from_csv(
        _csv_file_name="csv/emp_leaves.csv")
    test_dict_emp_leaves_dates_by_id = DictUtil.read_dict_from_csv(
        _csv_file_name="csv/emp_leaves_dates_by_ids.csv")
    # test swap duties
    DutyInitializer.swap_duties(_dict_duty_schedule=test_dict_duty_schedule, _dict_emp_leaves=test_dict_emp_leaves,
                                _swap_emp_id1='r4', _duty_date_emp_id1='20240401', _swap_emp_id2='r3', _duty_date_emp_id2='20240403')
    # test assign duty
    DutyInitializer.assign_duty(_dict_duty_schedule=test_dict_duty_schedule, _dict_emp_leaves=test_dict_emp_leaves,
                                _duty_date='20240404', _emp_id='r3')

    # test assign leave
    DutyInitializer.assign_leave(_dict_duty_schedule=test_dict_duty_schedule, _dict_emp_leaves=test_dict_emp_leaves,
                                 _leave_date='20240405', _emp_id='r1')

    # save html logic -
    from old_code.html import html_duty_viewer

    html_duty_viewer = html_duty_viewer.HtmlDutyViewer(
        _header_name="Duty Schedule  ( {} - {}) ".format('20240401', '20240430'), _footer="End of the Document")

    html_duty_viewer.add_table_row_header_with_two_column(_col1_header="Date", _col2_header = "Employee Name(s)")

    for business_date in test_dict_duty_schedule.keys():
        list_emp_ids = test_dict_duty_schedule[business_date]
        list_emp_ids.sort()
        formatted_emp_ids = ""
        for count in range(1, len(list_emp_ids)+1):
            formatted_emp_ids = formatted_emp_ids + "| {}. {} ".format(count, list_emp_ids[count-1] )
            formatted_business_date = business_date[:10]
            formatted_business_date = formatted_business_date + " (" + DateTimeUtil.get_day_from_date(str(formatted_business_date).replace('-','')) + ")"
        html_duty_viewer.add_table_row_values_with_two_column(_col1_value=formatted_business_date, _col2_value=formatted_emp_ids)

    html_duty_viewer.save_html_file("C:\\Users\\User\\Documents\\GitHub\\projects\\duty_roster_scheduler\\csv\\duty_schedult.html")
    # test_dict_duty_schedule

    print('PyCharm')
