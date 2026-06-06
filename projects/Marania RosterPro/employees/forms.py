from django import forms
from .models import Employee, Department, Team

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['employee_id', 'first_name', 'last_name', 'email', 'phone', 'department', 'teams', 'is_active', 'notes']
        widgets = {
            'teams': forms.SelectMultiple(attrs={'class': 'form-control', 'size': 5}),
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code']

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'code', 'department', 'description']
