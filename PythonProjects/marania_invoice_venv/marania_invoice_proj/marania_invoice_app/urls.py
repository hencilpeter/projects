
from django.urls import path
from . import views

urlpatterns = [
# parties     
path('parties',views.parties, name='parties'),
path('parties/add/', views.create_party, name='create_party'),
path('parties/load/<int:id>/', views.load_party, name='load_party'),

# invoice 
path('invoice_entry', views.invoice_entry, name='invoice_entry'),
path('invoice_entry/save', views.invoice_save, name='invoice_save'),
path('invoice_entry/view/<str:invoice_number>', views.invoice_view, name='invoice_view'),
path('invoice_entry/pdf/<str:invoice_number>/', views.invoice_pdf, name='invoice_pdf'),
path('invoice_entry/show_gst_calculator', views.show_gst_calculator, name='show_gst_calculator'),
path('invoice_entry/get_invoice/<str:invoice_number>/', views.get_invoice, name='get_invoice'),

# company settings 
path('settings/company/', views.company_settings_view, name='company_settings'),

# price  catalog 
 path("price-list/add/", views.add_price_list, name="add_price_list"),
 path("price-list/load/<str:price_code>", views.load_price_list, name="load_price_list"),
 path("price-list/save", views.save_price_list, name="save_price_list"),

# customer price catalog
path('customer-price-catalog/', views.customer_price_catalog, name='customer_price_catalog'),
path('customer-price-catalog/load/<int:id>/', views.load_customer_price_catalog, name='load_customer_price_catalog'),

# products
path("products/", views.product_master, name="product_master"),
path("products/load/<int:id>/", views.load_product, name="load_product"),

# materials 
path("materials/", views.materials_view, name="materials"),
path("materials/load/<int:pk>/", views.load_material, name="load_material"),

# view customer price dictionary
path("customer-price-dictionary/", views.customer_price_dictionary_view,  name="customer_price_dictionary"  ),
path("customer-price-dictionary_invoice/", views.customer_price_dictionary_view_invoice,  name="customer_price_dictionary_invoice"),


# path('login',views.login, name='login'),
# path('logout',views.logout, name='logout'),
# path('dashboard',views.dashboard, name='dashboard'),
# path('invoices',views.invoices, name='invoices'),
# path('products',views.products, name='products'),
# path('clients',views.clients, name='clients'),
]

