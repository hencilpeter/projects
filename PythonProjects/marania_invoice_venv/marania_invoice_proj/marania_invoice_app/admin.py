from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Parties)
admin.site.register(Product)
#admin.site.register(ProductPrice)
admin.site.register(Configuration)
admin.site.register(CustomerPriceMap)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(Transportation)
admin.site.register(PriceCatalog)
admin.site.register(CompanySettings)
admin.site.register(CustomerPriceCatalog)


