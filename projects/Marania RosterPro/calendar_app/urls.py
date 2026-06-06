from django.urls import path
from . import views

app_name = 'calendar_app'

urlpatterns = [
    path('team/<int:team_id>/<int:year>/<int:month>/', views.team_calendar, name='team_calendar'),
    path('team/<int:team_id>/', views.team_calendar, name='team_calendar_default'),
    path('team/', views.team_calendar, name='team_calendar_select'),
    path('employee/<int:emp_id>/<int:year>/<int:month>/', views.employee_calendar, name='employee_calendar'),
    path('employee/<int:emp_id>/', views.employee_calendar, name='employee_calendar_default'),
    path('employee/', views.employee_calendar, name='my_calendar'),
]
