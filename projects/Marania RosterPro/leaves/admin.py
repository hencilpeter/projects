from django.contrib import admin
from .models import LeaveRequest, LeaveConfiguration

admin.site.register(LeaveRequest)
admin.site.register(LeaveConfiguration)
