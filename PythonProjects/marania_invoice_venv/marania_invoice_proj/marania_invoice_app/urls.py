
from django.urls import path
from . import views

urlpatterns = [
path('customer',views.customer, name='customer'),
path('invoice_entry', views.invoice_entry, name='invoice_entry'),

path('customer/add/', views.create_customer, name='create_customer'),
path('invoice_entry/save', views.invoice_save, name='invoice_save'),
path('invoice_entry/view/<str:invoice_number>', views.invoice_view, name='invoice_view'),
path('invoice_entry/pdf/<str:invoice_number>/', views.invoice_pdf, name='invoice_pdf'),
path('invoice_entry/show_gst_calculator', views.show_gst_calculator, name='show_gst_calculator'),

path('settings/company/', views.company_settings_view, name='company_settings'),
#path("settings/company", views.company_settings_view, name="company_settings"),


# path('login',views.login, name='login'),
# path('logout',views.logout, name='logout'),
# path('dashboard',views.dashboard, name='dashboard'),
# path('invoices',views.invoices, name='invoices'),
# path('products',views.products, name='products'),
# path('clients',views.clients, name='clients'),
]

