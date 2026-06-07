import calendar as cal_module
from datetime import date, timedelta
from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import admin_or_hr_required
from .models import ScheduleRule, RotationPattern, RosterVersion, DutyAssignment, SwapRequest, AuditLog
from .forms import ScheduleRuleForm, RotationPatternForm, RosterGenerateForm
from .scheduler import SchedulerEngine
from employees.models import Team, Employee
from shifts.models import ShiftType
from leaves.models import LeaveRequest

@login_required
def roster_list(request):
    rosters = RosterVersion.objects.all().select_related('team', 'created_by')
    return render(request, 'roster/roster_list.html', {'rosters': rosters})

@admin_or_hr_required
def roster_generate(request):
    if request.method == 'POST':
        form = RosterGenerateForm(request.POST)
        if form.is_valid():
            teams = form.cleaned_data['teams']
            start = form.cleaned_data['start_date']
            end = form.cleaned_data['end_date']
            name = form.cleaned_data.get('name')
            overwrite = form.cleaned_data.get('overwrite', True)
            generated = []
            errors = []
            for team in teams:
                try:
                    engine = SchedulerEngine(team, start, end, user=request.user)
                    roster = engine.generate(name=name, overwrite=overwrite)
                    generated.append(roster)
                except ValueError as e:
                    errors.append(f"{team.name}: {e}")
            if generated:
                messages.success(request, f'Rosters generated for {len(generated)} team(s).')
            for e in errors:
                messages.error(request, e)
            return redirect('roster:roster_list')
    else:
        form = RosterGenerateForm()
    return render(request, 'roster/roster_generate.html', {'form': form})

@login_required
def roster_detail(request, pk):
    roster = get_object_or_404(RosterVersion.objects.select_related('team', 'created_by'), pk=pk)
    assignments = roster.assignments.all().select_related('employee', 'shift').order_by('date', 'shift__start_time')
    by_date = defaultdict(list)
    for a in assignments:
        by_date[a.date].append(a)
    return render(request, 'roster/roster_detail.html', {
        'roster': roster,
        'by_date': dict(by_date),
    })

@admin_or_hr_required
def roster_publish(request, pk):
    roster = get_object_or_404(RosterVersion, pk=pk)
    roster.status = 'published'
    roster.save()
    AuditLog.objects.create(
        roster_version=roster,
        user=request.user,
        action='publish',
        description=f"Roster published: {roster}"
    )
    messages.success(request, 'Roster published.')
    return redirect('roster:roster_detail', pk=roster.pk)

@admin_or_hr_required
def roster_delete(request, pk):
    roster = get_object_or_404(RosterVersion, pk=pk)
    if request.method == 'POST':
        roster.delete()
        messages.success(request, 'Roster deleted.')
        return redirect('roster:roster_list')
    return render(request, 'roster/roster_confirm_delete.html', {'roster': roster})

@admin_or_hr_required
def assignment_override(request, pk):
    assignment = get_object_or_404(DutyAssignment, pk=pk)
    if request.method == 'POST':
        shift_id = request.POST.get('shift')
        if shift_id:
            shift = get_object_or_404(ShiftType, pk=shift_id)
            old_shift = assignment.shift
            assignment.shift = shift
            assignment.is_manual_override = True
            from django.utils import timezone
            assignment.overridden_at = timezone.now()
            assignment.overridden_by = request.user
            assignment.save()
            AuditLog.objects.create(
                roster_version=assignment.roster_version,
                user=request.user,
                action='override',
                description=f"Override: {assignment.employee} shift changed from {old_shift} to {shift} on {assignment.date}"
            )
            messages.success(request, 'Assignment updated.')
        return redirect('roster:roster_detail', pk=assignment.roster_version.pk)
    shifts = ShiftType.objects.filter(is_active=True)
    return render(request, 'roster/assignment_override.html', {'assignment': assignment, 'shifts': shifts})

