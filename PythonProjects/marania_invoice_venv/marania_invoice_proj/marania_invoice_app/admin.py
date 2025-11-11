from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(ProductPrice)
admin.site.register(Configuration)
admin.site.register(CustomerPriceMap)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(Transportation)



