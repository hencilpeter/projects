
from django.urls import path
from . import views

urlpatterns = [
path('customer',views.customer, name='customer'),
#path('customer',views.create_customer, name='customer'),
path('invoice_entry', views.invoice_entry, name='invoice_entry'),

path('customer/add/', views.create_customer, name='create_customer'),
path('customer/load/<int:id>/', views.load_customer, name='load_customer'),

path('invoice_entry/save', views.invoice_save, name='invoice_save'),
path('invoice_entry/view/<str:invoice_number>', views.invoice_view, name='invoice_view'),
path('invoice_entry/pdf/<str:invoice_number>/', views.invoice_pdf, name='invoice_pdf'),
path('invoice_entry/show_gst_calculator', views.show_gst_calculator, name='show_gst_calculator'),

path('settings/company/', views.company_settings_view, name='company_settings'),
path('invoice_entry/get_invoice/<str:invoice_number>/', views.get_invoice, name='get_invoice'),

# price  catalog 
 path("price-list/add/", views.add_price_list, name="add_price_list"),
 path("price-list/load/<str:price_code>", views.load_price_list, name="load_price_list"),
 path("price-list/save", views.save_price_list, name="save_price_list"),

# customer price catalog 
# path('customer-price-catalog/', views.customer_price_catalog, name='customer_price_catalog'),
# path('customer-price-catalog/save/', views.customer_price_catalog_save, name='customer_price_catalog_save'),
# path('customer-price-catalog/load/<str:price_code>/', views.customer_price_catalog_load, name='customer_price_catalog_load'),
# path('customer-price-catalog/delete/<str:price_code>/', views.customer_price_catalog_delete, name='customer_price_catalog_delete'),

# customer price catalog
path('customer-price-catalog/', views.customer_price_catalog, name='customer_price_catalog'),
path('customer-price-catalog/load/<int:id>/', views.load_customer_price_catalog, name='load_customer_price_catalog'),

# products
path("products/", views.product_master, name="product_master"),
path("products/load/<int:id>/", views.load_product, name="load_product"),


#path("settings/company", views.company_settings_view, name="company_settings"),


# path('login',views.login, name='login'),
# path('logout',views.logout, name='logout'),
# path('dashboard',views.dashboard, name='dashboard'),
# path('invoices',views.invoices, name='invoices'),
# path('products',views.products, name='products'),
# path('clients',views.clients, name='clients'),
]