@admin_or_hr_required
def swap_shifts(request, pk):
    roster = get_object_or_404(RosterVersion, pk=pk)
    if request.method == 'POST':
        a1_id = request.POST.get('assignment1')
        a2_id = request.POST.get('assignment2')
        if a1_id and a2_id:
            a1 = get_object_or_404(DutyAssignment, pk=a1_id)
            a2 = get_object_or_404(DutyAssignment, pk=a2_id)
            a1.employee, a2.employee = a2.employee, a1.employee
            a1.is_manual_override = True
            a2.is_manual_override = True
            from django.utils import timezone
            a1.overridden_at = timezone.now()
            a2.overridden_at = timezone.now()
            a1.overridden_by = request.user
            a2.overridden_by = request.user
            a1.save()
            a2.save()
            AuditLog.objects.create(
                roster_version=roster,
                user=request.user,
                action='swap',
                description=f"Swap: {a1.employee} <-> {a2.employee} on {a1.date}"
            )
            messages.success(request, 'Shifts swapped.')
        return redirect('roster:roster_detail', pk=roster.pk)
    assignments = roster.assignments.all().select_related('employee', 'shift').order_by('date')
    return render(request, 'roster/swap_shifts.html', {'roster': roster, 'assignments': assignments})

@admin_or_hr_required
def schedule_rules(request):
    rules = ScheduleRule.objects.all().select_related('team')
    return render(request, 'roster/schedule_rules.html', {'rules': rules})

@admin_or_hr_required
def schedule_rule_create(request):
    if request.method == 'POST':
        form = ScheduleRuleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Schedule rule created.')
            return redirect('roster:schedule_rules')
    else:
        form = ScheduleRuleForm()
    return render(request, 'roster/schedule_rule_form.html', {'form': form, 'title': 'Add Schedule Rule'})

@admin_or_hr_required
def schedule_rule_update(request, pk):
    rule = get_object_or_404(ScheduleRule, pk=pk)
    if request.method == 'POST':
        form = ScheduleRuleForm(request.POST, instance=rule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Schedule rule updated.')
            return redirect('roster:schedule_rules')
    else:
        form = ScheduleRuleForm(instance=rule)
    return render(request, 'roster/schedule_rule_form.html', {'form': form, 'title': 'Edit Schedule Rule'})

@admin_or_hr_required
def rotation_patterns(request, rule_pk):
    rule = get_object_or_404(ScheduleRule, pk=rule_pk)
    patterns = RotationPattern.objects.filter(rule=rule).select_related('shift')
    return render(request, 'roster/rotation_patterns.html', {'rule': rule, 'patterns': patterns})

@admin_or_hr_required
def rotation_pattern_add(request, rule_pk):
    rule = get_object_or_404(ScheduleRule, pk=rule_pk)
    if request.method == 'POST':
        form = RotationPatternForm(request.POST)
        if form.is_valid():
            week = form.cleaned_data['week_number']
            shift = form.cleaned_data['shift']
            count = RotationPattern.objects.filter(rule=rule, week_number=week).count()
            RotationPattern.objects.create(rule=rule, week_number=week, shift=shift, sort_order=count)
            messages.success(request, f'Shift {shift} added to week {week}.')
            return redirect('roster:rotation_patterns', rule_pk=rule.pk)
    else:
        form = RotationPatternForm()
    return render(request, 'roster/rotation_pattern_form.html', {'form': form, 'rule': rule})

@admin_or_hr_required
def rotation_pattern_delete(request, pk):
    pattern = get_object_or_404(RotationPattern, pk=pk)
    rule_pk = pattern.rule_id
    pattern.delete()
    messages.success(request, 'Rotation pattern removed.')
    return redirect('roster:rotation_patterns', rule_pk=rule_pk)

@login_required
def combined_roster(request, year=None, month=None):
    year = year or date.today().year
    month = month or date.today().month
    _, last_day = cal_module.monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)

    rosters = RosterVersion.objects.filter(
        start_date__lte=end_date,
        end_date__gte=start_date,
    ).filter(status__in=['draft', 'published']).select_related('team')

    assignments = DutyAssignment.objects.filter(
        roster_version__in=rosters,
        date__gte=start_date,
        date__lte=end_date,
    ).select_related('employee', 'shift', 'roster_version__team').order_by('date', 'shift__start_time', 'roster_version__team__name')

    cal = cal_module.Calendar()
    weeks = []
    by_date_team = defaultdict(lambda: defaultdict(list))
    for a in assignments:
        by_date_team[a.date][a.roster_version.team].append(a)

    for week in cal.monthdayscalendar(year, month):
        week_data = []
        for day in week:
            if day == 0:
                week_data.append(None)
            else:
                d = date(year, month, day)
                week_data.append((d, dict(by_date_team.get(d, {}))))
        weeks.append(week_data)

    prev_m = month - 1 or 12
    prev_y = year if month > 1 else year - 1
    next_m = month + 1 if month < 12 else 1
    next_y = year if month < 12 else year + 1

    return render(request, 'roster/combined_roster.html', {
        'year': year,
        'month': month,
        'month_name': date(year, month, 1).strftime('%B'),
        'weeks': weeks,
        'rosters': rosters,
        'prev_year': prev_y,
        'prev_month': prev_m,
        'prev_month_name': date(prev_y, prev_m, 1).strftime('%B'),
        'next_year': next_y,
        'next_month': next_m,
        'next_month_name': date(next_y, next_m, 1).strftime('%B'),
    })

