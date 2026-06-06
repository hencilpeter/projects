from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('employees/', include('employees.urls')),
    path('shifts/', include('shifts.urls')),
    path('leaves/', include('leaves.urls')),
    path('roster/', include('roster.urls')),
    path('calendar/', include('calendar_app.urls')),
    path('reports/', include('reporting.urls')),
    path('dashboard/', lambda r: redirect('roster:roster_list'), name='dashboard'),
    path('', lambda r: redirect('dashboard')),
]
