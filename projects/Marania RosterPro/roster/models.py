from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from employees.models import Team, Employee
from shifts.models import ShiftType

class ScheduleRule(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='schedule_rules')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='weekly')
    min_staffing_percent = models.IntegerField(default=50, validators=[MinValueValidator(1), MaxValueValidator(100)])
    default_rotation_weeks = models.IntegerField(default=4, help_text="Number of weeks in rotation cycle")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Schedule Rule'
        verbose_name_plural = 'Schedule Rules'

    def __str__(self):
        return f"{self.team} - {self.get_frequency_display()}"

class RotationPattern(models.Model):
    rule = models.ForeignKey(ScheduleRule, on_delete=models.CASCADE, related_name='rotation_patterns')
    week_number = models.IntegerField(help_text="Week number in rotation (1-based)")
    shift = models.ForeignKey(ShiftType, on_delete=models.CASCADE)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['rule', 'week_number', 'sort_order']
        unique_together = ['rule', 'week_number', 'shift']

    def __str__(self):
        return f"Week {self.week_number}: {self.shift.code}"

class RosterVersion(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='roster_versions')
    name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.team} - {self.name} ({self.status})"

class DutyAssignment(models.Model):
    roster_version = models.ForeignKey(RosterVersion, on_delete=models.CASCADE, related_name='assignments')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='duty_assignments')
    shift = models.ForeignKey(ShiftType, on_delete=models.CASCADE)
    date = models.DateField()
    is_manual_override = models.BooleanField(default=False)
    overridden_at = models.DateTimeField(null=True, blank=True)
    overridden_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['date', 'shift__start_time']
        unique_together = ['roster_version', 'employee', 'date']

    def __str__(self):
        return f"{self.employee} - {self.shift.code} on {self.date}"

class SwapRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    assignment_from = models.ForeignKey(DutyAssignment, on_delete=models.CASCADE, related_name='swap_requests_from')
    assignment_to = models.ForeignKey(DutyAssignment, on_delete=models.CASCADE, related_name='swap_requests_to')
    requested_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='swap_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Swap: {self.assignment_from.employee} <-> {self.assignment_to.employee}"

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('override', 'Override'),
        ('swap', 'Swap'),
        ('publish', 'Publish'),
    ]
    roster_version = models.ForeignKey(RosterVersion, on_delete=models.CASCADE, null=True, blank=True, related_name='audit_logs')
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M} - {self.action} by {self.user}"
