from django.urls import path
from . import views

app_name = 'reporting'

urlpatterns = [
    path('monthly/<int:year>/<int:month>/', views.monthly_report, name='monthly_report'),
    path('monthly/', views.monthly_report, name='monthly_report_default'),
    path('team/<int:team_id>/<int:year>/<int:month>/', views.team_report, name='team_report'),
    path('team/<int:team_id>/', views.team_report, name='team_report_default'),
]
