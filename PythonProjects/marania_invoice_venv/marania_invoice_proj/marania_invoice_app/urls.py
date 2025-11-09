
from django.urls import path
from . import views

urlpatterns = [
path('customer',views.customer, name='customer'),
path('invoice_entry', views.invoice_entry, name='invoice_entry'),

path('customer/add/', views.create_customer, name='create_customer'),
# path('login',views.login, name='login'),
# path('logout',views.logout, name='logout'),
# path('dashboard',views.dashboard, name='dashboard'),
# path('invoices',views.invoices, name='invoices'),
# path('products',views.products, name='products'),
# path('clients',views.clients, name='clients'),
]

