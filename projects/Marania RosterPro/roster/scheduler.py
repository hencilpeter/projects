import datetime
from collections import defaultdict
from .models import ScheduleRule, RotationPattern, RosterVersion, DutyAssignment, AuditLog
from leaves.models import LeaveRequest
from employees.models import Employee
from shifts.models import ShiftType

class SchedulerEngine:

    def __init__(self, team, start_date, end_date, user=None):
        self.team = team
        self.start_date = start_date
        self.end_date = end_date
        self.user = user
        self.rule = ScheduleRule.objects.filter(team=team, is_active=True).first()
        if not self.rule:
            raise ValueError(f"No active schedule rule found for team {team}")

    def generate(self, name=None, overwrite=False):
        if not name:
            name = f"Roster - {self.team.name} ({self.start_date} to {self.end_date})"

        existing = RosterVersion.objects.filter(
            team=self.team,
            start_date=self.start_date,
            end_date=self.end_date,
            status='draft'
        ).first()

        if existing and not overwrite:
            return existing

        if existing and overwrite:
            existing.assignments.all().delete()
            roster = existing
        else:
            roster = RosterVersion.objects.create(
                team=self.team,
                name=name,
                start_date=self.start_date,
                end_date=self.end_date,
                status='draft',
                created_by=self.user
            )

        employees = list(Employee.objects.filter(teams=self.team, is_active=True))
        if not employees:
            raise ValueError(f"No active employees found in team '{self.team.name}'. Add employees to the team first.")

        min_staff = max(1, int(len(employees) * self.rule.min_staffing_percent / 100))

        rotation_map = self._build_rotation_map()
        leaves = self._get_leaves()

        dates = []
        d = self.start_date
        while d <= self.end_date:
            dates.append(d)
            d += datetime.timedelta(days=1)

        assignments = []
        warnings = []
        for date in dates:
            week_of_year = date.isocalendar()[1]
            week_in_rotation = ((week_of_year - 1) % self.rule.default_rotation_weeks) + 1
            shifts_today = rotation_map.get(week_in_rotation, [])

            if not shifts_today:
                shifts_today = list(ShiftType.objects.filter(is_active=True))

            if not shifts_today:
                continue

            available = [emp for emp in employees if not self._is_on_leave(emp, date, leaves)]

            if not available:
                continue

            num_shifts = len(shifts_today)

            if len(available) < min_staff * num_shifts:
                warnings.append(f"{date}: Not enough staff to meet minimum for all shifts")

            for i, emp in enumerate(available):
                shift = shifts_today[i % num_shifts]
                assignments.append(DutyAssignment(
                    roster_version=roster,
                    employee=emp,
                    shift=shift,
                    date=date
                ))

        DutyAssignment.objects.bulk_create(assignments)

        AuditLog.objects.create(
            roster_version=roster,
            user=self.user,
            action='create',
            description=f"Auto-generated roster for {self.team.name} ({self.start_date} to {self.end_date})"
        )

        return roster

    def _build_rotation_map(self):
        patterns = RotationPattern.objects.filter(rule=self.rule).select_related('shift')
        rotation = defaultdict(list)
        for p in patterns:
            rotation[p.week_number].append(p.shift)
        return rotation

    def _get_leaves(self):
        leaves = LeaveRequest.objects.filter(
            employee__teams=self.team,
            status='approved',
            start_date__lte=self.end_date,
            end_date__gte=self.start_date
        ).select_related('employee')
        leaf_map = defaultdict(list)
        for leave in leaves:
            d = max(leave.start_date, self.start_date)
            end = min(leave.end_date, self.end_date)
            while d <= end:
                leaf_map[d].append(leave.employee.id)
                d += datetime.timedelta(days=1)
        return leaf_map

    def _is_on_leave(self, employee, date, leaves_map):
        return employee.id in leaves_map.get(date, [])
