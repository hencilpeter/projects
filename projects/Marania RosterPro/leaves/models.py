from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from employees.models import Employee

class LeaveConfiguration(models.Model):
    max_leave_days_per_month = models.IntegerField(default=4, validators=[MinValueValidator(1)])
    requires_approval = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Leave Configuration'
        verbose_name_plural = 'Leave Configuration'

    def __str__(self):
        return f"Max {self.max_leave_days_per_month} days/month"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_config(cls):
        config, _ = cls.objects.get_or_create(pk=1)
        return config

class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.employee} - {self.start_date} to {self.end_date} ({self.status})"

    @property
    def leave_days(self):
        return (self.end_date - self.start_date).days + 1
