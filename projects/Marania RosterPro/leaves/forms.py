from django import forms
from .models import LeaveRequest, LeaveConfiguration
from employees.models import Employee

class LeaveRequestForm(forms.ModelForm):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(is_active=True),
        required=False,
        label="Employee (leave blank for yourself)"
    )

    class Meta:
        model = LeaveRequest
        fields = ['employee', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

class LeaveConfigForm(forms.ModelForm):
    class Meta:
        model = LeaveConfiguration
        fields = ['max_leave_days_per_month', 'requires_approval']
