from django.urls import path
from . import views

app_name = 'roster'

urlpatterns = [
    path('', views.roster_list, name='roster_list'),
    path('combined/<int:year>/<int:month>/', views.combined_roster, name='combined_roster'),
    path('combined/', views.combined_roster, name='combined_roster_default'),
    path('combined/print/<int:year>/<int:month>/', views.combined_roster_print, name='combined_roster_print'),
    path('combined/print/', views.combined_roster_print, name='combined_roster_print_default'),
    path('generate/', views.roster_generate, name='roster_generate'),
    path('<int:pk>/', views.roster_detail, name='roster_detail'),
    path('<int:pk>/calendar/<int:year>/<int:month>/', views.roster_calendar, name='roster_calendar'),
    path('<int:pk>/calendar/', views.roster_calendar, name='roster_calendar_default'),
    path('<int:pk>/publish/', views.roster_publish, name='roster_publish'),
    path('<int:pk>/delete/', views.roster_delete, name='roster_delete'),
    path('<int:pk>/swap/', views.swap_shifts, name='swap_shifts'),
    path('assignment/<int:pk>/override/', views.assignment_override, name='assignment_override'),
    path('rules/', views.schedule_rules, name='schedule_rules'),
    path('rules/create/', views.schedule_rule_create, name='schedule_rule_create'),
    path('rules/<int:pk>/update/', views.schedule_rule_update, name='schedule_rule_update'),
    path('rules/<int:rule_pk>/patterns/', views.rotation_patterns, name='rotation_patterns'),
    path('rules/<int:rule_pk>/patterns/add/', views.rotation_pattern_add, name='rotation_pattern_add'),
    path('patterns/<int:pk>/delete/', views.rotation_pattern_delete, name='rotation_pattern_delete'),
]
