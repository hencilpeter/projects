import calendar
from datetime import date
from collections import defaultdict

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string

from employees.models import Employee, Team
from roster.models import RosterVersion, DutyAssignment
from shifts.models import ShiftType
from leaves.models import LeaveRequest

@login_required
def monthly_report(request, year=None, month=None):
    year = year or date.today().year
    month = month or date.today().month

    teams = Team.objects.all()
    employees = Employee.objects.filter(is_active=True)
    _, last_day = calendar.monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)

    report_data = []
    for emp in employees:
        assignments = DutyAssignment.objects.filter(
            employee=emp,
            date__gte=start_date,
            date__lte=end_date
        ).select_related('shift')

        shift_hours = {'morning': 0, 'afternoon': 0, 'night': 0}
        total_hours = 0
        work_days = 0
        for a in assignments:
            h = a.shift.duration_hours
            total_hours += h
            work_days += 1
            code = a.shift.code.lower()
            if 'morning' in code or code == 'ms':
                shift_hours['morning'] += h
            elif 'afternoon' in code or code == 'as':
                shift_hours['afternoon'] += h
            elif 'night' in code or code == 'ns':
                shift_hours['night'] += h

        approved_leaves = LeaveRequest.objects.filter(
            employee=emp,
            status='approved',
            start_date__lte=end_date,
            end_date__gte=start_date
        )
        leave_days = sum(
            (min(l.end_date, end_date) - max(l.start_date, start_date)).days + 1
            for l in approved_leaves
        )

        days_off = last_day - work_days - leave_days

        report_data.append({
            'employee': emp,
            'teams': ', '.join(emp.teams.values_list('name', flat=True)) or '—',
            'shift_hours': shift_hours,
            'total_hours': round(total_hours, 1),
            'work_days': work_days,
            'leave_days': leave_days,
            'days_off': max(0, days_off),
        })

    report_data.sort(key=lambda x: x['employee'].first_name)

    months = [{'num': m, 'name': date(year, m, 1).strftime('%B')} for m in range(1, 13)]
    prev_m = month - 1 or 12
    prev_y = year if month > 1 else year - 1
    next_m = month + 1 if month < 12 else 1
    next_y = year if month < 12 else year + 1
    prev_date = date(prev_y, prev_m, 1)
    next_date = date(next_y, next_m, 1)

    return render(request, 'reporting/monthly_report.html', {
        'year': year,
        'month': month,
        'month_name': date(year, month, 1).strftime('%B'),
        'report_data': report_data,
        'months': months,
        'prev_date': prev_date,
        'next_date': next_date,
    })

@login_required
def team_report(request, team_id, year=None, month=None):
    year = year or date.today().year
    month = month or date.today().month
    team = get_object_or_404(Team, pk=team_id)

    _, last_day = calendar.monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)

    employees = Employee.objects.filter(teams=team, is_active=True)
    roster = RosterVersion.objects.filter(
        team=team,
        start_date__lte=end_date,
        end_date__gte=start_date,
        status='published'
    ).first()

    report_data = []
    for emp in employees:
        qs = DutyAssignment.objects.filter(
            employee=emp,
            date__gte=start_date,
            date__lte=end_date
        )
        if roster:
            qs = qs.filter(roster_version=roster)
        assignments = qs.select_related('shift')

        total_hours = 0
        work_days = 0
        for a in assignments:
            total_hours += a.shift.duration_hours
            work_days += 1

        report_data.append({
            'employee': emp,
            'total_hours': round(total_hours, 1),
            'work_days': work_days,
        })

    prev_m = month - 1 or 12
    prev_y = year if month > 1 else year - 1
    next_m = month + 1 if month < 12 else 1
    next_y = year if month < 12 else year + 1
    prev_date = date(prev_y, prev_m, 1)
    next_date = date(next_y, next_m, 1)

    return render(request, 'reporting/team_report.html', {
        'team': team,
        'year': year,
        'month': month,
        'month_name': date(year, month, 1).strftime('%B'),
        'report_data': report_data,
        'prev_date': prev_date,
        'next_date': next_date,
    })
