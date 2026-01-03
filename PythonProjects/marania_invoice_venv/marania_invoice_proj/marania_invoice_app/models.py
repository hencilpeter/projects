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
    #return f"{start_year}-{end_year}"  # e.g., "2025-2026"
    return f"{str(start_year)[-2:]}-{str(end_year)[-2:]}"


# Create your models here.
  
class PartyRole(models.Model):
    role = models.CharField(max_length=255)

    def __str__(self):
        return self.role


class Parties(models.Model):
    code = models.CharField(max_length=50, unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    gst = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address_bill_to = models.TextField(blank=True, null=True)
    address_ship_to = models.TextField(blank=True, null=True)
    is_within_state = models.BooleanField(default=True)
    roles = models.ManyToManyField('PartyRole', blank=True, db_constraint=False)
    
    created_at = models.DateTimeField(auto_now_add=True)   # automatically set on creation
    updated_at = models.DateTimeField(auto_now=True)       # automatically set on update

    def __str__(self):
        return f"{self.code}-{self.name}"


class Transportation(models.Model):
    customer = models.ForeignKey(
        Parties,
        to_field='code',           # link to Parties.code
        related_name='transportations',
        on_delete=models.DO_NOTHING,
        db_constraint=True,        # keep constraint
        null=True,                 # optional
        blank=True,)
    delivery_place  = models.CharField(max_length=50, blank=True, null=True)
    transporter_name = models.CharField(max_length=100, null=True, blank=True)
    transporter_gst = models.CharField(max_length=30, null=True, blank=True)
    vehicle_name_number = models.CharField(max_length=100, blank=True, null=True)
    is_default_transport = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer.name} - {self.delivery_place}-{self.transporter_name}-{self.is_default_transport}"

class Materials(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    displayname = models.CharField(max_length=255, blank=True, null=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    gst = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="GST percentage (e.g. 9.00)"
    )

    supplier = models.ForeignKey(
                            Parties,
                            to_field='code',
                            on_delete=models.DO_NOTHING,
                            related_name='materials',
                            db_constraint=False,   # ⭐ KEY LINE
                        )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code}-{self.name}"
        

class Product(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    display_name = models.CharField(max_length=200, blank=True, null=True)
    hsn = models.CharField(max_length=20, blank=True, null=True)

    # ✅ Reference Material here
    material = models.ForeignKey(
        Materials,
        to_field='code',
        on_delete=models.DO_NOTHING,
        related_name='products',
        db_constraint=False,   # ⭐ KEY LINE
        null=True, 
        blank=True, 
    )

    cgst = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sgst = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    igst = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code}-{self.name}"
    

class PriceCatalog(models.Model):
    product = models.ForeignKey(
        Product,
        to_field="code",
        on_delete=models.DO_NOTHING,
        related_name='pricecatalogs',
        db_constraint=False,   # ⭐ KEY LINE
        null=True, 
        blank=True, 
    )

    sequence_id = models.PositiveIntegerField()
    code = models.CharField(max_length=50)
    customer_group = models.CharField(max_length=100)
    
    mesh_size_start = models.CharField(max_length=5)
    mesh_size_end = models.CharField(max_length=5)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    is_active = models.BooleanField(default=True)
    note = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code}-{self.customer_group}"
    
    
class CustomerPriceCatalog(models.Model):
    customer = models.ForeignKey(
         Parties,
         to_field='code',
         on_delete=models.DO_NOTHING,
         related_name='customer_items',
         db_constraint=False,
     )

    price_catalog =  models.ForeignKey(
         PriceCatalog,
         #to_field="id",
         on_delete=models.DO_NOTHING,
         related_name='price_catalog_items',
         db_constraint=False,
     )
    price_code  = models.TextField(blank=True, null=True)

    gst_included = models.BooleanField(default=False)
    colour_extra_price = models.FloatField(default=0)
    small_mesh_size_extra_price = models.FloatField(default=0)
    remark = models.TextField(blank=True, null=True)

    def __str__(self):
        # return f"{self.customer}-{self.price_catalog}"
        try:
            return f"{self.customer} - {self.price_catalog}"
        except Exception:
            return f"CustomerPriceCatalog(id={self.id})"

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

    finance_year = models.CharField(max_length=20, default=current_indian_financial_year)

    # Company information
    company_title = models.CharField(max_length=255)
    company_address = models.TextField()
    company_gst = models.CharField(max_length=50, blank=True, null=True)
    company_state = models.CharField(max_length=50, blank=True, null=True)
    company_state_code = models.CharField(max_length=50, blank=True, null=True)


    # Optional: contact info
    company_phone = models.CharField(max_length=50, blank=True, null=True)
    company_email = models.EmailField(blank=True, null=True)

    # bank account
    bank_account_name  = models.CharField(max_length=50, blank=True, null=True)
    bank_name  = models.CharField(max_length=25, blank=True, null=True)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_branch = models.CharField(max_length=50, blank=True, null=True)
    bank_ifsc  = models.CharField(max_length=50, blank=True, null=True)

    small_mesh_size_charge = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    colour_charge = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Company Settings"

    class Meta:
        verbose_name = "Company Setting"
        verbose_name_plural = "Company Settings"
    

###################################################
 # TODO - List 
 # 1.    CustomerPriceCatalog - price_catalog may need to be removed. 
    

class Configuration(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    value = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}: {self.value}"
    
    

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
    vehicle_name_number = models.CharField(max_length=100, null=True, blank=True)
    transporter_gst = models.CharField(max_length=100, null=True, blank=True)
    

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
    item_colour = models.CharField(max_length=100, blank=True, null=True)
    item_hsn_code = models.CharField(max_length=10, blank=True, null=True)

    #derived values
    item_gst_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    item_total_with_gst = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    def __str__(self):
        return f"{self.invoice.invoice_number or ''}({self.invoice.invoice_date})-{self.invoice.customer_name or ''} -{self.item_description or ''} - {self.item_quantity or ''}"






    


    

