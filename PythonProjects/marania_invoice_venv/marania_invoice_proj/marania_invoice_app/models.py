from django.db import models
from datetime import date

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
    default_delivery_transport = models.CharField(max_length=100, null=True, blank=True)
    default_delivery_location = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    

class Product(models.Model):
    code = models.CharField(max_length=50, unique=True, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    display_name = models.CharField(max_length=255, null=True, blank=True)
    hsn = models.CharField(max_length=10, null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.display_name or self.name} ({self.code})"

    
class ProductPrice(models.Model):
    code = models.CharField(max_length=50, unique=True, null=False, blank=False)
    category = models.CharField(max_length=100, null=False, blank=False)
    meshsize_start = models.IntegerField(null=True, blank=True)
    meshsize_end = models.IntegerField(null=True, blank=True)
    price_per_kilogram = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    remark = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.category}"

class Configuration(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    value = models.CharField(max_length=255, null=True, blank=True)
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

    customer_address_bill_to = models.TextField(null=True, blank=True)
    customer_address_ship_to = models.TextField(null=True, blank=True)

    customer_contact = models.CharField(max_length=20, null=True, blank=True)
    customer_email = models.EmailField(null=True, blank=True)

    dispatched_through = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.invoice_number} - {self.customer_name}"

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
        return f"{self.invoice.invoice_number or ''} - {self.invoice.customer_name or ''} -{self.item_description or ''} - {self.item_quantity or ''}"
