from django.db import models

class ShiftType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_overnight = models.BooleanField(default=False, help_text="Check if shift ends next day")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.name} ({self.start_time:%H:%M} - {self.end_time:%H:%M})"

    @property
    def duration_hours(self):
        start = self.start_time.hour + self.start_time.minute / 60
        end = self.end_time.hour + self.end_time.minute / 60
        if self.is_overnight:
            end += 24
        return round(end - start, 1)

    @property
    def time_range(self):
        return f"{self.start_time:%H:%M} – {self.end_time:%H:%M}"
