from django import forms
from .models import ShiftType

class ShiftTypeForm(forms.ModelForm):
    class Meta:
        model = ShiftType
        fields = ['name', 'code', 'start_time', 'end_time', 'is_overnight', 'description', 'is_active']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
