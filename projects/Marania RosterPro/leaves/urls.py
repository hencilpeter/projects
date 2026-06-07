from django.urls import path
from . import views

app_name = 'leaves'

urlpatterns = [
    path('', views.leave_list, name='leave_list'),
    path('apply/', views.leave_create, name='leave_create'),
    path('batch/', views.leave_batch_create, name='leave_batch'),
    path('<int:pk>/approve/', views.leave_approve, name='leave_approve'),
    path('<int:pk>/reject/', views.leave_reject, name='leave_reject'),
    path('<int:pk>/delete/', views.leave_delete, name='leave_delete'),
    path('bulk-delete/', views.leave_bulk_delete, name='leave_bulk_delete'),
    path('config/', views.leave_config, name='leave_config'),
]
