from django import forms
from .models import ScheduleRule, RotationPattern, RosterVersion
from employees.models import Team
from shifts.models import ShiftType

class ScheduleRuleForm(forms.ModelForm):
    class Meta:
        model = ScheduleRule
        fields = ['team', 'frequency', 'min_staffing_percent', 'default_rotation_weeks', 'is_active']

class RotationPatternForm(forms.Form):
    week_number = forms.IntegerField(min_value=1, max_value=52)
    shift = forms.ModelChoiceField(queryset=ShiftType.objects.filter(is_active=True))

class RosterGenerateForm(forms.Form):
    team = forms.ModelChoiceField(queryset=Team.objects.all(), label="Team")
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    name = forms.CharField(max_length=200, required=False, help_text="Optional roster name")
    overwrite = forms.BooleanField(required=False, initial=True, help_text="Overwrite existing draft roster for this period")
