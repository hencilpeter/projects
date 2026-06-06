from django.contrib import admin
from .models import ScheduleRule, RotationPattern, RosterVersion, DutyAssignment, SwapRequest, AuditLog

admin.site.register(ScheduleRule)
admin.site.register(RotationPattern)
admin.site.register(RosterVersion)
admin.site.register(DutyAssignment)
admin.site.register(SwapRequest)
admin.site.register(AuditLog)
