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

@login_required
def roster_list(request):
    rosters = RosterVersion.objects.all().select_related('team', 'created_by')
    return render(request, 'roster/roster_list.html', {'rosters': rosters})

@admin_or_hr_required
def roster_generate(request):
    if request.method == 'POST':
        form = RosterGenerateForm(request.POST)
        if form.is_valid():
            team = form.cleaned_data['team']
            start = form.cleaned_data['start_date']
            end = form.cleaned_data['end_date']
            name = form.cleaned_data.get('name')
            overwrite = form.cleaned_data.get('overwrite', True)
            try:
                engine = SchedulerEngine(team, start, end, user=request.user)
                roster = engine.generate(name=name, overwrite=overwrite)
                messages.success(request, f'Roster generated: {roster}')
                return redirect('roster:roster_detail', pk=roster.pk)
            except ValueError as e:
                messages.error(request, str(e))
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