@login_required
def combined_roster_print(request, year=None, month=None):
    year = year or date.today().year
    month = month or date.today().month
    _, last_day = cal_module.monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)

    rosters = RosterVersion.objects.filter(
        start_date__lte=end_date,
        end_date__gte=start_date,
    ).filter(status__in=['draft', 'published']).select_related('team')

    assignments = DutyAssignment.objects.filter(
        roster_version__in=rosters,
        date__gte=start_date,
        date__lte=end_date,
    ).select_related('employee', 'shift', 'roster_version__team').order_by('date', 'shift__start_time', 'roster_version__team__name')

    cal = cal_module.Calendar()
    weeks = []
    by_date_team = defaultdict(lambda: defaultdict(list))
    for a in assignments:
        by_date_team[a.date][a.roster_version.team].append(a)

    for week in cal.monthdayscalendar(year, month):
        week_data = []
        for day in week:
            if day == 0:
                week_data.append(None)
            else:
                d = date(year, month, day)
                week_data.append((d, dict(by_date_team.get(d, {}))))
        weeks.append(week_data)

    return render(request, 'roster/combined_roster_print.html', {
        'year': year,
        'month': month,
        'month_name': date(year, month, 1).strftime('%B'),
        'weeks': weeks,
        'rosters': rosters,
    })

@login_required
def roster_calendar(request, pk, year=None, month=None):
    roster = get_object_or_404(RosterVersion.objects.select_related('team', 'created_by'), pk=pk)
    year = year or date.today().year
    month = month or date.today().month

    _, last_day = cal_module.monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)

    assignments = roster.assignments.filter(
        date__gte=start_date, date__lte=end_date
    ).select_related('employee', 'shift').order_by('date', 'shift__start_time')

    by_date = defaultdict(list)
    for a in assignments:
        by_date[a.date].append(a)

    team_members = Employee.objects.filter(teams=roster.team, is_active=True)

    leaves_in_range = LeaveRequest.objects.filter(
        employee__teams=roster.team,
        status='approved',
        start_date__lte=end_date,
        end_date__gte=start_date
    ).select_related('employee')

    cal = cal_module.Calendar()
    weeks = []
    for week in cal.monthdayscalendar(year, month):
        week_data = []
        for day in week:
            if day == 0:
                week_data.append(None)
            else:
                d = date(year, month, day)
                week_data.append((d, by_date.get(d, [])))
        weeks.append(week_data)

    prev_m = month - 1 or 12
    prev_y = year if month > 1 else year - 1
    next_m = month + 1 if month < 12 else 1
    next_y = year if month < 12 else year + 1

    return render(request, 'roster/roster_calendar.html', {
        'roster': roster,
        'year': year,
        'month': month,
        'month_name': date(year, month, 1).strftime('%B'),
        'weeks': weeks,
        'team_members': team_members,
        'leaves': leaves_in_range,
        'prev_year': prev_y,
        'prev_month': prev_m,
        'prev_month_name': date(prev_y, prev_m, 1).strftime('%B'),
        'next_year': next_y,
        'next_month': next_m,
        'next_month_name': date(next_y, next_m, 1).strftime('%B'),
    })
