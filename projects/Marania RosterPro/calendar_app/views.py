import calendar
from datetime import date, timedelta
from collections import defaultdict

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from employees.models import Employee, Team
from roster.models import RosterVersion, DutyAssignment
from shifts.models import ShiftType

def _build_month_calendar(year, month):
    cal = calendar.Calendar()
    weeks = []
    for week in cal.monthdayscalendar(year, month):
        week_data = []
        for day in week:
            if day == 0:
                week_data.append(None)
            else:
                week_data.append(date(year, month, day))
        weeks.append(week_data)
    return weeks

def _get_month_range(year, month):
    _, last_day = calendar.monthrange(year, month)
    return date(year, month, 1), date(year, month, last_day)

@login_required
def team_calendar(request, team_id=None, year=None, month=None):
    year = year or date.today().year
    month = month or date.today().month
    teams = Team.objects.all()
    selected_team = None
    months = []

    if team_id:
        selected_team = get_object_or_404(Team, pk=team_id)

    start, end = _get_month_range(year, month)
    weeks = _build_month_calendar(year, month)

    assignments_by_date = {}
    if selected_team:
        roster = RosterVersion.objects.filter(
            team=selected_team,
            start_date__lte=end,
            end_date__gte=start,
        ).filter(status__in=['draft', 'published']).first()

        if roster:
            assignments = DutyAssignment.objects.filter(
                roster_version=roster,
                date__gte=start,
                date__lte=end
            ).select_related('employee', 'shift')

            by_date = defaultdict(list)
            for a in assignments:
                by_date[a.date].append(a)
            assignments_by_date = dict(by_date)

    # Build calendar_data with (date, assignments) pairs
    calendar_data = []
    for week in weeks:
        week_data = []
        for d in week:
            week_data.append((d, assignments_by_date.get(d, [])) if d else None)
        calendar_data.append(week_data)

    roster = roster if selected_team else None

    for m in range(1, 13):
        months.append({'num': m, 'name': date(year, m, 1).strftime('%B')})

    prev_m = month - 1 or 12
    prev_y = year if month > 1 else year - 1
    next_m = month + 1 if month < 12 else 1
    next_y = year if month < 12 else year + 1
    prev_date = date(prev_y, prev_m, 1)
    next_date = date(next_y, next_m, 1)

    return render(request, 'calendar/team_calendar.html', {
        'teams': teams,
        'selected_team': selected_team,
        'year': year,
        'month': month,
        'month_name': date(year, month, 1).strftime('%B'),
        'weeks': weeks,
        'calendar_data': calendar_data,
        'months': months,
        'prev_date': prev_date,
        'next_date': next_date,
        'roster': roster,
    })

@login_required
def employee_calendar(request, emp_id=None, year=None, month=None):
    year = year or date.today().year
    month = month or date.today().month

    from django.contrib import messages
    from django.shortcuts import redirect

    if emp_id:
        employee = get_object_or_404(Employee, pk=emp_id)
    else:
        employee = Employee.objects.filter(user=request.user).first()
        if not employee:
            messages.warning(request, 'Select an employee to view their calendar.')
            return redirect('employees:employee_list')

    start, end = _get_month_range(year, month)
    weeks = _build_month_calendar(year, month)

    leaves = employee.leave_requests.filter(
        status='approved',
        start_date__lte=end,
        end_date__gte=start
    )

    leaf_dates = set()
    for leave in leaves:
        d = max(leave.start_date, start)
        end_d = min(leave.end_date, end)
        while d <= end_d:
            leaf_dates.add(d)
            d += timedelta(days=1)

    assignments = DutyAssignment.objects.filter(
        employee=employee,
        date__gte=start,
        date__lte=end
    ).select_related('shift')

    by_date = {}
    total_hours = {'morning': 0, 'afternoon': 0, 'night': 0, 'total': 0}
    for a in assignments:
        by_date[a.date] = {
            'shift_code': a.shift.code,
            'shift_name': a.shift.name,
            'time_range': a.shift.time_range,
            'duration': a.shift.duration_hours,
        }
        h = a.shift.duration_hours
        total_hours['total'] += h
        code = a.shift.code.lower()
        if 'morning' in code.lower() or 'ms' == code.lower():
            total_hours['morning'] += h
        elif 'afternoon' in code.lower() or 'as' == code.lower():
            total_hours['afternoon'] += h
        elif 'night' in code.lower() or 'ns' == code.lower():
            total_hours['night'] += h

    work_days = len(assignments)
    days_off = sum(1 for w in weeks for d in w if d and d not in by_date and d not in leaf_dates)

    prev_m = month - 1 or 12
    prev_y = year if month > 1 else year - 1
    next_m = month + 1 if month < 12 else 1
    next_y = year if month < 12 else year + 1
    prev_date = date(prev_y, prev_m, 1)
    next_date = date(next_y, next_m, 1)

    return render(request, 'calendar/employee_calendar.html', {
        'employee': employee,
        'year': year,
        'month': month,
        'month_name': date(year, month, 1).strftime('%B'),
        'weeks': weeks,
        'by_date': by_date,
        'leaf_dates': leaf_dates,
        'total_hours': total_hours,
        'work_days': work_days,
        'days_off': days_off,
        'leaves': leaves,
        'prev_date': prev_date,
        'next_date': next_date,
    })
