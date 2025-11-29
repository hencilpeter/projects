from django.db import models
from datetime import date

def current_indian_financial_year():
    today = date.today()
    year = today.year
    if today.month >= 4:  # April or later
        start_year = year
        end_year = year + 1
    else:  # January to March
        start_year = year - 1
        end_year = year
    return f"{start_year}-{end_year}"  # e.g., "2025-2026"

# Create your models here.
class Customer(models.Model):
    code = models.CharField(max_length=50, unique=True, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    gst = models.CharField(max_length=15, null=True, blank=True)
    phone = models.CharField(max_length=25, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    address_bill_to = models.TextField(null=True, blank=True)
    address_ship_to = models.TextField(null=True, blank=True)
    is_within_state = models.BooleanField(default=True)
    price_list_tag = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    


    
# class ProductPrice(models.Model):
#     code = models.CharField(max_length=50, unique=True, null=False, blank=False)
#     category = models.CharField(max_length=100, null=False, blank=False)
#     meshsize_start = models.IntegerField(null=True, blank=True)
#     meshsize_end = models.IntegerField(null=True, blank=True)
#     price_per_kilogram = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
#     remark = models.TextField(null=True, blank=True)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.code} - {self.category}"

class Configuration(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    value = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}: {self.value}"
    

class CustomerPriceMap(models.Model):
    #customer_id = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='id')
    #product_id = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='id')
    #price_id = models.ForeignKey('ProductPrice', on_delete=models.CASCADE, related_name='id')
    remark = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer.name} - {self.product.code}: {self.price}"
    

class Invoice(models.Model):
    invoice_date = models.DateField(null=True, blank=True, default=date.today)
    invoice_number = models.CharField(max_length=50, unique=True, null=True)
    
    customer_code = models.CharField(max_length=50, unique=False, null=True)
    customer_name = models.CharField(max_length=100, null=True)
    customer_gst = models.CharField(max_length=20, null=True, blank=True)
    customer_address = models.TextField(null=True, blank=True)
    customer_contact = models.CharField(max_length=30, null=True, blank=True)
    customer_email = models.EmailField(null=True, blank=True)

    ship_to_customer_code = models.CharField(max_length=50, unique=False, null=True)
    ship_to_customer_name = models.CharField(max_length=100, null=True)
    ship_to_customer_gst = models.CharField(max_length=20, null=True, blank=True)
    ship_to_customer_address = models.TextField(null=True, blank=True)
    ship_to_customer_contact = models.CharField(max_length=30, null=True, blank=True)
    ship_to_customer_email = models.EmailField(null=True, blank=True)

    dispatched_through = models.CharField(max_length=100, null=True, blank=True)
    

    def __str__(self):
        return f"{self.invoice_number}-{self.invoice_date}-{self.customer_name}"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        related_name='items',      # allows invoice.items.all()
        on_delete=models.CASCADE,  # deletes items if invoice is deleted
        to_field='invoice_number'  # optional: link by invoice_number instead of id
    )
    item_spec = models.CharField(max_length=200, blank=True, null=True)
    item_code = models.CharField(max_length=50, blank=True, null=True)
    item_description = models.CharField(max_length=200, blank=True, null=True)
    item_mesh_size = models.CharField(max_length=20, blank=True, null=True)
    item_mesh_depth = models.CharField(max_length=20, blank=True, null=True)
    item_quantity = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    item_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.invoice.invoice_number or ''}({self.invoice.invoice_date})-{self.invoice.customer_name or ''} -{self.item_description or ''} - {self.item_quantity or ''}"

class Transportation(models.Model):
    customer = models.ForeignKey(
        Customer,
        related_name='items',      # allows customer.items.all()
        on_delete=models.CASCADE,  # deletes items if customer is deleted
        to_field='code'  # optional: link by customer_code instead of id
        )
    delivery_place  = models.CharField(max_length=50, blank=True, null=True)
    transporter_name = models.CharField(max_length=100, null=True, blank=True)
    transporter_gst = models.CharField(max_length=30, null=True, blank=True)
    vehicle_name_number = models.CharField(max_length=100, blank=True, null=True)
    is_default_transport = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer.name} - {self.delivery_place}-{self.transporter_name}-{self.is_default_transport}"



class Product(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    display_name = models.CharField(max_length=200, blank=True, null=True)
    hsn = models.CharField(max_length=20, blank=True, null=True)

    cgst = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sgst = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    igst = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class PriceList(models.Model):
    product = models.ForeignKey(
        Product,
        related_name='items',      # allows product.items.all()
        on_delete=models.CASCADE,  # deletes items if product is deleted
        to_field='code'  # optional: link by product_code instead of id
        )
    code = models.CharField(max_length=50)
    customer_group = models.CharField(max_length=100)
    sequence_id = models.PositiveIntegerField()
    twine_code = models.CharField(max_length=50)
    mesh_size_start = models.CharField(max_length=5) # models.DecimalField(max_digits=10, decimal_places=2)
    mesh_size_end =   models.CharField(max_length=5) # models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Price List"
        verbose_name_plural = "Price Lists"
        ordering = ["sequence_id"]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.customer_group} - {self.sequence_id}"
    

class CompanySettings(models.Model):
    # Ensure only one row exists
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)

    # Invoice running number
    current_invoice_number = models.PositiveIntegerField(default=1)
    invoice_prefix = models.CharField(max_length=20, default="INV")

    # GST values
    igst = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cgst = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sgst = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    finance_year = models.CharField(max_length=20, default=current_indian_financial_year())

    # Company information
    company_title = models.CharField(max_length=255)
    company_address = models.TextField()

    # Optional: contact info
    company_phone = models.CharField(max_length=50, blank=True, null=True)
    company_email = models.EmailField(blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Company Settings"

    class Meta:
        verbose_name = "Company Setting"
        verbose_name_plural = "Company Settings"
    
