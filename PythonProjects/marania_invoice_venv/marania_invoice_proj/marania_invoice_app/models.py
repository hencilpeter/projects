from django.db import models
from datetime import date
from decimal import Decimal

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
                            null=True,
                            blank=True
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
            print(self.price_code)
            price_catalog_object = PriceCatalog.objects.filter(code=self.price_code).first()
            #return f"{self.customer} - {self.price_catalog}"
            return f"{self.customer} - {price_catalog_object.code}-{price_catalog_object.customer_group}"
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
    destination = models.CharField(max_length=200, null=True, blank=True)
    vehicle_name_number = models.CharField(max_length=100, null=True, blank=True)
    transporter_gst = models.CharField(max_length=100, null=True, blank=True)
    
    quantity_total  = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=Decimal('0.00'))
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    cgst_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    sgst_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    igst_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    round_off = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    gross_total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    remark = models.CharField(max_length=1024, null=True, blank=True,default="")

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
class Order(models.Model):
    QUANTITY_UNIT_CHOICES = [
        ('KG', 'KG'),
        ('Bag', 'Bag'),
    ]

    STATUS_CHOICES = [
        ('Ordered', 'Ordered'),
        ('ProductionQueue', 'P Queue'),
        ('InProduction', 'In Prod'),
        ('ProductionCompleted', 'P Completed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('OnHold', 'On Hold'),
        ('Rejected', 'Rejected'),
    ]

    order_key = models.AutoField(primary_key=True)
    order_sequence = models.IntegerField(default=0)
    order_number = models.CharField(max_length=100)
    order_date = models.DateField()
    twine = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_unit = models.CharField(max_length=10, choices=QUANTITY_UNIT_CHOICES, default='Bag')
    customer = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_gst_included = models.BooleanField(default=False)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Ordered')
    last_status_date = models.DateField(blank=True, null=True)
    order_instructions = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order_number} - {self.customer} - {self.order_date}"

    class Meta:
        ordering = ['-order_date', '-order_sequence']


class OrderSpecification(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='specifications', null=True, blank=True)
    mesh_size = models.IntegerField(blank=True, null=True)
    mesh_depth = models.CharField(max_length=50, blank=True, null=True)
    salvage = models.CharField(max_length=255, blank=True, null=True)
    piece_weight = models.CharField(max_length=50, blank=True, null=True)
    colour = models.CharField(max_length=50, default='White')
    no_of_pcs = models.IntegerField(blank=True, null=True)

    def __str__(self):
        if self.order_id:
            return f"Spec for {self.order.order_number}"
        return f"Spec #{self.pk}"


class ExcelSheet(models.Model):
    name = models.CharField(max_length=100)
    data = models.JSONField(default=list)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Sales(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PAID', 'PAID'),
        ('PARTIALLY_PAID', 'PARTIALLY PAID'),
        ('PENDING', 'PENDING'),
        ('NO_PAYMENT', 'NO PAYMENT'),
        ('ON_HOLD_STOCK', 'ON HOLD(Item On Stock)'),
        ('ON_HOLD_PROCESSING', 'ON HOLD(PROCESSING)'),
    ]

    sales_key = models.AutoField(primary_key=True)
    sales_sequence = models.IntegerField(default=0)
    order_no = models.CharField(max_length=100)
    sales_entry_date = models.DateField(default=date.today)
    customer = models.CharField(max_length=255)
    twine = models.CharField(max_length=255, blank=True, null=True)
    speification = models.CharField(max_length=255, blank=True, null=True)
    colour = models.CharField(max_length=50, default='White')
    piece_weight = models.CharField(max_length=50, blank=True, null=True)
    piece_count = models.IntegerField(blank=True, null=True)
    initial_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    processed_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    delivery_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=30, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    payment_date = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order_no} - {self.customer} - {self.sales_entry_date}"

    class Meta:
        ordering = ['-sales_entry_date', '-sales_sequence']


class PaymentReceipt(models.Model):
    PAYMENT_MODE_CHOICES = [
        ('Cash', 'Cash'), ('Bank', 'Bank'),
        ('Cheque', 'Cheque'), ('UPI', 'UPI'),
    ]
    ALLOCATION_STATUS_CHOICES = [
        ('Unallocated', 'Unallocated'),
        ('Partially Allocated', 'Partially Allocated'),
        ('Fully Allocated', 'Fully Allocated'),
    ]
    payment_id = models.AutoField(primary_key=True)
    receipt_no = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(
        Parties, to_field='code', on_delete=models.DO_NOTHING,
        related_name='payment_receipts', db_constraint=False)
    payment_date = models.DateField()
    total_received = models.DecimalField(max_digits=18, decimal_places=2)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES)
    reference_no = models.CharField(max_length=100, blank=True, null=True)
    allocation_status = models.CharField(
        max_length=20, choices=ALLOCATION_STATUS_CHOICES, default='Unallocated')
    remarks = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.receipt_no} - {self.customer} - {self.payment_date}"

    class Meta:
        ordering = ['-payment_date']


class PaymentAllocation(models.Model):
    allocation_id = models.AutoField(primary_key=True)
    payment = models.ForeignKey(
        PaymentReceipt, on_delete=models.CASCADE,
        related_name='allocations', db_constraint=False)
    invoice = models.ForeignKey(
        Invoice, on_delete=models.DO_NOTHING,
        related_name='payment_allocations', db_constraint=False,
        to_field='invoice_number')
    allocated_amount = models.DecimalField(max_digits=18, decimal_places=2)
    allocation_date = models.DateField()
    remarks = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Alloc {self.allocation_id} - {self.payment.receipt_no} - {self.invoice.invoice_number}"

    class Meta:
        ordering = ['-allocation_date']


class OpeningBalance(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'), ('Posted', 'Posted'), ('Cancelled', 'Cancelled'),
    ]
    opening_balance_id = models.AutoField(primary_key=True)
    opening_date = models.DateField()
    account_id = models.CharField(max_length=100, blank=True, null=True)
    customer = models.ForeignKey(
        Parties, to_field='code', on_delete=models.DO_NOTHING,
        related_name='opening_balances', db_constraint=False,
        null=True, blank=True)
    debit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    reference_no = models.CharField(max_length=100, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"OB {self.opening_balance_id} - {self.opening_date}"

    class Meta:
        ordering = ['-opening_date']

