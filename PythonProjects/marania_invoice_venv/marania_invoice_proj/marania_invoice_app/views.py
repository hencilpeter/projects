# =======================
# Django core
# =======================
from django.shortcuts import render, redirect, reverse 
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import get_template 
from django.template import TemplateDoesNotExist
from django.conf import settings
from django.apps import apps
from django.db import transaction, models, IntegrityError

# =======================
# Django ORM utilities
# =======================
from django.db.models import (
    Count,
    Max,
    Sum,
    Q,
    BooleanField,
    ForeignKey,
)

from django.db.models.functions import TruncMonth # , Lower, Trim

# =======================
# Third-party libraries
# =======================
from weasyprint import HTML, CSS

# =======================
# App config & services
# =======================
from .config import REPORT_CONFIG
from .services import (
    get_report_queryset,
    serialize_report_data,
    export_data,
)

# =======================
# Forms
# =======================
from . import forms
from .forms import (
    CustomerForm,
    InvoiceForm,
    CompanySettingsForm,
    CustomerPriceCatalogForm,
    PriceListFormSet,
)

# =======================
# Models
# =======================
from .models import (
    Parties,
    PartyRole,
    Configuration,
    Invoice,
    InvoiceItem,
    Transportation,
    PriceCatalog,
    CompanySettings,
    Product,
    CustomerPriceCatalog,
    Materials,
    Order,
    OrderSpecification,
    Sales,
    PaymentReceipt,
    PaymentAllocation,
    OpeningBalance,
    Expense,
    Purchase,
    ProfitLoss,
    TwineInventory,
    MaterialConversionRatio,
    ProcessingCost,
    MachineOperationalCost,
    AdditionalCost,
    SettlementInvoice,
    PriceListConfiguration,

)

# =======================
# Serializers
# =======================
from .serializers import MODEL_REGISTRY, UNIQUE_KEY_MODEL

# =======================
# Utilities
# =======================
from collections import defaultdict, OrderedDict
from decimal import Decimal, ROUND_DOWN,ROUND_HALF_UP
from datetime import datetime
from zipfile import ZipFile
import csv
import json
import io
import os

# Excel sheets
from .models import ExcelSheet
from django.views.decorators.csrf import csrf_exempt

AUTO_FIELDS = {"id", "created_at", "updated_at"}


# Global cache
_CUSTOMER_PRICE_DICT = None

_PRODUCT_DICT = None


# @singleton
class Configurations:
    
    def __init__(self):
        configurations = Configuration.objects.all() 
        self.config = defaultdict()
        self.config['CompanyName'] = 'Marania Filaments'#configurations['CompanyName']
        #self.config['CGST'] = configurations['CGST']
        #self.config['SGST'] = configurations['SGST']
        #self.config['IGST'] = configurations['IGST']

company_settings, created = CompanySettings.objects.get_or_create(id=1)

#######################################################-Common Functions-#############
def round_half_up(value, decimals=0):
    value = Decimal(str(value))
    rounding_format = '1.' + '0' * decimals
    return value.quantize(Decimal(rounding_format), rounding=ROUND_HALF_UP)

def get_next_invoice_number():
    try:
        # Get the single CompanySettings row
        settings = CompanySettings.objects.get(id=1)
        # Format: PREFIX + current invoice number
        next_invoice = f"{settings.current_invoice_number+1}"
        return next_invoice
    except CompanySettings.DoesNotExist:
        # Handle case if row is missing
        return None

def get_invoices_dict():
    invoice_items = InvoiceItem.objects.select_related('invoice').all()
    invoices = Invoice.objects.all()
    
    invoice_dict = defaultdict(lambda:{})
    invice_item_dict = defaultdict(lambda:{})
    for invoice_item in invoice_items:
        if invoice_item.invoice.invoice_number not in invice_item_dict:
            invice_item_dict[invoice_item.invoice.invoice_number] = [invoice_item]
        else:
            invice_item_dict[invoice_item.invoice.invoice_number].append(invoice_item)

    for invoice in invoices:
        invoice_dict[invoice.invoice_number]={
                    "invoice_date": invoice.invoice_date,
                    #bill to 
                    "customer_code":invoice.customer_code,"customer_name":invoice.customer_name,
                    "customer_gst":invoice.customer_gst,"customer_address":invoice.customer_address,                    
                    "customer_contact":invoice.customer_contact,"customer_email":invoice.customer_email, 
                    #ship to
                    "ship_to_customer_code":invoice.ship_to_customer_code, "ship_to_customer_name":invoice.ship_to_customer_name,
                    "ship_to_customer_gst":invoice.ship_to_customer_gst, "ship_to_customer_address":invoice.ship_to_customer_address,
                    "ship_to_customer_contact":invoice.ship_to_customer_contact,"ship_to_customer_email":invoice.ship_to_customer_email,

                    "dispatched_through":invoice.dispatched_through,
                    "destination":invoice.destination,
                    "vehicle_no": "" if invoice.vehicle_name_number == "" or invoice.vehicle_name_number == None else  invoice.vehicle_name_number,
                    "invoice_items":invice_item_dict[invoice.invoice_number],
                    "remark":invoice.remark}
    
    return invoice_dict

def get_parties_dict():
    parties_dict = defaultdict(dict)

    parties = Parties.objects.prefetch_related('roles').all()

    for party in parties:
        parties_dict[party.code] = {
            "name": party.name,
            "gst": party.gst,
            "phone": party.phone,
            "email": party.email,
            "address_bill_to": party.address_bill_to,
            "address_ship_to": party.address_ship_to,
            "is_within_state": party.is_within_state,
            "roles": list(party.roles.values_list('role', flat=True)),
            "created_at": party.created_at,
            "updated_at": party.updated_at,
        }
        
    return parties_dict

def get_product_dict():
    global _PRODUCT_DICT

    # ✅ Return cached dictionary if already initialized
    if _PRODUCT_DICT is not None:
        return _PRODUCT_DICT

    # ✅ Build dictionary only once
    products_dict = defaultdict(dict)

    products = Product.objects.select_related('material').all()

    for product in products:
        products_dict[product.code] = {
            "name": product.name,
            "display_name": product.display_name,
            "hsn": product.hsn,

            # Material reference
            "material_code": product.material.code if product.material else None,
            "material_name": product.material.name if product.material else None,

            # Tax rates
            "cgst": str(product.cgst),
            "sgst": str(product.sgst),
            "igst": str(product.igst),

            "description": product.description,
        }

    # ✅ Cache globally
    _PRODUCT_DICT = products_dict

    return _PRODUCT_DICT

def reset_global_dict():
    global _PRODUCT_DICT
    global _CUSTOMER_PRICE_DICT

    _PRODUCT_DICT = None
    _CUSTOMER_PRICE_DICT = None

def get_first_part(value):
    if not value:
        return ""
    return value.split("-", 1)[0]

def print_dict(d, indent=0):
    for key, value in d.items():
        print(" " * indent + str(key) + ":")
        if isinstance(value, dict):
            print_dict(value, indent + 4)
        else:
            print(" " * (indent + 4) + str(value))

def get_product_code_from_price_code(price_code):
    price_catalog = (
        PriceCatalog.objects
        .filter(code=price_code, is_active=True)
        .select_related("product")
        .first()
    )
    if price_catalog and price_catalog.product:
        return price_catalog.product.code

    return ""

def get_price_catalog_object_from_price_code(price_code):
    price_catalog = (
        PriceCatalog.objects
        .filter(code=price_code, is_active=True)
        .select_related("product")
        .first()
    )
   
    return price_catalog



def get_customer_price_dictionary():
    global _CUSTOMER_PRICE_DICT

    # ✅ If already initialized, return cached object
    if _CUSTOMER_PRICE_DICT is not None:
        return _CUSTOMER_PRICE_DICT

    # ✅ Initialize dictionary only once
    customer_price_dict = defaultdict(lambda: -1)

    # [customer_code][product_code][size_range] = price details
    for customer_price_catalog in CustomerPriceCatalog.objects.all():

        customer_code = customer_price_catalog.customer.code

        if customer_price_dict[customer_code] == -1:
            customer_price_dict[customer_code] = defaultdict(lambda: -1)

        price_code = customer_price_catalog.price_code
        product_code = get_product_code_from_price_code(price_code=price_code)
        if price_code == "":
            print("##########price code empty")
            continue
        
        if customer_price_dict[customer_code][product_code] == -1:
            customer_price_dict[customer_code][product_code] = {}
     

        for price_item in PriceCatalog.objects.filter(code=price_code):
            size_range = f"{price_item.mesh_size_start}-{price_item.mesh_size_end}"

            customer_price_dict[customer_code][product_code][size_range] = {
                "price": str(price_item.price),
                "price_code": price_code,
                "sequence_id": price_item.sequence_id,
                "customer_group": price_item.customer_group,
                "customer_name": customer_price_catalog.customer.name,
                "colour_extra_price": customer_price_catalog.colour_extra_price,
                "small_mesh_size_extra_price": customer_price_catalog.small_mesh_size_extra_price,
                "gst_included": customer_price_catalog.gst_included,
            }

    # ✅ Cache it globally
    _CUSTOMER_PRICE_DICT = customer_price_dict

    return _CUSTOMER_PRICE_DICT

# def get_customer_price_dictionary():

#     customer_price_dict = defaultdict(lambda: -1)

#     # [customer_code][product_code][size_range] = price details
#     for customer_price_catalog in CustomerPriceCatalog.objects.all():

#         customer_code = customer_price_catalog.customer.code

#         if customer_price_dict[customer_code] == -1:
#             customer_price_dict[customer_code] = defaultdict(lambda: -1)

#         product_code = customer_price_catalog.price_catalog.product.code

#         if customer_price_dict[customer_code][product_code] == -1:
#             customer_price_dict[customer_code][product_code] = {}

#         price_code = customer_price_catalog.price_catalog.code

#         for price_item in PriceCatalog.objects.filter(code=price_code):
#             size_range = f"{price_item.mesh_size_start}-{price_item.mesh_size_end}"

#             customer_price_dict[customer_code][product_code][size_range] = {
#                 "price": price_item.price,
#                 "price_code": price_code,
#                 "sequence_id": price_item.sequence_id,
#                 "customer_group": price_item.customer_group,
#                 "customer_name":customer_price_catalog.customer.name,
#                 "colour_extra_price": customer_price_catalog.colour_extra_price,
#                 "small_mesh_size_extra_price": customer_price_catalog.small_mesh_size_extra_price,
#                 "gst_included": customer_price_catalog.gst_included,
#             }

#     return customer_price_dict


########################################################-Helper Functions-############
def number_to_words(num):
    """
    Convert a number to words in Indian numbering system with Rupees and Paise.
    """

    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
            "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen",
            "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

    def two_digits(n):
        if n < 20:
            return ones[n]
        else:
            return tens[n // 10] + (" " + ones[n % 10] if n % 10 != 0 else "")
    
    def three_digits(n):
        h = n // 100
        rem = n % 100
        if h and rem:
            return ones[h] + " Hundred " + two_digits(rem)
        elif h:
            return ones[h] + " Hundred"
        elif rem:
            return two_digits(rem)
        else:
            return ""
    
    def convert_to_words(n):
        crore = n // 10000000
        n %= 10000000
        lakh = n // 100000
        n %= 100000
        thousand = n // 1000
        n %= 1000
        hundred = n  # remaining
        
        parts = []
        if crore: parts.append(three_digits(crore) + " Crore")
        if lakh: parts.append(three_digits(lakh) + " Lakh")
        if thousand: parts.append(three_digits(thousand) + " Thousand")
        if hundred: parts.append(three_digits(hundred))
        
        return " ".join(parts)
    
    # Split rupees and paise
    rupees = int(num)
    paise = int(round((num - rupees) * 100))

    words = ""
    if rupees:
        words += "Rupees " + convert_to_words(rupees)
    if paise:
        if words:
            words += " and "
        words += convert_to_words(paise) + " Paise"
    if not words:
        words = "Rupees Zero"
    words += " Only"
    
    return words

# Test examples
# print(number_to_words(12345678.90))
# print(number_to_words(5000))
# print(number_to_words(0.75))
# print(number_to_words(0))



def invoice_summary():
    invoice_items = InvoiceItem.objects.select_related('invoice').all()
    # invoice_items = (
    #                     InvoiceItem.objects.select_related('invoice')
    #                                        .order_by('-invoice__invoice_date', '-invoice__invoice_number')
    #         )

    invoice_summary = {}

    for invoice_item in invoice_items:
        invoice_number = invoice_item.invoice.invoice_number
        item_subtotal = Decimal(invoice_item.item_quantity * invoice_item.item_price).quantize(Decimal("0.00"))
        item_amount = Decimal(item_subtotal * (Decimal(1.05))).quantize(Decimal("0.00"))

        if invoice_number not in invoice_summary:
            invoice_summary[invoice_number] = {
                'date': invoice_item.invoice.invoice_date,
                'customer': invoice_item.invoice.customer_name,
                'weight': invoice_item.item_quantity,
                'sub_total': item_subtotal,
                'invoice_amount': item_amount
            }
        else:
            summary = invoice_summary[invoice_number]
            summary['weight'] += invoice_item.item_quantity
            summary['sub_total'] += item_subtotal
            summary['invoice_amount'] += item_amount
    return invoice_summary

#################################

@login_required
def dashboard(request):

    # -------- SUMMARY COUNTS --------
    total_customers = Parties.objects.count()
    total_products = Product.objects.count()
    total_price_catalogs = PriceCatalog.objects.count()
    total_invoices = Invoice.objects.count()
    total_sales = Sales.objects.count()
    total_purchases = Purchase.objects.count()
    total_twine_inventory = TwineInventory.objects.count()

    # -------- TWINE INVENTORY SUMMARY --------
    from datetime import datetime
    current_month = datetime.now().month
    current_year = datetime.now().year
    twine_inventory_current = TwineInventory.objects.filter(month=current_month, year=current_year)
    total_twine_balance = sum(ti.balance for ti in twine_inventory_current)

    # -------- SALES SUMMARY --------
    sales_current_month = Sales.objects.filter(sales_entry_date__month=current_month, sales_entry_date__year=current_year)
    total_sales_amount = sum(s.total_amount for s in sales_current_month if s.total_amount)
    pending_sales = Sales.objects.filter(status='PENDING').count()

    # -------- PURCHASE SUMMARY --------
    purchase_current_month = Purchase.objects.filter(delivery_date__month=current_month, delivery_date__year=current_year)
    total_purchase_amount = sum(p.total_amount for p in purchase_current_month if p.total_amount)
    pending_purchases = Purchase.objects.filter(payment_status='PENDING').count()

    # -------- LATEST CUSTOMERS --------
    latest_customers = Parties.objects.order_by("-created_at")[:5]

    # -------- RECENT INVOICES --------
    recent_invoices = Invoice.objects.order_by("-invoice_date")[:5]

    # -------- RECENT SALES --------
    recent_sales = Sales.objects.order_by("-sales_entry_date")[:5]

    # -------- RECENT PURCHASES --------
    recent_purchases = Purchase.objects.order_by("-delivery_date")[:5]

    # -------- INVOICE CHART: INVOICES PER MONTH --------
    # invoice_data = (
    #     Invoice.objects
    #     .annotate(month=TruncMonth("invoice_date"))
    #     .values("month")
    #     .annotate(count=Count("id"))
    #     .order_by("month")
    # )
    from django.db.models import Count, Sum
    from django.db.models.functions import TruncMonth, Coalesce
    from decimal import Decimal
    invoice_data = (
    Invoice.objects
    .annotate(month=TruncMonth("invoice_date"))
    .values("month")
    .annotate(
        invoice_count=Count("id", distinct=True),
        total_gst_amount=Coalesce(
            Sum("items__item_gst_amount"),
            Decimal("0.00")
        ),
        total_amount_with_gst=Coalesce(
            Sum("items__item_total_with_gst"),
            Decimal("0.00")
        ),
    )
    .order_by("month")
)

    # print(invoice_data)
    invoice_months = [d["month"].strftime("%b %Y") for d in invoice_data]
    #invoice_counts = [d["count"] for d in invoice_data]
    invoice_counts = [d["invoice_count"] for d in invoice_data]
    total_gst_amount = [d["total_gst_amount"] for d in invoice_data]
    total_amount_with_gst = [d["total_amount_with_gst"] for d in invoice_data]

    # -------- PRICE CATALOG CHART: ITEMS PER CUSTOMER GROUP --------
    price_group_data = (
        PriceCatalog.objects
        .values("customer_group")
        .annotate(count=Count("id"))
        .order_by("customer_group")
    )

    catalog_groups = [d["customer_group"] for d in price_group_data]
    catalog_group_counts = [d["count"] for d in price_group_data]

    # -------- CONTEXT FOR TEMPLATE --------
    context = {
        "total_customers": total_customers,
        "total_products": total_products,
        "total_price_catalogs": total_price_catalogs,
        "total_invoices": total_invoices,
        "total_sales": total_sales,
        "total_purchases": total_purchases,
        "total_twine_inventory": total_twine_inventory,

        "latest_customers": latest_customers,
        "recent_invoices": recent_invoices,
        "recent_sales": recent_sales,
        "recent_purchases": recent_purchases,

        "invoice_months": invoice_months,
        "invoice_counts": invoice_counts,
        "total_gst_amount": total_gst_amount,
        "total_amount_with_gst":total_amount_with_gst,

        "catalog_groups": catalog_groups,
        "catalog_group_counts": catalog_group_counts,

        "total_twine_balance": total_twine_balance,
        "total_sales_amount": total_sales_amount,
        "pending_sales": pending_sales,
        "total_purchase_amount": total_purchase_amount,
        "pending_purchases": pending_purchases,
    }

    #TODO - check customer price catalog
    get_customer_price_dictionary()
    return render(request, "marania_invoice_app/dashboard.html", context)



def parties(request):
    customers = Parties.objects.prefetch_related("roles").all()
    form = CustomerForm()
   
    # Prepare unique values for select filters
    unique_codes = customers.values_list('code', flat=True).distinct()
    unique_names = customers.values_list('name', flat=True).distinct()
    unique_roles_qs = PartyRole.objects.filter(parties__in=customers).distinct()
    unique_roles = [role.role for role in unique_roles_qs]

    context = {
        "form": form,
        "customers": customers,
        "unique_codes": unique_codes,
        "unique_names": unique_names,
        "unique_roles": unique_roles,
    }

    return render(request, "marania_invoice_app/party.html", context)


def load_party(request, code):
    #customer = Parties.objects.prefetch_related("roles", "items").get(code=code)
    customer = Parties.objects.get(code=code)
 
    
    roles_ids = list(customer.roles.values_list('id', flat=True))

    transport_data = []
    for t in customer.transportations.all():  # use related_name 'items'
        transport_data.append({
            "delivery_place": t.delivery_place,
            "transporter_name": t.transporter_name,
            "transporter_gst": t.transporter_gst,
            "vehicle_name_number": t.vehicle_name_number,
            "is_default": t.is_default_transport,  # boolean
        })
    
    data = {
        #"id": customer.id,
        "code": customer.code,
        "name": customer.name,
        "gst": customer.gst,
        "phone": customer.phone,
        "email": customer.email,
        "address_bill_to": customer.address_bill_to,
        "address_ship_to": customer.address_ship_to,
        "is_within_state": customer.is_within_state,
        "roles": roles_ids,
        "transport_details": transport_data,
    }
    return JsonResponse(data)

def show_gst_calculator(request):
     return render(request, "marania_invoice_app/gst_calculator.html") 

def show_gst_calculator_from_main_UI(request):
     return render(request, "marania_invoice_app/view_gst_calculator.html") 

def invoice_entry(request):
    Invoices =Invoice.objects.order_by('-invoice_date', '-invoice_number')
    Customers = Parties.objects.all()
    customer_dict = defaultdict(lambda:-1)
    transporter_dict = defaultdict(lambda:-1)
    # price_dict = defaultdict(lambda:-1)
    
    # customer details 
    for customer in Parties.objects.all():
        customer_dict[customer.code] = {'name':customer.name, 'gst':customer.gst, 'phone':customer.phone, 'email':customer.email, 
                                        'address_bill_to':customer.address_bill_to, 'address_ship_to':customer.address_ship_to,
                                        'is_within_state':customer.is_within_state
                                        }
    
    # transportation details 
    for transporter in Transportation.objects.all():
        code = transporter.customer.code 
        transporter_dict_temp = {'delivery_place':transporter.delivery_place, 'transporter_name':transporter.transporter_name,
                            'transporter_gst':transporter.transporter_gst, 'vehicle_name_number':transporter.vehicle_name_number,
                            'is_default_transport':transporter.is_default_transport}
        if code not in transporter_dict:
            transporter_dict[code] = [transporter_dict_temp]
        else:
            transporter_dict[code].append(transporter_dict_temp)

    summary_data = invoice_summary()
    product_dict = get_product_dict()
    customer_price_dict = get_customer_price_dictionary()
    next_invoice_number = get_next_invoice_number()
    formatted_number = f"{int(next_invoice_number):04d}"
    invoice_number =  company_settings.invoice_prefix + "-" + formatted_number + "-" + company_settings.finance_year
    context = {'invoice_form': forms.InvoiceForm(initial={'invoice_number':invoice_number}) , 
               'invoices':Invoices, 'invoiceitems':summary_data,
               'customers':Customers, 'customer_dict': json.dumps(customer_dict),
               'transporter_dict':json.dumps(transporter_dict), 
               #'price_dict':json.dumps(price_dict),
               'customer_price_dict':json.dumps(customer_price_dict),
               'product_dict':json.dumps(product_dict),
               }

    return render(request, 'marania_invoice_app/invoice_entry.html', context)

      
############################-Functions-###################################


def create_party(request):
    if request.method == 'POST':
        action = request.POST.get("action")
        code = request.POST.get("code", "").strip()

        try:
            if action == "delete":
                Parties.objects.filter(code=code).delete()
                messages.success(request, f"Party {code} deleted successfully.")
                return redirect('parties')

            # Try to get existing party
            customer_instance = Parties.objects.get(code=code)
            form = CustomerForm(request.POST, instance=customer_instance)

        except Parties.DoesNotExist:
            # Create new party
            form = CustomerForm(request.POST)

        if form.is_valid():
            # Save party and roles (ManyToMany handled in form.save())
            customer_obj = form.save()

            # Delete existing Transportation entries
            customer_obj.transportations.all().delete()

            # Prepare new Transportation objects
            delivery_place_list = request.POST.getlist('delivery_place[]')
            transporter_name_list = request.POST.getlist('transporter_name[]')
            transporter_gst_list = request.POST.getlist('transporter_gst[]')
            vehicle_name_number_list = request.POST.getlist('vehicle_name_number[]')
            default_transport_index = request.POST.get('default_transport')

            transporter_list = []

            for index, place in enumerate(delivery_place_list):
                if place.strip():
                    is_default = (str(index) == default_transport_index)
                    transporter_list.append(Transportation(
                        customer_id=customer_obj.code,  # crucial for to_field='code'
                        delivery_place=place.strip(),
                        transporter_name=transporter_name_list[index].strip(),
                        transporter_gst=transporter_gst_list[index].strip(),
                        vehicle_name_number=vehicle_name_number_list[index].strip(),
                        is_default_transport=is_default,
                    ))

            # Bulk create Transportation safely
            if transporter_list:
                try:
                    Transportation.objects.bulk_create(transporter_list)
                except IntegrityError as e:
                    messages.error(request, f"Failed to save transportations: {str(e)}")
                    return render(request, 'marania_invoice_app/party.html', {'form': form})

            messages.success(request, f"Party {customer_obj.code} saved successfully.")
            return redirect('parties')

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = CustomerForm()

    context = {'form': form}
    return render(request, 'marania_invoice_app/party.html', context)



def invoice_save(request):
    if request.method == 'POST':
        try:
            # Check if invoice_id exists → UPDATE MODE
            invoice_number = request.POST.get('invoice_number')
            invoice_instance = Invoice.objects.filter(invoice_number=invoice_number).first()
            is_new_invoice = False
            if invoice_instance:
                form = InvoiceForm(request.POST, instance=invoice_instance)
            else:
                form = InvoiceForm(request.POST)
                is_new_invoice = True

            # Validate form
            if form.is_valid():

                invoice_instance = form.save()   # Creates or updates

                # --- SAVE CURRENT INVOICE NUMBER ---
                # invoice_number_int =  get_next_invoice_number() #int(form.cleaned_data['invoice_number'])

                try:
                    with transaction.atomic():
                        if is_new_invoice:
                            settings = CompanySettings.objects.select_for_update().get(id=1)
                            settings.current_invoice_number += 1
                            settings.save()
                except CompanySettings.DoesNotExist:
                    print("###Exception raised while saving the invoice number")
                    pass

                # ============================
                #   PROCESS INVOICE ITEMS
                # ============================

                # Get item lists
                item_spec_list             = request.POST.getlist('item_spec[]')
                item_code_list             = request.POST.getlist('item_code[]')
                item_description_list      = request.POST.getlist('item_description[]')
                item_mesh_size_list        = request.POST.getlist('item_mesh_size[]')
                item_mesh_depth_list       = request.POST.getlist('item_mesh_depth[]')
                item_quantity_list         = request.POST.getlist('item_quantity[]')
                item_price_list            = request.POST.getlist('item_price[]')
                item_colour_list           = request.POST.getlist('item_colour[]')
                item_hsn_code_list         = request.POST.getlist('item_hsn_code[]')
                item_gst_amount_list       = request.POST.getlist('item_gst_amount[]')
                item_total_with_gst_list   = request.POST.getlist('item_total_with_gst[]')
                
                # ============================
                #     UPDATE MODE CLEANUP
                # ============================
                if invoice_instance:
                    # Delete all old items before inserting new ones
                    InvoiceItem.objects.filter(invoice=invoice_instance).delete()

                # ============================
                #     INSERT NEW ITEMS
                # ============================

                invoice_item_list = []

                for index in range(len(item_code_list)):
                    if item_code_list[index].strip():

                        invoice_item_list.append(
                            InvoiceItem(
                                invoice               = invoice_instance,
                                item_spec             = item_spec_list[index],
                                item_code             = item_code_list[index],
                                item_description      = item_description_list[index],
                                item_mesh_size        = item_mesh_size_list[index],
                                item_mesh_depth       = item_mesh_depth_list[index],
                                item_quantity         = item_quantity_list[index],
                                item_price            = item_price_list[index],
                                item_colour           = item_colour_list[index],
                                item_hsn_code         = item_hsn_code_list[index],
                                item_gst_amount       = item_gst_amount_list[index],
                                item_total_with_gst   = item_total_with_gst_list[index],
                            )
                        )

                if invoice_item_list:
                    InvoiceItem.objects.bulk_create(invoice_item_list)

            else:
                print("FORM IS NOT VALID")
                print(form.errors)

        except Exception as e:
            print("Exception raised...")
            print(f"Error: {e}")
            return HttpResponse(f"An error occurred: {e}")

        return redirect('invoice_entry')

    else:
        form = InvoiceForm()

    invoices = Invoice.objects.all()
    context = {
        'invoice_form': InvoiceForm(),
        'invoices': invoices
    }
    return render(request, 'marania_invoice_app/invoice_entry.html', context)

def update_invoice_payment_status(invoice):
    """Recalculate payment_status for an invoice based on allocations vs gross_total."""
    total_alloc = PaymentAllocation.objects.filter(
        invoice=invoice
    ).aggregate(total=Sum('allocated_amount'))['total'] or 0
    if total_alloc >= invoice.gross_total:
        invoice.payment_status = 'Paid'
    elif total_alloc > 0:
        invoice.payment_status = 'Partial'
    else:
        invoice.payment_status = 'Pending'
    invoice.save(update_fields=['payment_status'])

def update_expense_payment_status(expense):
    """Recalculate payment_status for an expense based on allocations vs expense_amount."""
    total_alloc = PaymentAllocation.objects.filter(
        expense=expense
    ).aggregate(total=Sum('allocated_amount'))['total'] or 0
    balance = expense.expense_amount - total_alloc
    if balance <= 0:
        expense.payment_status = 'Paid'
    elif total_alloc > 0:
        expense.payment_status = 'Partially Paid'
    else:
        expense.payment_status = 'Pending'

def update_settlement_invoice_status(si):
    """Recalculate status for a settlement invoice based on allocations vs amount."""
    total_alloc = PaymentAllocation.objects.filter(
        settlement_invoice=si
    ).aggregate(total=Sum('allocated_amount'))['total'] or 0
    balance = si.amount - total_alloc
    if balance <= 0:
        si.status = 'Paid'
    elif total_alloc > 0:
        si.status = 'Partially Paid'
    else:
        si.status = 'Pending'
    si.save(update_fields=['status'])
    expense.balance_amount = balance
    expense.save(update_fields=['payment_status', 'balance_amount'])

def decimal_to_str(value):
    return format(Decimal(str(value)).normalize(), 'f')

def get_invoice_dictonaries(invoice_number):
    invoice_dict = get_invoices_dict()
    partices_dict = get_parties_dict()
    product_dict = get_product_dict()

    company_dict = {"logo_url": "/static/images/marania_eagle_logo.png",
                    "name": company_settings.company_title, 
                    "address": company_settings.company_address,
                    "gstin": company_settings.company_gst,
                    "state_name": company_settings.company_state,
                    "state_code": company_settings.company_state_code,
                    "contact": company_settings.company_phone, 
                    "bank_account_name": company_settings.bank_account_name, 
                    "bank_name": company_settings.bank_name,
                    "bank_account_no": company_settings.bank_account_number, 
                    "bank_branch": company_settings.bank_branch,
                    "bank_ifsc":  company_settings.bank_ifsc,  
                    }
    consignee_dict= {
            "name": invoice_dict[invoice_number]["ship_to_customer_name"],
            "address": invoice_dict[invoice_number]["ship_to_customer_address"],
            "gstin": invoice_dict[invoice_number]["ship_to_customer_gst"],
            "contact":invoice_dict[invoice_number]["ship_to_customer_contact"],
            # "state_name": "Tamil Nadu",
            # "state_code": "33"
        }
    
    buyer_dict= {
            "name": invoice_dict[invoice_number]["customer_name"],
            "address": invoice_dict[invoice_number]["customer_address"],
            "gstin": invoice_dict[invoice_number]["customer_gst"],
            "contact":invoice_dict[invoice_number]["customer_contact"],
            # "state_name": "Tamil Nadu",
            # "state_code": "33"
        }
    invoice_items = invoice_dict[invoice_number]["invoice_items"]
    items= [
            # {"packages": "1", "description": ".20DK/34MM/150MD", "hsn": "5608", "gst_rate": 5, "quantity": "50.700 KGS", "rate": "476.19", "unit": "KGS", "amount": "24,142.83"},
        ]
    sub_total = 0
    total_quantity = 0
    cgst = sgst = igst = 0 
    # based on the customer decide cgst/sgst or igst 
    customer_code = invoice_dict[invoice_number]["customer_code"]
    is_within_state = partices_dict[customer_code]["is_within_state"]

    cgst_rate = Decimal(company_settings.cgst)
    sgst_rate = Decimal(company_settings.sgst)
    igst_rate = Decimal(company_settings.igst)
    gst_rate = cgst_rate + sgst_rate if is_within_state else igst_rate


    for invoice_item in invoice_items:
        amount = invoice_item.item_quantity * invoice_item.item_price 
        amount = Decimal(amount).quantize(Decimal("0.00"), rounding=ROUND_DOWN)
        sub_total += amount
        total_quantity += invoice_item.item_quantity
        description =  f"{invoice_item.item_description}" 
        # based on the product decide the HSN
        item_code = str(invoice_item.item_code)
        hsn =  str(product_dict[invoice_item.item_code]["hsn"])
        # items.append({"packages": "1", "description": description,"hsn": hsn, "gst_rate": gst_rate, "quantity": str(invoice_item.item_quantity) + " KGS", 
        #               "rate": invoice_item.item_price, "unit": "KGS", "amount": amount})
        items.append({"packages": "1", "description": description,"hsn": hsn, "gst_rate": gst_rate, "quantity": str(invoice_item.item_quantity) , 
                      "rate": invoice_item.item_price, "unit": "KGS", "amount": amount})
        
        
       
    if is_within_state :
        cgst = Decimal(Decimal(sub_total) * Decimal(company_settings.cgst/100)).quantize(Decimal("0.00"), rounding=ROUND_DOWN)
        sgst = Decimal(Decimal(sub_total) * Decimal(company_settings.sgst/100)).quantize(Decimal("0.00"), rounding=ROUND_DOWN)
    else:
        igst = Decimal(Decimal(sub_total) * Decimal(company_settings.igst/100)).quantize(Decimal("0.00"), rounding=ROUND_DOWN)

    total = sub_total + cgst + sgst + igst
    # rounded_total = round(total,2)
    rounded_total = round_half_up(total).quantize(Decimal('0.00'))
    round_off_amount = rounded_total - total
    tax_words =""
    amount_words = number_to_words(Decimal(rounded_total))
    invoice_date = invoice_dict[invoice_number]["invoice_date"]
    
    invoice= {
            "invoice_no": invoice_number,
            "date": invoice_date.strftime("%d-%m-%Y"),
            "financial_year": company_settings.finance_year,
            "delivery_note": "",
            "payment_terms": "",
            "reference_no": "",
            "other_ref": "",
            "order_no": "",
            "order_date": "",
            "dispatch_doc": "",
            "delivery_date": "",
            "dispatch_mode": "",
            "destination": invoice_dict[invoice_number]["destination"],
            "lr_no": "",
            "vehicle_no": invoice_dict[invoice_number]["vehicle_no"],
            "terms_delivery": "",
            "dispatched_through":invoice_dict[invoice_number]["dispatched_through"],
            "subtotal": sub_total ,
            "total_quantity":total_quantity,
            "cgst_amount": cgst,
            "sgst_amount": sgst,
            "igst_amount": igst,
            "igst_rate": decimal_to_str(igst_rate),
            "sgst_rate": decimal_to_str(sgst_rate),
            "cgst_rate": decimal_to_str(cgst_rate),
            "round_off": round_off_amount,
            "total": rounded_total,
            "tax_words": "",
            "amount_words": amount_words}
    
    return company_dict, invoice, consignee_dict, buyer_dict, items



def invoice_view(request, invoice_number):
    invoice_dict = get_invoices_dict()
    if invoice_dict[invoice_number] == -1:
        context = {}
        return  render(request, 'marania_invoice_app/invoice_view.html', context) 

    company_dict, invoice, consignee_dict, buyer_dict, items = get_invoice_dictonaries(invoice_number)
    context = {"company":company_dict, "invoice":invoice, "consignee":consignee_dict, "buyer":buyer_dict, "items":items}

    return render(request, 'marania_invoice_app/invoice_view.html', context) 


def invoice_pdf(request, invoice_number):
    company_dict, invoice, consignee_dict, buyer_dict, items = get_invoice_dictonaries(invoice_number)
    context = {
        "company": company_dict,
        "invoice": invoice,
        "consignee": consignee_dict,
        "buyer": buyer_dict,
        "items": items
    }

    template = get_template('marania_invoice_app/invoice_view.html')
    html_string = template.render(context)

    css_string = """
        @page {
            size: A4;
            margin: 10mm;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }

        /* --- FIX HEADER ALIGNMENT --- */
        .invoice-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 10px;
        }

        .invoice-header-left,
        .invoice-header-right {
            width: 49%;
        }

        .invoice-box {
            border: 1px solid #000;
            padding: 8px;
        }
    """

    html = HTML(string=html_string)
    css = CSS(string=css_string)
    pdf_file = html.write_pdf(stylesheets=[css])

    response = HttpResponse(pdf_file, content_type='application/pdf')
    customer_name = buyer_dict["name"]
    
    customer_name = (customer_name.strip().replace(" ", "_").replace(".", ""))
    invoice_date = invoice["date"]
    invoice_date  = (invoice_date.strip().replace("-", "").replace(".", ""))
    invoice_title = f"Marania_Invoice_{invoice_number}_{customer_name}_{invoice_date}.pdf" 

    response['Content-Disposition'] = f'attachment; filename="{invoice_title}"'

    return response

   
def company_settings_view(request):
    settings, created = CompanySettings.objects.get_or_create(id=1)

    if request.method == "POST":
        form = CompanySettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Settings saved successfully!")
            return redirect("company_settings")  # redirect to same view

    else:
        form = CompanySettingsForm(instance=settings)
    return render(request, "marania_invoice_app/company_settings_form.html", {"form": form})
  

def get_invoice(request, invoice_number):
    # print("get invoice called!!!!!!")
    invoice = Invoice.objects.get(invoice_number=invoice_number)
    items = InvoiceItem.objects.filter(invoice=invoice).values(
        'item_spec', 'item_code', 'item_description', 'item_mesh_size', 'item_mesh_depth',
        'item_quantity', 'item_price' , 'item_colour', 'item_hsn_code', 'item_gst_amount', 'item_total_with_gst'
    )
    return JsonResponse({
        "invoice": {
            "invoice_number": invoice.invoice_number,
            "invoice_date": invoice.invoice_date.strftime("%Y-%m-%d"),
            "customer_code": invoice.customer_code,
            "customer_name": invoice.customer_name,
            "customer_gst": invoice.customer_gst,
            "customer_address": invoice.customer_address,
            "customer_contact": invoice.customer_contact,
            "customer_email": invoice.customer_email,
            "ship_to_customer_code": invoice.ship_to_customer_code,
            "ship_to_customer_name": invoice.ship_to_customer_name,
            "ship_to_customer_gst": invoice.ship_to_customer_gst,
            "ship_to_customer_address": invoice.ship_to_customer_address,
            "ship_to_customer_contact": invoice.ship_to_customer_contact,
            "ship_to_customer_email": invoice.ship_to_customer_email,
            "dispatched_through": invoice.dispatched_through,
            "destination": invoice.destination,
            "vehicle_name_number":invoice.vehicle_name_number,
            "transporter_gst": invoice.transporter_gst,
            "remark":invoice.remark,
            "payment_status": invoice.payment_status
        },
        "items": list(items)
    })



def add_price_list(request):
    if request.method == "POST":
        formset = PriceListFormSet(request.POST)

        if formset.is_valid():
            formset.save()
            messages.success(request, "Price list records saved successfully!")
            return redirect("add_price_list")
        else:
            messages.error(request, "Please correct the errors and try again.")
    else:
        formset = PriceListFormSet(queryset=PriceCatalog.objects.none())

    saved_prices = PriceCatalog.objects.all()
    products = Product.objects.all()

    unique_product_names = {f"{p.code}-{p.name}" for p in products}
    unique_customer_group = {p.customer_group for p in saved_prices}
    unique_price_codes =  {price.code for price in saved_prices}

    filter_header = {
        'product_names': unique_product_names,
        'customer_groups': unique_customer_group,
        'price_codes':unique_price_codes,
    }

    return render(
        request,
        "marania_invoice_app/price_catalog.html",
        {
            "formset": formset,
            "saved_prices": saved_prices,
            "filter_header": filter_header,
        }
    )

def load_price_list(request, price_code):
    items = PriceCatalog.objects.filter(code=price_code).order_by("sequence_id")

    data = {
        "items": [
            {
                "product": f"{p.product.code}-{p.product.name}",
                "sequence_id": p.sequence_id,
                "code": p.code,
                "customer_group": p.customer_group,
                "mesh_size_start": p.mesh_size_start,
                "mesh_size_end": p.mesh_size_end,
                "price": str(p.price),
            }
            for p in items
        ]
    }

    return JsonResponse(data)

def save_price_list(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)
        items = data.get("items", [])
        if not items:
            return JsonResponse({"error": "No items received"}, status=400)

        price_code = items[0].get("code")
        if not price_code:
            return JsonResponse({"error": "Price code missing"}, status=400)

        action = data.get("action")

        PriceCatalog.objects.filter(code=price_code).delete()

        if action == "delete":
            return JsonResponse({"status": "deleted"})

        new_objs = []
        for item in items:
            product_name = item.get("product")
            product_code = product_name.split("-")[0]

            product_obj = Product.objects.get(code=product_code)

            new_objs.append(PriceCatalog(
                product=product_obj,
                sequence_id=item.get("sequence_id"),
                code=item.get("code"),
                customer_group=item.get("customer_group"),
                mesh_size_start=item.get("mesh_size_start"),
                mesh_size_end=item.get("mesh_size_end"),
                price=item.get("price"),
            ))

        PriceCatalog.objects.bulk_create(new_objs)

        # reset the global cache
        reset_global_dict()

        return JsonResponse({"status": "saved", "count": len(new_objs)})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required    
def customer_price_catalog(request):
    customers = Parties.objects.all()
    unique_price_catalogs = list({ pc.code +"-"+pc.customer_group   for pc in PriceCatalog.objects.all()})
    price_catalogs = []
    for unique_price_catalog in unique_price_catalogs:
        price_code = get_first_part(unique_price_catalog)
        price_catalogs.append(PriceCatalog.objects.filter(code=price_code).first())
    
    catalogs = CustomerPriceCatalog.objects.all()
    
    if request.method == "POST":
        action = request.POST.get("action")
        testids =  request.POST.getlist("id")
        ids = request.POST.getlist("row_id")
        customer_vals = request.POST.getlist("customer")
        catalog_vals = request.POST.getlist("price_catalog")
        gst_vals = request.POST.getlist("gst_included")
        colour_vals = request.POST.getlist("colour_extra_price")
        mesh_vals = request.POST.getlist("small_mesh_size_extra_price")
        remark_vals = request.POST.getlist("remark")

        for idx in range(len(customer_vals)):
            row_id = ids[idx].strip() if idx < len(ids) else ""
            customer_code = customer_vals[idx]
            price_code = catalog_vals[idx]
            
            # Skip blank rows
            if not customer_code or not customer_vals:
                continue

            if action == "delete":
                CustomerPriceCatalog.objects.filter(customer__code=customer_code,price_code = price_code).delete()
                continue

            # SAVE ACTION
            try:
                # update logic - get the existing object 
                obj = CustomerPriceCatalog.objects.get(customer__code=customer_code, price_code=price_code)
            except CustomerPriceCatalog.DoesNotExist:
                # new entry - create new object
                obj = CustomerPriceCatalog()
            
            price_catalog_object = PriceCatalog.objects.filter(code=price_code).first()
            customer_object = Parties.objects.filter(code=customer_code).first()
            obj.customer = customer_object
            obj.price_catalog = price_catalog_object
            obj.price_code = price_code
            obj.gst_included = True if (  idx < len(gst_vals)  and gst_vals[idx] == "on" ) else False
            obj.colour_extra_price = float(colour_vals[idx] or 0)
            obj.small_mesh_size_extra_price = float(mesh_vals[idx] or 0)
            obj.remark = remark_vals[idx]
            obj.save()

            # reset global cache    
            reset_global_dict()

        return redirect("customer_price_catalog")

    # if the remark is empty assign the "-" value. 
    for c in catalogs:
        if not c.remark or c.remark.strip() == "":
            c.remark = "-"
        #TODO: final usage of price catalog - below code introduced for a hot fix. 
        # need to remove. and customer_price_catalog.html file to be modified.     
        c.price_catalog  = get_price_catalog_object_from_price_code(c.price_code)

    # UNIQUE FILTER LISTS
    unique_customers = list({str(c.customer) for c in catalogs})
    #unique_item_code_customer = list() #TODO list({str(c.price_catalog) for c in catalogs})
    unique_item_code_customer = []
    for c in catalogs:
        price_catalog_object =  get_price_catalog_object_from_price_code(c.price_code)
        unique_item_code_customer.append(str(price_catalog_object))

    unique_gst_included = list({str(c.gst_included) for c in catalogs})
    unique_remarks = list({str(c.remark) for c in catalogs})

    return render(request, "marania_invoice_app/customer_price_catalog.html", {
        "customers": customers,
        "price_catalogs": price_catalogs,
        "catalogs": catalogs,
        "unique_customers": unique_customers,
        "unique_item_code_customer": unique_item_code_customer,
        "unique_gst_included": unique_gst_included,
        "unique_remarks": unique_remarks,
    })

def load_customer_price_catalog(request, id):
    catalog = CustomerPriceCatalog.objects.get(id=id)
    #price_code = get_first_part(str(catalog.price_catalog))
    price_catalog_object = PriceCatalog.objects.filter(code=catalog.price_code).first()

    data = {
        "customer": catalog.customer.code,
        "price_catalog": price_catalog_object.code, 
        "gst_included": catalog.gst_included,
        "colour_extra_price": catalog.colour_extra_price,
        "small_mesh_size_extra_price": catalog.small_mesh_size_extra_price,
        "remark": catalog.remark
    }
    return JsonResponse(data)

@login_required
def product_master(request):
    products = Product.objects.select_related("material").all()
    materials = Materials.objects.all()

    if request.method == "POST":
        action = request.POST.get("action")

        codes = request.POST.getlist("code")
        names = request.POST.getlist("name")
        display_names = request.POST.getlist("display_name")
        hsn_codes = request.POST.getlist("hsn")
        material_ids = request.POST.getlist("material")   # ✅ NEW
        cgsts = request.POST.getlist("cgst")
        sgsts = request.POST.getlist("sgst")
        igsts = request.POST.getlist("igst")
        descriptions = request.POST.getlist("description")

        for idx in range(len(codes)):
            code = codes[idx].strip()
            name = names[idx].strip()

            if not code or not name:
                continue

            if action == "delete":
                Product.objects.filter(code=code).delete()
                continue

            try:
                obj = Product.objects.get(code=code)
            except Product.DoesNotExist:
                obj = Product()

            obj.code = code
            obj.name = name
            obj.display_name = display_names[idx]
            obj.hsn = hsn_codes[idx]
            obj.cgst = cgsts[idx] or 0
            obj.sgst = sgsts[idx] or 0
            obj.igst = igsts[idx] or 0
            obj.description = descriptions[idx]

            # ✅ MATERIAL SAVE
            if material_ids[idx]:
                obj.material = Materials.objects.get(id=material_ids[idx])

            obj.save()
            # reset the cache
            reset_global_dict()

        return redirect("product_master")

    unique_codes = sorted({p.code for p in products})
    unique_names = sorted({p.name for p in products})
    unique_hsn = sorted({p.hsn or "-" for p in products})
    unique_materials = sorted({p.material.name for p in products if p.material})

    return render(request, "marania_invoice_app/product_master.html", {
        "products": products,
        "materials": materials,              # ✅ NEW
        "unique_codes": unique_codes,
        "unique_names": unique_names,
        "unique_hsn": unique_hsn,
        "unique_materials": unique_materials # ✅ NEW
    })

def load_product(request, id):
    p = Product.objects.get(id=id)
    material_id = ""
    try:
        material_code = get_first_part(str(p.material))
        material = Materials.objects.filter(code=material_code).first()
        material_id =  material.id
    except Materials.DoesNotExist:
        material_id = None

    return JsonResponse({
        "code": p.code,
        "name": p.name,
        "display_name": p.display_name,
        "hsn": p.hsn,
        "material": material_id,
        "cgst": str(p.cgst),
        "sgst": str(p.sgst),
        "igst": str(p.igst),
        "description": p.description,
    })


def customer_price_dictionary_view(request):
    price_dict = get_customer_price_dictionary()

    rows = []

    for customer_code, products in price_dict.items():
        for product_code, sizes in products.items():
            for size_range, details in sizes.items():
                rows.append({
                    "customer_code": customer_code,
                    "customer_name": details.get("customer_name"),
                     "customer_group": details.get("customer_group"),
                    "product": product_code,
                    "size_range": size_range,
                    "price": details.get("price"),
                    "price_code": details.get("price_code"),
                    "sequence_id": details.get("sequence_id"),
                    # "customer_group": details.get("customer_group"),
                    "colour_extra_price": details.get("colour_extra_price"),
                    "small_mesh_size_extra_price": details.get("small_mesh_size_extra_price"),
                    "gst_included": details.get("gst_included"),
                })

    return render(
        request,
        "marania_invoice_app/view_customer_price_dictionary.html",
        {"rows": rows}
    )

def customer_price_dictionary_view_invoice(request):
    price_dict = get_customer_price_dictionary()

    rows = []

    for customer_code, products in price_dict.items():
        for product_code, sizes in products.items():
            for size_range, details in sizes.items():
                rows.append({
                    "customer_code": customer_code,
                    "customer_name": details.get("customer_name"),
                     "customer_group": details.get("customer_group"),
                    "product": product_code,
                    "size_range": size_range,
                    "price": details.get("price"),
                    "price_code": details.get("price_code"),
                    "sequence_id": details.get("sequence_id"),
                    # "customer_group": details.get("customer_group"),
                    "colour_extra_price": details.get("colour_extra_price"),
                    "small_mesh_size_extra_price": details.get("small_mesh_size_extra_price"),
                    "gst_included": details.get("gst_included"),
                })

    return render(
        request,
        "marania_invoice_app/customer_price_dictionary.html",
        {"rows": rows}
    )


def materials_view(request):

    if request.method == "POST":
        action = request.POST.get("action")

        # SAVE / UPDATE
        if action == "save":
            rows = zip(
                request.POST.getlist("code"),
                request.POST.getlist("name"),
                request.POST.getlist("displayname"),
                request.POST.getlist("price"),
                request.POST.getlist("gst"),
                request.POST.getlist("supplier"),
            )

            for code, name, displayname, price, gst, supplier in rows:
                if not code:
                    continue
                Materials.objects.update_or_create(
                    code=code,
                    defaults={
                        "name": name,
                        "displayname": displayname,
                        "price": price or 0,
                        "gst": gst or None,
                        "supplier_id": supplier or None,
                    }
                )

        # DELETE
        elif action == "delete":
            codes = request.POST.getlist("code")

            for code in codes:
                if code:
                    Materials.objects.filter(code=code).delete()

    context = {
        "materials": Materials.objects.select_related("supplier"),
        "suppliers": Parties.objects.filter(
            roles__role__iexact="supplier"
        ).distinct(),
    }

    return render(request, "marania_invoice_app/materials.html", context)


def load_material(request, pk):
    m = Materials.objects.get(pk=pk)
    return JsonResponse({
        "code": m.code,
        "name": m.name,
        "displayname": m.displayname,
        "price": m.price,
        "gst": m.gst,
        "supplier": m.supplier_id,
    })



@transaction.atomic
def import_data_no_unique_key(model_name, file_type, file):
    model = MODEL_REGISTRY[model_name]

    AUTO_FIELDS = {"id", "created_at", "updated_at", "sales_key", "purchase_key"}
    # Allow order_key to be imported for Order model
    if model_name != 'Order':
        AUTO_FIELDS.add("order_key")

    model_fields = {
        f.name: f
        for f in model._meta.fields
        if f.name not in AUTO_FIELDS
    }

    fk_fields = {
        f.name: f
        for f in model._meta.fields
        if isinstance(f, ForeignKey)
    }

    def normalize(record):
        clean = {}

        for key, value in record.items():
            key = key.strip()
            value = value.strip() if isinstance(value, str) else value

            if value in ("", None):
                continue

            # ---------- ForeignKey via *_id ----------
            if key.endswith("_id") and key[:-3] in fk_fields:
                clean[key] = value
                continue

            # ---------- ForeignKey via field name ----------
            if key in fk_fields:
                fk = fk_fields[key]
                rel_model = fk.remote_field.model
                rel_field = fk.target_field.name  # e.g. "code"
                
                # Special handling for Order foreign key in OrderSpecification
                if model_name == 'OrderSpecification' and key == 'order':
                    # Order ForeignKey targets order_key (primary key), but we have order_number
                    # Need to look up Order by order_number first
                    lookup_value = str(value).strip()
                    try:
                        if lookup_value == "":
                            clean[key] = ""
                        else:
                            # Look up Order by order_number, then assign the Order object
                            order_obj = rel_model.objects.get(order_key=lookup_value)
                            clean[key] = order_obj
                    except rel_model.DoesNotExist:
                        raise ValueError(f"Invalid FK value '{value}' for {key}. Order with order_key '{lookup_value}' not found.")
                    continue
                elif rel_field =="id": # TODO- fix the issue later
                    rel_field = "code"
                    value = value.split("-", 1)[0]

                try:
                    #clean[key] = rel_model.objects.get( **{rel_field: value}).first()
                    related_obj = rel_model.objects.filter(**{rel_field: value}).first()
                    clean[key] = related_obj
                except rel_model.DoesNotExist:
                    raise ValueError(
                        f"Invalid FK value '{value}' for {key}.{rel_field}"
                    )
                continue

            # ---------- Normal fields ----------
            if key not in model_fields:
                continue

            field = model_fields[key]

            if isinstance(field, BooleanField):
                clean[key] = str(value).upper() in ("TRUE", "1", "YES")
            else:
                clean[key] = value

        return clean

    def save(record):
        clean = normalize(record)
        model.objects.create(**clean)

    # ---------- CSV ----------
    if file_type == "csv":
        raw = file.read()
        decoded = None
        for enc in ("utf-8-sig", "utf-16", "cp1252", "latin1"):
            try:
                decoded = raw.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        if decoded is None:
            raise ValueError("Unable to decode CSV file")

        reader = csv.DictReader(io.StringIO(decoded))
        model.objects.all().delete()
        
        # Check if file has data rows (beyond headers)
        rows = list(reader)
        if not rows:
            return  # Empty file - table already cleared
        
        for row in rows:
            save(row)

    # ---------- JSON ----------
    elif file_type == "json":
        records = json.load(file)
        model.objects.all().delete()
        
        if not records:
            return  # Empty file - table already cleared
        
        for record in records:
            save(record)

    else:
        raise ValueError("Unsupported file type")
    


@transaction.atomic
def import_data(model_name, file_type, file):
    model = MODEL_REGISTRY[model_name]

    AUTO_FIELDS = {"id", "created_at", "updated_at", "sales_key", "purchase_key"}
    UNIQUE_KEY = "code"  # explicitly use 'code' as lookup
    if model_name == 'Invoice':
        UNIQUE_KEY = "invoice_number"
    elif model_name == 'Order':
        UNIQUE_KEY = "order_key"  # Use order_key as unique key since order_number is not unique


    IMPORT_STRATEGY = getattr(model, "IMPORT_STRATEGY", "update_or_create")
    UNIQUE_KEYS = getattr(model, "IMPORT_UNIQUE_KEYS", None)

    model_fields = {
        f.name: f
        for f in model._meta.fields
        if f.name not in AUTO_FIELDS
    }


    def normalize(record):
        clean = {}
        fk_fields = {
            f.name: f
            for f in model._meta.fields
            if isinstance(f, ForeignKey)
            }
        
        for key, value in record.items():
            key = key.strip()
            if value in ("", None):
                continue
            # ---------- ForeignKey handling first ----------
            if key in fk_fields:
                fk = fk_fields[key]
                rel_model = fk.remote_field.model
                rel_field = fk.target_field.name  # e.g. "code"
                
                # Special handling for Order foreign key in OrderSpecification
                if model_name == 'OrderSpecification' and key == 'order':
                    # Order ForeignKey targets order_key (primary key)
                    # CSV now contains order_key (PK) values directly
                    lookup_value = str(value).strip()
                    try:
                        if lookup_value == "":
                            clean[key] = ""
                        else:
                            # Look up Order by order_key (PK)
                            order_obj = rel_model.objects.get(order_key=lookup_value)
                            clean[key] = order_obj
                    except rel_model.DoesNotExist:
                        raise ValueError(f"Invalid FK value '{value}' for {key}. Order with order_key '{lookup_value}' not found.")
                    continue
                    continue
                elif rel_field == "id": #TODO - temp fix 
                    rel_field = 'code'
                    # Extract code from CSV like "LINGF-LINGESWARI FILAMENTS"
                    if  str(value) != "":
                        lookup_value = str(value).split("-", 1)[0].strip()
                    else:
                        lookup_value =""
                else:
                    # Extract code from CSV like "LINGF-LINGESWARI FILAMENTS"
                    if  str(value) != "":
                        lookup_value = str(value).split("-", 1)[0].strip()
                    else:
                        lookup_value =""

                try:
                    if lookup_value == "":
                        clean[key] = ""    
                    else:
                        clean[key] = rel_model.objects.get(**{rel_field: lookup_value})
                except rel_model.DoesNotExist:
                    raise ValueError(f"Invalid FK value '{value}' for {key}.{rel_field}")
                continue

            # ---------- Skip non-model fields ----------
            if key not in model_fields:
                continue

            field = model_fields[key]

            if isinstance(field, BooleanField):
                clean[key] = str(value).strip().upper() in ("TRUE", "1", "YES")
              # ---------- Handle DateField ----------
            elif isinstance(field, models.DateField):
                if isinstance(value, str):
                    # Convert MM/DD/YYYY or YYYY-MM-DD to date object
                    try:
                        if "/" in value:  # MM/DD/YYYY
                            value = datetime.strptime(value, "%m/%d/%Y").date()
                        else:  # assume ISO YYYY-MM-DD
                            value = datetime.strptime(value, "%Y-%m-%d").date()
                    except Exception as e:
                        raise ValueError(f"Invalid date format for {key}: {value}") from e

                    clean[key] = value

            else:
                clean[key] = str(value).strip()

        return clean

    def save(record):
        #print(f'save called witih record {record}')

        clean = normalize(record)
        if UNIQUE_KEY not in clean:
            raise ValueError(f"Missing unique key '{UNIQUE_KEY}' in row: {record}")

        lookup = {UNIQUE_KEY: clean.pop(UNIQUE_KEY)}
        obj, created = model.objects.update_or_create(
            **lookup,
            defaults=clean
        )
        #print(f"{'Created' if created else 'Updated'}: {lookup[UNIQUE_KEY]}")  # debug log

    # ---------- CSV ----------
    if file_type == "csv":
        raw = file.read()
        decoded = None
        for enc in ("utf-8-sig", "utf-16", "cp1252", "latin1"):
            try:
                decoded = raw.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        if decoded is None:
            raise ValueError("Unable to decode CSV file")

        reader = csv.DictReader(io.StringIO(decoded))
        records = list(reader)
        
        # Clear table first (even for empty file - user requirement)
        model.objects.all().delete()
        
        if not records:
            return  # Empty file - table already cleared
        
        for row in records:
            save(row)

    # ---------- JSON ----------
    elif file_type == "json":
        records = json.load(file)
        model.objects.all().delete()
        if not records:
            return  # Empty file - table already cleared
        for record in records:
            save(record)

    else:
        raise ValueError("Unsupported file type")



def export_view(request):
    if request.method == "POST":
        return export_data(
            request.POST["model"],
            request.POST["file_type"]
        )

    return render(request, "marania_invoice_app/export.html", {
        "models": MODEL_REGISTRY.keys()
    })


def import_view(request):
    if request.method == "POST":
        UNIQUE_KEY = UNIQUE_KEY_MODEL[request.POST["model"]]
    
        if UNIQUE_KEY == "":
            import_data_no_unique_key(request.POST["model"], request.POST["file_type"], request.FILES["file"])
        else:
            import_data(request.POST["model"], request.POST["file_type"], request.FILES["file"])

    return render(request, "marania_invoice_app/import.html", {
        "models": MODEL_REGISTRY.keys()
    })



@login_required
def backup_import_all(request):
    """
    Import all data from uploaded ZIP file containing per-table JSON or CSV files.
    """
    if request.method == "POST" and request.FILES.get("backup_zip"):
        backup_file = request.FILES["backup_zip"]

        # Save uploaded ZIP to temporary location
        temp_zip_path = os.path.join(settings.MEDIA_ROOT, backup_file.name)
        with open(temp_zip_path, "wb") as f:
            for chunk in backup_file.chunks():
                f.write(chunk)

        temp_extract_path = os.path.join(settings.MEDIA_ROOT, f"temp_import_{backup_file.name}")
        os.makedirs(temp_extract_path, exist_ok=True)

        # Extract ZIP
        with ZipFile(temp_zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_extract_path)

        # Iterate over files and import data
        for file_name in os.listdir(temp_extract_path):
            file_path = os.path.join(temp_extract_path, file_name)
            model_name, ext = os.path.splitext(file_name)
            ext = ext.lower()

            try:
                model = apps.get_model('marania_invoice_app', model_name)
            except LookupError:
                continue  # skip unknown models

            with transaction.atomic():
                # Optional: clear existing data
                model.objects.all().delete()

                if ext == ".json":
                    with open(file_path, "r", encoding="utf-8") as f:
                        rows = json.load(f)
                        for row in rows:
                            model.objects.create(**row)

                elif ext == ".csv":
                    with open(file_path, "r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            # Convert empty strings to None
                            row = {k: (v if v != "" else None) for k, v in row.items()}
                            model.objects.create(**row)

        # Cleanup
        os.remove(temp_zip_path)
        for root, dirs, files in os.walk(temp_extract_path, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(temp_extract_path)

        messages.success(request, "Import All completed successfully.")
        return redirect('dashboard')

    return render(request, 'marania_invoice_app/backup_import_all.html')


def backup_export_all(request):
    """
    Export all models in 'marania_invoice_app' as separate JSON or CSV files
    inside a timestamped folder, then compress to a ZIP for download.
    """
    export_format = request.GET.get('format')

    if not export_format:
        # Initial page load, show HTML
        return render(request, 'marania_invoice_app/backup_export_all.html')

    export_format = export_format.lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_folder_name = f"marania_backup_{export_format}_{timestamp}"
    backup_folder_path = os.path.join(settings.MEDIA_ROOT, backup_folder_name)

    os.makedirs(backup_folder_path, exist_ok=True)

    # Export each model as a separate file
    for model in apps.get_app_config('marania_invoice_app').get_models():
        model_name = model.__name__
        filename = f"{model_name}.{export_format}"
        file_path = os.path.join(backup_folder_path, filename)

        rows = list(model.objects.all().values())
        if export_format == "json":
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(rows, f, indent=2, default=str)
        elif export_format == "csv":
            if rows:
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    headers = rows[0].keys()
                    writer.writerow(headers)
                    for row in rows:
                        writer.writerow([row[h] for h in headers])

    # Create ZIP file
    zip_filename = f"{backup_folder_name}.zip"
    zip_path = os.path.join(settings.MEDIA_ROOT, zip_filename)
    with ZipFile(zip_path, "w") as zipf:
        for root, dirs, files in os.walk(backup_folder_path):
            for file in files:
                zipf.write(os.path.join(root, file), arcname=file)

    # Optional: remove the folder after zipping
    for root, dirs, files in os.walk(backup_folder_path, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))
    os.rmdir(backup_folder_path)

    # Serve ZIP as download
    with open(zip_path, "rb") as f:
        response = HttpResponse(f.read(), content_type="application/zip")
        response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
        return response
    


@login_required
def backup_clean_all(request):
    if request.method == "POST":
        # TODO: implement irreversible clean logic
        messages.warning(request, "⚠️ All data has been cleaned successfully.")
        return redirect('dashboard')

    return render(request, 'marania_invoice_app/backup_clean_all.html')


@login_required
def backup_sync(request):
    if request.method == "POST":
        # TODO: implement sync logic (local ↔ cloud)
        messages.success(request, "Sync completed successfully.")
        return redirect('dashboard')

    return render(request, 'marania_invoice_app/backup_sync.html')


# report functions 
def report_page(request):
    from datetime import datetime, timedelta
    
    report_key = request.GET.get("report", "invoice")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    # Set default date range to one month if not provided
    if not start_date or not end_date:
        today = datetime.now().date()
        # Default to previous month to current month (one month gap)
        # Or current month start to current month end
        start_date = (today.replace(day=1)).strftime("%Y-%m-%d")
        # Get first day of next month, then subtract one day to get last day of current month
        next_month = today.replace(day=28) + timedelta(days=4)  # Go to next month
        end_date = (next_month.replace(day=1) - timedelta(days=1)).strftime("%Y-%m-%d")

    config = REPORT_CONFIG[report_key]
    qs = get_report_queryset(report_key, start_date, end_date)
    rows = serialize_report_data(report_key, qs)

    return render(request, "marania_invoice_app/report_page.html", {
        "reports": REPORT_CONFIG,
        "current_report": report_key,
        "columns": [label for _, label in config["columns"]],
        "rows": rows,
        "start_date": start_date,
        "end_date": end_date,
    })


def report_csv(request):
    report_key = request.GET.get("report")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    qs = get_report_queryset(report_key, start_date, end_date)
    rows = serialize_report_data(report_key, qs)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{report_key}.csv"'

    writer = csv.writer(response)
    if rows:
        writer.writerow(rows[0].keys())
        for row in rows:
            writer.writerow(row.values())

    return response


def report_pdf(request):
    report_key = request.GET.get("report")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    qs = get_report_queryset(report_key, start_date, end_date)
    rows = serialize_report_data(report_key, qs)

    html = render(request, "marania_invoice_app/report_table.html", {
        "rows": rows
    }).content.decode("utf-8")

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{report_key}.pdf"'
    HTML(string=html).write_pdf(response)
    return response


def order_entry(request):
    orders = Order.objects.all().prefetch_related('specifications')

    if request.method == "POST":
        action = request.POST.get("action")

        # Handle single order delete (from table action button)
        if action == "delete":
            order_key = request.POST.get("order_key")
            if order_key:
                Order.objects.filter(order_key=order_key).delete()
                messages.success(request, "Order deleted successfully.")
            return redirect('order_entry')

        drafts_raw = request.POST.get("drafts_data")
        edit_mode = request.POST.get("edit_mode", "single_edit")  # Get edit mode from frontend

        if not drafts_raw and request.content_type == 'application/json':
            try:
                body = json.loads(request.body)
                drafts_raw = body.get('drafts_data')
                edit_mode = body.get('edit_mode', 'single_edit')
            except (json.JSONDecodeError, AttributeError):
                drafts_raw = None

        saved_count = 0
        if drafts_raw:
            if isinstance(drafts_raw, str):
                try:
                    entries = json.loads(drafts_raw)
                    if not isinstance(entries, list):
                        entries = []
                except json.JSONDecodeError:
                    entries = []
            else:
                entries = drafts_raw if isinstance(drafts_raw, list) else []
            batch_sequence = None
            batch_order_number = None
            base_twine = None
            now = datetime.now()
            saved_count = 0

            # Determine batch order_number
            for entry in entries:
                twine = (entry.get("twine") or "").strip()
                if not twine:
                    continue
                order_key = entry.get("order_key")
                if order_key is not None:
                    order_key = str(order_key).strip()
                    if order_key and batch_order_number is None:
                        try:
                            batch_order_number = Order.objects.values_list('order_number', flat=True).get(order_key=order_key)
                        except Order.DoesNotExist:
                            pass
                if batch_order_number is None:
                    on = (entry.get("order_number") or "").strip()
                    if on:
                        batch_order_number = on

            # Handle group_edit mode: delete all orders with the same order_number before processing
            if edit_mode == 'group_edit' and batch_order_number:
                Order.objects.filter(order_number=batch_order_number).delete()

            batch_sequence = None
            base_twine = None
            for entry in entries:
                twine = (entry.get("twine") or "").strip()
                if not twine:
                    continue

                order_key = entry.get("order_key")
                if order_key is not None:
                    order_key = str(order_key).strip()
                else:
                    order_key = ""
                is_update = bool(order_key)

                # Check if order_number is provided for update
                updated_order_number = None
                if is_update and entry.get("order_number"):
                    updated_order_number = str(entry.get("order_number")).strip()

                if is_update:
                    try:
                        obj = Order.objects.get(order_key=order_key)
                    except Order.DoesNotExist:
                        obj = Order()
                    if batch_order_number is None:
                        batch_order_number = obj.order_number
                else:
                    obj = Order()
                    if batch_order_number is None:
                        batch_order_number = (entry.get("order_number") or "").strip() or None
                    if batch_order_number is None:
                        batch_sequence = (Order.objects.aggregate(max_seq=Max('order_sequence'))['max_seq'] or 0) + 1
                        base_twine = base_twine or twine
                        batch_order_number = f"{base_twine}-{batch_sequence}"

                raw_seq = entry.get("order_sequence")
                obj.order_sequence = int(str(raw_seq).strip()) if raw_seq is not None and str(raw_seq).strip() else (batch_sequence or (Order.objects.aggregate(max_seq=Max('order_sequence'))['max_seq'] or 0) + 1)
                obj.order_number = batch_order_number or entry.get("order_number") or f"{twine}-{obj.order_sequence}"
                obj.order_date = entry.get("order_date") or now.strftime('%Y-%m-%d')
                obj.twine = twine
                obj.quantity = entry.get("quantity") or 0
                obj.quantity_unit = entry.get("quantity_unit") or "Bag"
                obj.customer = entry.get("customer") or ""
                obj.unit_price = entry.get("unit_price") or None
                obj.is_gst_included = entry.get("is_gst_included") in (True, "True", "true", "on")
                obj.status = entry.get("status") or "Ordered"
                raw_lsd = entry.get("last_status_date")
                if raw_lsd and str(raw_lsd).strip():
                    obj.last_status_date = str(raw_lsd).strip()
                else:
                    obj.last_status_date = now.strftime('%Y-%m-%d')
                obj.order_instructions = entry.get("order_instructions") or ""
                obj.comments = entry.get("comments") or ""
                obj.updated_at = now
                if not is_update:
                    obj.created_at = now
                
                # Allow order_number to be updated on existing orders
                if is_update and updated_order_number:
                    obj.order_number = updated_order_number
                    
                obj.save()
                saved_count += 1

                # Replace specifications
                obj.specifications.all().delete()
                specs_data = entry.get("specifications")
                if specs_data:
                    for s in specs_data:
                        raw_pcs = s.get("no_of_pcs")
                        OrderSpecification.objects.create(
                            order=obj,
                            mesh_size=s.get("mesh_size") or None,
                            mesh_depth=s.get("mesh_depth") or "",
                            salvage=s.get("salvage") or "",
                            piece_weight=s.get("piece_weight") or "",
                            colour=s.get("colour") or "White",
                            no_of_pcs=int(str(raw_pcs).strip()) if raw_pcs is not None and str(raw_pcs).strip() else None,
                        )
                else:
                    # Fallback to flat fields
                    raw_pcs = entry.get("no_of_pcs")
                    OrderSpecification.objects.create(
                        order=obj,
                        mesh_size=entry.get("mesh_size") or None,
                        mesh_depth=entry.get("mesh_depth") or "",
                        salvage=entry.get("salvage") or "",
                        piece_weight=entry.get("piece_weight") or "",
                        colour=entry.get("colour") or "White",
                        no_of_pcs=int(str(raw_pcs).strip()) if raw_pcs is not None and str(raw_pcs).strip() else None,
                    )
        else:
            keys = request.POST.getlist("order_key")
            order_number = request.POST.getlist("order_number")
            order_dates = request.POST.getlist("order_date")
            twines = request.POST.getlist("twine")
            mesh_sizes = request.POST.getlist("mesh_size")
            mesh_depths = request.POST.getlist("mesh_depth")
            salvages = request.POST.getlist("salvage")
            piece_weights = request.POST.getlist("piece_weight")
            quantities = request.POST.getlist("quantity")
            quantity_units = request.POST.getlist("quantity_unit")
            customers = request.POST.getlist("customer")
            unit_prices = request.POST.getlist("unit_price")
            is_gst_includeds = request.POST.getlist("is_gst_included")
            statuses = request.POST.getlist("status")
            colours = request.POST.getlist("colour")
            no_of_pcss = request.POST.getlist("no_of_pcs")
            order_instructions = request.POST.getlist("order_instructions")
            comments = request.POST.getlist("comments")

            for idx in range(len(twines)):
                order_key = keys[idx].strip() if idx < len(keys) else ""
                twine = twines[idx].strip()
                if not twine:
                    continue

                try:
                    obj = Order.objects.get(order_key=order_key) if order_key else None
                except Order.DoesNotExist:
                    obj = None

                is_new = obj is None

                if is_new:
                    obj = Order()
                    next_seq = (Order.objects.aggregate(max_seq=Max('order_sequence'))['max_seq'] or 0) + 1
                    obj.order_sequence = next_seq
                    obj.order_number = f"{twine}-{next_seq}"

                obj.order_date = order_dates[idx] if idx < len(order_dates) else None
                obj.twine = twine
                obj.quantity = quantities[idx] if idx < len(quantities) else 0
                obj.quantity_unit = quantity_units[idx] if idx < len(quantity_units) else "Bag"
                obj.customer = customers[idx] if idx < len(customers) else ""
                obj.unit_price = unit_prices[idx] if idx < len(unit_prices) and unit_prices[idx] else None
                obj.is_gst_included = True if (idx < len(is_gst_includeds) and is_gst_includeds[idx] == "on") else False
                obj.status = statuses[idx] if idx < len(statuses) else "Ordered"
                obj.order_instructions = order_instructions[idx] if idx < len(order_instructions) else ""
                obj.comments = comments[idx] if idx < len(comments) else ""
                
                # Allow order_number to be updated on existing orders
                if is_update:
                    updated_order_number = None
                    if idx < len(order_number):
                        updated_order_number = order_number[idx].strip() if order_number[idx] else None
                    elif entry.get("order_number"):
                        updated_order_number = str(entry.get("order_number")).strip()
                    
                    if updated_order_number:
                        obj.order_number = updated_order_number
                        
                obj.save()

                # Read spec rows from POST (indexed by spec_idx)
                spec_mesh_sizes = request.POST.getlist("spec_mesh_size")
                spec_mesh_depths = request.POST.getlist("spec_mesh_depth")
                spec_salvages = request.POST.getlist("spec_salvage")
                spec_piece_weights = request.POST.getlist("spec_piece_weight")
                spec_colours = request.POST.getlist("spec_colour")
                spec_no_of_pcss = request.POST.getlist("spec_no_of_pcs")

                # Delete existing specs and recreate
                obj.specifications.all().delete()
                num_specs = max(len(spec_mesh_sizes), 1)
                for si in range(num_specs):
                    OrderSpecification.objects.create(
                        order=obj,
                        mesh_size=spec_mesh_sizes[si] if si < len(spec_mesh_sizes) else None,
                        mesh_depth=spec_mesh_depths[si] if si < len(spec_mesh_depths) else "",
                        salvage=spec_salvages[si] if si < len(spec_salvages) else "",
                        piece_weight=spec_piece_weights[si] if si < len(spec_piece_weights) else "",
                        colour=spec_colours[si] if si < len(spec_colours) and spec_colours[si] else "White",
                        no_of_pcs=int(spec_no_of_pcss[si]) if si < len(spec_no_of_pcss) and spec_no_of_pcss[si] else None,
                    )

        if saved_count:
            messages.success(request, f'{saved_count} order(s) saved successfully')
        if request.content_type == 'application/json':
            return JsonResponse({'status': 'ok', 'saved': saved_count})
        return redirect("order_entry")

    orders_data = list(orders.values(
        'order_key', 'order_sequence', 'order_number', 'order_date', 'customer',
        'twine', 'quantity', 'quantity_unit', 'unit_price', 'is_gst_included',
        'status', 'order_instructions', 'comments',
    ))
    
    # Ensure order_number is included in the context for templates
    for order in orders:
        order.order_number = order.order_number
    order_keys = [o['order_key'] for o in orders_data]
    specs = list(OrderSpecification.objects.filter(order__order_key__in=order_keys).values(
        'order_id', 'mesh_size', 'mesh_depth', 'salvage', 'piece_weight', 'colour', 'no_of_pcs',
    ))
    specs_by_order = {}
    for s in specs:
        specs_by_order.setdefault(s['order_id'], []).append(
            {k: s[k] for k in ('mesh_size', 'mesh_depth', 'salvage', 'piece_weight', 'colour', 'no_of_pcs')}
        )
    for item in orders_data:
        order_specs = specs_by_order.get(item['order_key'], [])
        item['specifications'] = order_specs
        # Flatten first spec for backward compat with JS
        first = order_specs[0] if order_specs else {}
        for fld in ('mesh_size', 'mesh_depth', 'salvage', 'piece_weight', 'colour', 'no_of_pcs'):
            item[fld] = first.get(fld)
    orders_json = json.dumps(orders_data, default=str)

    next_order_sequence = (Order.objects.aggregate(max_seq=Max('order_sequence'))['max_seq'] or 0) + 1

    parties = Parties.objects.all()
    products = Product.objects.all()
    colours_list = list(OrderSpecification.objects.exclude(colour__isnull=True).exclude(colour='').values_list('colour', flat=True).distinct().order_by('colour'))

    context = {
        "orders": orders,
        "orders_json": orders_json,
        "next_order_sequence": next_order_sequence,
        "parties": parties,
        "products": products,
        "colours_list": colours_list,
    }
    return render(request, "marania_invoice_app/order_entry.html", context)


def sheet_sales_view(request):
    sheet, _ = ExcelSheet.objects.get_or_create(name="Invoice Sheet")
    return render(request, 'marania_invoice_app/sheet_sales.html', {
        'sheet_data': json.dumps(sheet.data)
    })

@csrf_exempt
def sheet_sales_save(request):
    if request.method == "POST":
        body = json.loads(request.body)
        sheet = ExcelSheet.objects.get(name="Invoice Sheet")
        sheet.data = body['data']
        sheet.save()
        return JsonResponse({'status': 'saved'})


# =======================
# Sales Entry
# =======================

def parse_date(value):
    if not value:
        return None
    s = str(value).strip()
    try:
        datetime.strptime(s, '%Y-%m-%d')
        return s
    except (ValueError, TypeError):
        return None

def sales_entry(request):
    sales_list = Sales.objects.all().order_by('-sales_entry_date', '-order_no')
    products = Product.objects.all()
    parties = Parties.objects.all()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "delete":
            sales_key = request.POST.get("sales_key")
            if sales_key:
                Sales.objects.filter(sales_key=sales_key).delete()
                messages.success(request, "Sale deleted successfully.")
            return redirect('sales_entry')

        if action == "delete_cart_items":
            sales_keys = request.POST.get("sales_keys")
            if sales_keys:
                try:
                    sales_key_list = json.loads(sales_keys)
                    if sales_key_list:
                        Sales.objects.filter(sales_key__in=sales_key_list).delete()
                except (json.JSONDecodeError, TypeError):
                    pass
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'ok'})
            return redirect('sales_entry')

        drafts_raw = request.POST.get("drafts_data")

        if not drafts_raw and request.content_type == 'application/json':
            try:
                body = json.loads(request.body)
                drafts_raw = body.get('drafts_data')
            except (json.JSONDecodeError, AttributeError):
                drafts_raw = None

        saved_count = 0
        if drafts_raw:
            if isinstance(drafts_raw, str):
                try:
                    entries = json.loads(drafts_raw)
                    if not isinstance(entries, list):
                        entries = []
                except json.JSONDecodeError:
                    entries = []
            else:
                entries = drafts_raw if isinstance(drafts_raw, list) else []

            now = datetime.now()
            order_nos = []
            entry_sales_keys = []
            edit_mode = request.POST.get('edit_mode', 'single_edit')
            
            for entry in entries:
                twine = (entry.get("twine") or "").strip()
                if not twine:
                    continue
                ono = entry.get("order_no") or ""
                if ono:
                    order_nos.append(ono)
                sk = entry.get('sales_key')
                if sk:
                    entry_sales_keys.append(sk)

            if edit_mode == 'group_edit' and order_nos:
                Sales.objects.filter(order_no__in=order_nos).delete()
            elif edit_mode == 'single_edit' and entry_sales_keys:
                Sales.objects.filter(sales_key__in=entry_sales_keys).delete()

            for entry in entries:
                twine = (entry.get("twine") or "").strip()
                if not twine:
                    continue

                # Check if invoice_no is provided for update
                updated_invoice_no = None
                if entry.get("invoice_no"):
                    updated_invoice_no = str(entry.get("invoice_no")).strip()

                obj = Sales()

                obj.order_no = entry.get("order_no") or ""
                obj.invoice_no = entry.get("invoice_no") or ""
                obj.sales_entry_date = parse_date(entry.get("sales_entry_date")) or now.strftime('%Y-%m-%d')
                obj.customer = entry.get("customer") or ""
                obj.twine = twine
                obj.speification = entry.get("speification") or ""
                obj.colour = entry.get("colour") or "White"
                obj.piece_weight = entry.get("piece_weight") or ""
                raw_pc = entry.get("piece_count")
                if raw_pc is not None and str(raw_pc).strip():
                    obj.piece_count = int(str(raw_pc).strip())
                else:
                    obj.piece_count = None
                obj.initial_weight = entry.get("initial_weight") or None
                obj.processed_weight = entry.get("processed_weight") or None
                obj.unit_price = entry.get("unit_price") or None
                obj.gst_rate = entry.get("gst_rate") or None
                obj.total_amount = entry.get("total_amount") or None
                obj.delivery_date = parse_date(entry.get("delivery_date"))
                obj.status = entry.get("status") or "ON_HOLD_PROCESSING"
                obj.payment_date = parse_date(entry.get("payment_date"))
                obj.remarks = entry.get("remarks") or ""
                obj.created_at = now
                obj.updated_at = now
                
                # Allow invoice_no to be updated on existing sales
                if updated_invoice_no:
                    obj.invoice_no = updated_invoice_no
                    
                obj.save()
                saved_count += 1

            if saved_count:
                messages.success(request, f"{saved_count} sale(s) saved successfully.")
        else:
            messages.error(request, "No sales data received.")

        if request.content_type == 'application/json':
            return JsonResponse({'saved_count': saved_count})
        return redirect('sales_entry')

    sales_json = []
    for s in sales_list:
        # Check if invoice_no is provided for update (in the context of the form)
        # We need to check if this specific sale is being updated
        updated_invoice_no = None
        
        # If the sale has an invoice_no that is not empty, use it
        if s.invoice_no:
            updated_invoice_no = s.invoice_no
        
        # Build the sales JSON with updated invoice_no support
        sales_json.append({
            'sales_key': s.sales_key,
            'order_no': s.order_no,
            'invoice_no': updated_invoice_no or s.invoice_no or '',
            'sales_entry_date': str(s.sales_entry_date) if s.sales_entry_date else '',
            'customer': s.customer or '',
            'twine': s.twine or '',
            'speification': s.speification or '',
            'colour': s.colour or 'White',
            'piece_weight': s.piece_weight or '',
            'piece_count': s.piece_count,
            'initial_weight': str(s.initial_weight) if s.initial_weight else '',
            'processed_weight': str(s.processed_weight) if s.processed_weight else '',
            'unit_price': str(s.unit_price) if s.unit_price else '',
            'gst_rate': str(s.gst_rate) if s.gst_rate else '',
            'total_amount': str(s.total_amount) if s.total_amount else '',
            'delivery_date': str(s.delivery_date) if s.delivery_date else '',
            'status': s.status or 'PENDING',
            'payment_date': str(s.payment_date) if s.payment_date else '',
            'remarks': s.remarks or '',
        })

    return render(request, 'marania_invoice_app/sales_entry.html', {
        'sales': sales_list,
        'sales_json': json.dumps(sales_json),
        'products': products,
        'parties': parties,
    })


def submit_invoice_from_spec(request):
    """Parse invoice specification and auto-create invoices for each customer."""
    if request.method == 'POST':
        try:
            import json
            import re
            from decimal import Decimal, ROUND_HALF_UP
            from datetime import date

            data = json.loads(request.body)
            spec_text = data.get('spec_text', '')

            if not spec_text:
                return JsonResponse({'success': False, 'error': 'No specification text provided'})

            # Parse the specification text
            lines = spec_text.strip().split('\n')
            customer_groups = {}
            current_customer = None
            product_dict = get_product_dict()

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Check if line starts with a number followed by "Customer:"
                if re.match(r'^\d+\.\s+Customer:', line):
                    # Extract customer code and name
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        customer_info = parts[1].strip()
                        current_customer = customer_info
                        customer_groups[current_customer] = []
                elif current_customer and line:
                    # This is a specification line for the current customer
                    # Format: TWINE CODE/MM/MD/PROCESSED WEIGHT/PRICE/COLOUR
                    spec_parts = line.split('/')
                    if len(spec_parts) >= 6:
                        customer_groups[current_customer].append({
                            'twine_code': spec_parts[0].strip(),
                            'mm': spec_parts[1].strip(),
                            'md': spec_parts[2].strip(),
                            'processed_weight': spec_parts[3].strip(),
                            'price': spec_parts[4].strip(),
                            'colour': spec_parts[5].strip()
                        })

            # Create invoices for each customer
            created_invoices = []
            settings = CompanySettings.objects.get(id=1)

            for customer_info, items in customer_groups.items():
                if not items:
                    continue

                # Parse customer code (e.g., "AN-ASIAN NETS" -> code="AN", name="ASIAN NETS")
                customer_parts = customer_info.split('-', 1)
                customer_code = customer_parts[0].strip() if len(customer_parts) > 1 else customer_info
                customer_name = customer_parts[1].strip() if len(customer_parts) > 1 else customer_info

                # Get customer details from Parties model
                party = Parties.objects.filter(code=customer_code).first()
                if not party:
                    continue

                # Get next invoice number - auto genreated code disabled as its not working as expected
                #current_invoice_num = settings.current_invoice_number
                #invoice_number = f"INV-{current_invoice_num:04d}"

                next_invoice_number = get_next_invoice_number()
                formatted_number = f"{int(next_invoice_number):04d}"
                invoice_number =  company_settings.invoice_prefix + "-" + formatted_number + "-" + company_settings.finance_year


                # Create invoice
                invoice = Invoice.objects.create(
                    invoice_date=date.today(),
                    invoice_number=invoice_number,
                    customer_code=party.code,
                    customer_name=party.name,
                    customer_gst=party.gst or '',
                    customer_address=party.address_bill_to or '',
                    customer_contact=party.phone or '',
                    customer_email=party.email or '',
                    ship_to_customer_code=party.code,
                    ship_to_customer_name=party.name,
                    ship_to_customer_gst=party.gst or '',
                    ship_to_customer_address=party.address_ship_to or party.address_bill_to or '',
                    ship_to_customer_contact=party.phone or '',
                    ship_to_customer_email=party.email or '',
                    payment_status='Pending',
                    remark='Auto-generated from Sales Invoice Specification'
                )

                # Get default transportation
                default_transport = party.transportations.filter(is_default_transport=True).first()
                if default_transport:
                    invoice.dispatched_through = default_transport.transporter_name or ''
                    invoice.destination = default_transport.delivery_place or ''
                    invoice.vehicle_name_number = default_transport.vehicle_name_number or ''
                    invoice.transporter_gst = default_transport.transporter_gst or ''
                    invoice.save()

                # Create invoice items
                invoice_items = []
                total_quantity = Decimal('0.00')
                subtotal = Decimal('0.00')

                for item in items:
                    # Build specification from parts
                    #spec_text = #f"{item['mm']}MM-{item['md']}MD"
                    spec_text = f"{item['twine_code']}/{item['mm']}/{item['md']}/{item['processed_weight']}/{item['price']}/{item['colour']}"
                    product_description = product_dict[item['twine_code']]
                    product_description = product_description["display_name"]
                    product_description = f"{product_description}-{item['mm']}MM/{item['md']}MD"
                    item_colour = (item['colour']).upper()
                    if item_colour:
                        product_description = f"{product_description}/{item_colour}"

                    quantity = Decimal(item['processed_weight'] or '0')
                    price = Decimal(item['price'] or '0')
                    colour = (item.get('colour') or '').upper() # item['colour'] or ''

                    # Calculate GST
                    if party.is_within_state:
                        gst_rate = (settings.cgst or 0) + (settings.sgst or 0)
                    else:
                        gst_rate = settings.igst or 0

                    item_total = quantity * price
                    gst_amount = item_total * (Decimal(str(gst_rate)) / Decimal('100'))
                    item_total_with_gst = item_total + gst_amount

                    invoice_items.append(InvoiceItem(
                        invoice=invoice,
                        item_spec=spec_text,
                        item_code=item['twine_code'],
                        item_description= product_description, 
                        item_mesh_size=item['mm'],
                        item_mesh_depth=item['md'],
                        item_quantity=str(quantity),
                        item_price=str(price),
                        item_colour=colour,
                        item_hsn_code='',
                        item_gst_amount=str(gst_amount),
                        item_total_with_gst=str(item_total_with_gst)
                    ))

                    total_quantity += quantity
                    subtotal += item_total

                # Bulk create invoice items
                if invoice_items:
                    InvoiceItem.objects.bulk_create(invoice_items)

                # Calculate totals
                total_gst = subtotal * (Decimal(str(gst_rate)) / Decimal('100'))
                gross_total = subtotal + total_gst
                round_off = (gross_total * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP) / 100 - gross_total
                gross_total = gross_total + round_off

                # Update invoice with totals
                invoice.quantity_total = total_quantity
                invoice.subtotal = subtotal
                invoice.cgst_amount = total_gst / 2 if party.is_within_state else Decimal('0.00')
                invoice.sgst_amount = total_gst / 2 if party.is_within_state else Decimal('0.00')
                invoice.igst_amount = total_gst if not party.is_within_state else Decimal('0.00')
                invoice.round_off = round_off
                invoice.gross_total = gross_total
                invoice.save()

                # Increment invoice number
                settings.current_invoice_number += 1
                settings.save()

                created_invoices.append({
                    'invoice_number': invoice_number,
                    'customer': customer_name,
                    'items_count': len(items)
                })

            return JsonResponse({
                'success': True,
                'message': f'Successfully created {len(created_invoices)} invoices',
                'invoices': created_invoices
            })

        except Exception as e:
            import traceback
            return JsonResponse({'success': False, 'error': str(e), 'traceback': traceback.format_exc()})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def copy_order_to_sales(request, order_key):
    try:
        order = Order.objects.prefetch_related('specifications').get(order_key=order_key)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('order_entry')

    specs = order.specifications.all()
    if not specs:
        messages.error(request, "No specifications found for this order.")
        return redirect('order_entry')

    # Generate base sequence from max existing sales_sequence
    base_seq = (Sales.objects.aggregate(max_seq=Max('sales_sequence'))['max_seq'] or 0) + 1
    created_count = 0

    for index, spec in enumerate(specs, start=1):
        seq = base_seq + index - 1

        mesh_size = spec.mesh_size if spec else ''
        mesh_depth = spec.mesh_depth if spec else ''
        salvage = spec.salvage if spec else ''
        md_disp = mesh_depth if mesh_depth and 'MD' in mesh_depth.upper() else (mesh_depth + 'MD' if mesh_depth else '')
        sal_disp = salvage if salvage and 'SEL' in salvage.upper() else (salvage + 'Sel' if salvage else '')
        spec_text = f"{mesh_size}MM-{md_disp}-{sal_disp}" if mesh_size or md_disp or sal_disp else ""

        # Determine GST rate from party/company settings
        party = Parties.objects.filter(code=order.customer).first()
        settings = CompanySettings.objects.get(id=1)
        if party and party.is_within_state:
            gst_rate = (settings.cgst or 0) + (settings.sgst or 0)
        else:
            gst_rate = settings.igst or 0

        # Calculate unit price (exclude GST if is_gst_included)
        unit_price = order.unit_price
        if order.is_gst_included and order.unit_price and gst_rate:
            unit_price = round(order.unit_price / (1 + gst_rate / 100), 2)

        sales = Sales(
            sales_sequence=seq,
            order_no=order.order_number or f"{order.twine}-{seq}",
            sales_entry_date=now.strftime('%Y-%m-%d'),
            customer=order.customer or "",
            twine=order.twine or "",
            speification=spec_text,
            colour=spec.colour if spec else "White",
            piece_weight=spec.piece_weight if spec else "",
            piece_count=spec.no_of_pcs if spec else None,
            unit_price=unit_price,
            gst_rate=gst_rate,
            status='ON_HOLD_PROCESSING',
        )
        sales.save()
        created_count += 1


def copy_orders_to_sales(request):
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            order_keys = data.get('order_keys', [])
        except (json.JSONDecodeError, TypeError):
            order_keys = request.POST.getlist('order_keys')

        if not order_keys:
            messages.error(request, "No orders selected.")
            return redirect('order_entry')

        copied_count = 0
        for ok in order_keys:
            try:
                order = Order.objects.prefetch_related('specifications').get(order_key=ok)
            except Order.DoesNotExist:
                continue

            specs = order.specifications.all()
            if not specs:
                continue

            # Generate base sequence from max existing sales_sequence
            base_seq = (Sales.objects.aggregate(max_seq=Max('sales_sequence'))['max_seq'] or 0) + 1

            for index, spec in enumerate(specs, start=1):
                seq = base_seq + index - 1

                mesh_size = spec.mesh_size if spec else ''
                mesh_depth = spec.mesh_depth if spec else ''
                salvage = spec.salvage if spec else ''
                md_disp = mesh_depth if mesh_depth and 'MD' in mesh_depth.upper() else (mesh_depth + 'MD' if mesh_depth else '')
                sal_disp = salvage if salvage and 'SEL' in salvage.upper() else (salvage + 'Sel' if salvage else '')
                spec_text = f"{mesh_size}MM-{md_disp}-{sal_disp}" if mesh_size or md_disp or sal_disp else ""

                now = datetime.now()

                party = Parties.objects.filter(code=order.customer).first()
                settings = CompanySettings.objects.get(id=1)
                if party and party.is_within_state:
                    gst_rate = (settings.cgst or 0) + (settings.sgst or 0)
                else:
                    gst_rate = settings.igst or 0

                unit_price = order.unit_price
                if order.is_gst_included and order.unit_price and gst_rate:
                    unit_price = round(order.unit_price / (1 + gst_rate / 100), 2)

                sales = Sales(
                    sales_sequence=seq,
                    order_no=order.order_number or f"{order.twine}-{seq}",
                    sales_entry_date=now.strftime('%Y-%m-%d'),
                    customer=order.customer or "",
                    twine=order.twine or "",
                    speification=spec_text,
                    colour=spec.colour if spec else "White",
                    piece_weight=spec.piece_weight if spec else "",
                    piece_count=spec.no_of_pcs if spec else None,
                    unit_price=unit_price,
                    gst_rate=gst_rate,
                    status='ON_HOLD_PROCESSING',
                )
                sales.save()
                copied_count += 1

        messages.success(request, f"{copied_count} order(s) copied to Sales successfully.")
    return redirect('order_entry')


def purchase_entry(request):
    purchases = Purchase.objects.all()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "delete":
            pk = request.POST.get("purchase_key")
            if pk:
                Purchase.objects.filter(purchase_key=pk).delete()
                messages.success(request, "Purchase deleted successfully.")
            return redirect('purchase_entry')

        drafts_raw = request.POST.get("drafts_data")
        saved_count = 0
        if drafts_raw:
            try:
                entries = json.loads(drafts_raw)
                if not isinstance(entries, list):
                    entries = []
            except json.JSONDecodeError:
                entries = []

            for entry in entries:
                vendor = (entry.get("vendor") or "").strip()
                if not vendor:
                    continue

                subtotal = entry.get("subtotal") or 0
                gst_percent = entry.get("gst_percent") or 0
                gst_amount = entry.get("gst_amount") or 0
                total_amount = entry.get("total_amount") or 0
                amount_paid = entry.get("amount_paid") or 0
                try:
                    subtotal = float(subtotal)
                    gst_percent = float(gst_percent)
                    gst_amount = float(gst_amount)
                    total_amount = float(total_amount)
                    amount_paid = float(amount_paid)
                except (ValueError, TypeError):
                    subtotal = gst_amount = total_amount = amount_paid = 0

                balance = total_amount - amount_paid
                payment_status = entry.get("payment_status") or "PENDING"
                if total_amount > 0 and amount_paid >= total_amount:
                    payment_status = "PAID"
                elif amount_paid > 0:
                    payment_status = "PARTIALLY_PAID"

                purchase_key = entry.get("purchase_key") or ""
                if purchase_key:
                    Purchase.objects.filter(purchase_key=purchase_key).update(
                        invoice_no=entry.get("invoice_no") or "",
                        delivery_date=entry.get("delivery_date") or None,
                        payment_date=entry.get("payment_date") or None,
                        vendor=vendor,
                        is_twine=entry.get("is_twine") in (True, "True", "true", "on"),
                        material=entry.get("material") or "",
                        material_code=entry.get("material_code") or "",
                        order_description=entry.get("order_description") or "",
                        quantity_weight=entry.get("quantity_weight") or None,
                        unit=entry.get("unit") or "KG",
                        unit_price=entry.get("unit_price") or None,
                        subtotal=subtotal,
                        gst_percent=gst_percent,
                        gst_amount=gst_amount,
                        total_amount=total_amount,
                        amount_paid=amount_paid,
                        payment_status=payment_status,
                        balance=balance,
                        comments=entry.get("comments") or "",
                    )
                else:
                    Purchase.objects.create(
                        invoice_no=entry.get("invoice_no") or "",
                        delivery_date=entry.get("delivery_date") or None,
                        payment_date=entry.get("payment_date") or None,
                        vendor=vendor,
                        is_twine=entry.get("is_twine") in (True, "True", "true", "on"),
                        material=entry.get("material") or "",
                        material_code=entry.get("material_code") or "",
                        order_description=entry.get("order_description") or "",
                        quantity_weight=entry.get("quantity_weight") or None,
                        unit=entry.get("unit") or "KG",
                        unit_price=entry.get("unit_price") or None,
                        subtotal=subtotal,
                        gst_percent=gst_percent,
                        gst_amount=gst_amount,
                        total_amount=total_amount,
                        amount_paid=amount_paid,
                        payment_status=payment_status,
                        balance=balance,
                        comments=entry.get("comments") or "",
                    )
                saved_count += 1

        if saved_count:
            messages.success(request, f'{saved_count} purchase(s) saved successfully.')
        return redirect('purchase_entry')

    parties = Parties.objects.all()
    materials = Materials.objects.all()
    materials_list = list(Purchase.objects.exclude(material__isnull=True).exclude(material='').values_list('material', flat=True).distinct().order_by('material'))
    purchases_json = json.dumps(list(purchases.values(
        'purchase_key', 'invoice_no', 'delivery_date', 'payment_date', 'vendor',
        'is_twine', 'material', 'material_code', 'order_description', 'quantity_weight', 'unit',
        'unit_price', 'subtotal', 'gst_percent', 'gst_amount', 'total_amount',
        'amount_paid', 'payment_status', 'balance', 'comments',
    )), default=str)

    context = {
        "purchases": purchases,
        "purchases_json": purchases_json,
        "parties": parties,
        "materials": materials,
        "materials_list": materials_list,
    }
    return render(request, "marania_invoice_app/purchase_entry.html", context)


def payment_receipt_entry(request):
    receipts = PaymentReceipt.objects.all()
    parties = Parties.objects.all()
    invoices = Invoice.objects.all()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "delete":
            pk = request.POST.get("payment_id")
            if pk:
                PaymentReceipt.objects.filter(payment_id=pk).delete()
                messages.success(request, "Payment receipt deleted.")
            return redirect('payment_receipt_entry')

        drafts_raw = request.POST.get("drafts_data")
        if not drafts_raw and request.content_type == 'application/json':
            try:
                body = json.loads(request.body)
                drafts_raw = body.get('drafts_data')
            except (json.JSONDecodeError, AttributeError):
                drafts_raw = None

        saved_count = 0
        if drafts_raw:
            if isinstance(drafts_raw, str):
                try:
                    entries = json.loads(drafts_raw)
                    if not isinstance(entries, list):
                        entries = []
                except json.JSONDecodeError:
                    entries = []
            else:
                entries = drafts_raw if isinstance(drafts_raw, list) else []

            now = datetime.now()
            today_str = now.strftime('%Y%m%d')
            base = f'RCPT-{today_str}-'
            batch_seq = 0
            for entry in entries:
                customer = (entry.get("customer") or "").strip()
                if not customer:
                    continue

                pk = entry.get("payment_id")
                if pk is not None:
                    pk = str(pk).strip()
                else:
                    pk = ""
                is_update = bool(pk)

                if is_update:
                    try:
                        obj = PaymentReceipt.objects.get(payment_id=pk)
                    except PaymentReceipt.DoesNotExist:
                        obj = PaymentReceipt()
                else:
                    obj = PaymentReceipt()

                # Always generate receipt_no server-side for new records
                if is_update and (entry.get("receipt_no") or "").strip():
                    obj.receipt_no = entry.get("receipt_no").strip()
                else:
                    if batch_seq == 0:
                        existing = PaymentReceipt.objects.filter(
                            receipt_no__startswith=base
                        ).values_list('receipt_no', flat=True)
                        for r in existing:
                            parts = r.split('-')
                            try:
                                seq = int(parts[-1])
                                if seq > batch_seq:
                                    batch_seq = seq
                            except (ValueError, IndexError):
                                pass
                    batch_seq += 1
                    obj.receipt_no = base + str(batch_seq).zfill(3)
                party_code = customer.split('-')[0] if '-' in customer else customer
                party = Parties.objects.filter(code=party_code).first()
                if party:
                    obj.customer = party
                obj.payment_date = parse_date(entry.get("payment_date")) or now.strftime('%Y-%m-%d')
                obj.total_received = entry.get("total_received") or 0
                obj.transaction_type = entry.get("transaction_type") or "Payment"
                obj.payment_mode = entry.get("payment_mode") or "Cash"
                obj.reference_no = entry.get("reference_no") or ""
                obj.allocation_status = entry.get("allocation_status") or "Unallocated"
                obj.remarks = entry.get("remarks") or ""
                obj.display_comment = entry.get("display_comment") or ""
                obj.updated_at = now
                # Retry save with incremented seq on unique constraint collision
                for _ in range(3):
                    try:
                        obj.save()
                        break
                    except IntegrityError as e:
                        if not is_update and 'receipt_no' in str(e):
                            batch_seq += 1
                            obj.receipt_no = base + str(batch_seq).zfill(3)
                            continue
                        raise
                saved_count += 1

            if saved_count:
                messages.success(request, f"{saved_count} receipt(s) saved successfully.")
        else:
            messages.error(request, "No receipt data received.")

        if request.content_type == 'application/json':
            return JsonResponse({'saved_count': saved_count})
        return redirect('payment_receipt_entry')

    receipts_json = []
    for r in receipts:
        receipts_json.append({
            'payment_id': r.payment_id,
            'receipt_no': r.receipt_no or '',
            'customer': str(r.customer) if r.customer else '',
            'customer_code': r.customer.code if r.customer else '',
            'payment_date': str(r.payment_date) if r.payment_date else '',
            'total_received': str(r.total_received) if r.total_received else '',
            'transaction_type': r.transaction_type or 'Payment',
            'payment_mode': r.payment_mode or '',
            'reference_no': r.reference_no or '',
            'allocation_status': r.allocation_status or 'Unallocated',
            'remarks': r.remarks or '',
            'display_comment': r.display_comment or '',
        })

    # Compute outstanding balance per customer
    from django.db.models import Sum, Q
    customer_balance = {}
    for p in parties:
        code = p.code

        # Opening balance: Dr amounts - Cr amounts, minus allocations against OBs
        ob_dr = OpeningBalance.objects.filter(customer__code=code, balance_type='Debit').aggregate(total=Sum('amount'))['total'] or 0
        ob_cr = OpeningBalance.objects.filter(customer__code=code, balance_type='Credit').aggregate(total=Sum('amount'))['total'] or 0
        ob_alloc = PaymentAllocation.objects.filter(
            opening_balance__customer__code=code
        ).aggregate(total=Sum('allocated_amount'))['total'] or 0
        ob_net = float(ob_dr) - float(ob_cr) - float(ob_alloc)

        # Invoices: gross_total minus allocations against invoices
        inv_total = Invoice.objects.filter(customer_code=code).aggregate(
            total=Sum('gross_total'))['total'] or 0
        inv_alloc = PaymentAllocation.objects.filter(
            invoice__customer_code=code
        ).aggregate(total=Sum('allocated_amount'))['total'] or 0
        inv_net = float(inv_total) - float(inv_alloc)

        # Expenses billed to customer: expense_amount minus allocations
        exp_total = 0
        exp_alloc = 0
        for exp in Expense.objects.filter(bill_to='Customer'):
            vendor = exp.vendor or ''
            if vendor and vendor != 'Not Applicable':
                exp_code = vendor.split('-')[0].strip()
                if exp_code == code:
                    exp_total += float(exp.expense_amount)
                    exp_alloc += float(PaymentAllocation.objects.filter(
                        expense=exp
                    ).aggregate(total=Sum('allocated_amount'))['total'] or 0)
        exp_net = exp_total - exp_alloc

        # Settlement invoices: amount minus allocations
        si_total = 0
        si_alloc = 0
        for si in SettlementInvoice.objects.filter(customer__code=code):
            si_total += float(si.amount)
            si_alloc += float(PaymentAllocation.objects.filter(
                settlement_invoice=si
            ).aggregate(total=Sum('allocated_amount'))['total'] or 0)
        si_net = si_total - si_alloc

        # Unallocated payment receipts (payments + adjustments not yet applied)
        unalloc_payments = 0
        for receipt in PaymentReceipt.objects.filter(customer__code=code):
            r_alloc = PaymentAllocation.objects.filter(
                payment=receipt
            ).aggregate(total=Sum('allocated_amount'))['total'] or 0
            available = float(receipt.total_received) - float(r_alloc)
            if available > 0:
                ttype = receipt.transaction_type or 'Payment'
                if ttype == 'Adjustment(Dr)':
                    unalloc_payments -= available
                else:
                    unalloc_payments += available

        balance = ob_net + inv_net + exp_net + si_net - unalloc_payments
        customer_balance[code] = round(balance, 2)

    return render(request, 'marania_invoice_app/payment_receipt_entry.html', {
        'receipts': receipts,
        'receipts_json': json.dumps(receipts_json),
        'parties': parties,
        'customer_balance_json': json.dumps(customer_balance),
    })


def payment_allocation_entry(request):
    parties = Parties.objects.all()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "delete":
            pk = request.POST.get("allocation_id")
            if pk:
                alloc = PaymentAllocation.objects.filter(allocation_id=pk).first()
                if alloc:
                    invoice = alloc.invoice
                    expense_obj = alloc.expense
                    ob = alloc.opening_balance
                    si_obj = alloc.settlement_invoice
                    alloc.delete()
                    if invoice:
                        update_invoice_payment_status(invoice)
                    if expense_obj:
                        update_expense_payment_status(expense_obj)
                    if si_obj:
                        update_settlement_invoice_status(si_obj)
                messages.success(request, "Payment allocation deleted.")
            return redirect('payment_allocation_entry')

        if action == "save_allocations":
            payment_ids_str = request.POST.get("payment_ids", "")
            allocation_date = request.POST.get("allocation_date")
            remarks = request.POST.get("remarks", "")
            invoice_nos = request.POST.getlist("invoice_number[]")
            alloc_amts = request.POST.getlist("allocated_amount[]")

            payment_ids = [pid.strip() for pid in payment_ids_str.split(",") if pid.strip()]
            if not payment_ids:
                messages.error(request, "No payment receipts selected.")
                return redirect('payment_allocation_entry')

            receipts = PaymentReceipt.objects.filter(payment_id__in=payment_ids).order_by('payment_date')
            if not receipts.exists():
                messages.error(request, "Payment receipts not found.")
                return redirect('payment_allocation_entry')

            # Build available balance per receipt
            receipt_avail = {}
            for r in receipts:
                total_alloc = PaymentAllocation.objects.filter(
                    payment=r
                ).aggregate(total=Sum('allocated_amount'))['total'] or 0
                avail = r.total_received - total_alloc
                if avail > 0:
                    receipt_avail[r.payment_id] = avail

            if not receipt_avail:
                messages.warning(request, "Selected receipts have no available balance.")
                return redirect('payment_allocation_entry')

            now = datetime.now()
            sorted_pids = sorted(receipt_avail.keys())
            saved = 0
            affected_invoices = set()
            affected_expenses = set()
            affected_obs = set()
            affected_sis = set()

            for i, inv_no in enumerate(invoice_nos):
                amt_str = alloc_amts[i] if i < len(alloc_amts) else ""
                if not amt_str:
                    continue
                try:
                    amt = Decimal(str(amt_str))
                except Exception:
                    continue
                if amt <= 0:
                    continue

                remaining_amt = amt

                # Determine if this is an opening balance, expense, or invoice
                if inv_no.startswith('OBAL-'):
                    ob_id = inv_no.replace('OBAL-', '')
                    ob_obj = OpeningBalance.objects.filter(opening_balance_id=ob_id).first()
                    if not ob_obj:
                        continue
                    affected_obs.add(ob_obj)
                    target_invoice = None
                    target_expense = None
                    target_ob = ob_obj
                    target_si = None
                elif inv_no.startswith('EXP-'):
                    exp_id = inv_no.replace('EXP-', '')
                    expense_obj = Expense.objects.filter(expense_id=exp_id).first()
                    if not expense_obj:
                        continue
                    affected_expenses.add(expense_obj)
                    target_invoice = None
                    target_expense = expense_obj
                    target_ob = None
                    target_si = None
                elif inv_no.startswith('SI-'):
                    si_id = inv_no.replace('SI-', '')
                    si_obj = SettlementInvoice.objects.filter(settlement_id=si_id).first()
                    if not si_obj:
                        continue
                    affected_sis.add(si_obj)
                    target_invoice = None
                    target_expense = None
                    target_ob = None
                    target_si = si_obj
                else:
                    invoice_obj = Invoice.objects.filter(invoice_number=inv_no).first()
                    if not invoice_obj:
                        continue
                    affected_invoices.add(invoice_obj)
                    target_invoice = invoice_obj
                    target_expense = None
                    target_ob = None
                    target_si = None

                # Allocate from receipts in order
                for pid in sorted_pids:
                    if remaining_amt <= 0:
                        break
                    avail = receipt_avail[pid]
                    if avail <= 0:
                        continue
                    take = min(remaining_amt, avail)
                    receipt_obj = PaymentReceipt.objects.get(payment_id=pid)

                    filter_kwargs = {'payment': receipt_obj}
                    if target_ob:
                        filter_kwargs['opening_balance'] = target_ob
                        filter_kwargs['invoice__isnull'] = True
                        filter_kwargs['expense__isnull'] = True
                        filter_kwargs['settlement_invoice__isnull'] = True
                    elif target_expense:
                        filter_kwargs['expense'] = target_expense
                        filter_kwargs['invoice__isnull'] = True
                        filter_kwargs['opening_balance__isnull'] = True
                        filter_kwargs['settlement_invoice__isnull'] = True
                    elif target_si:
                        filter_kwargs['settlement_invoice'] = target_si
                        filter_kwargs['invoice__isnull'] = True
                        filter_kwargs['expense__isnull'] = True
                        filter_kwargs['opening_balance__isnull'] = True
                    else:
                        filter_kwargs['invoice'] = target_invoice
                        filter_kwargs['expense__isnull'] = True
                        filter_kwargs['opening_balance__isnull'] = True
                        filter_kwargs['settlement_invoice__isnull'] = True

                    # Use filter-based get_or_create since nullable FKs
                    existing = PaymentAllocation.objects.filter(**filter_kwargs).first()
                    if existing:
                        alloc = existing
                        alloc.allocated_amount = (alloc.allocated_amount or 0) + take
                        alloc.allocation_date = parse_date(allocation_date) or now.strftime('%Y-%m-%d')
                    else:
                        alloc = PaymentAllocation(
                            payment=receipt_obj,
                            invoice=target_invoice,
                            expense=target_expense,
                            opening_balance=target_ob,
                            settlement_invoice=target_si,
                            allocated_amount=take,
                            allocation_date=parse_date(allocation_date) or now.strftime('%Y-%m-%d'),
                        )
                    alloc.remarks = remarks
                    alloc.updated_at = now
                    alloc.save()

                    receipt_avail[pid] -= take
                    remaining_amt -= take
                    saved += 1

            # Update allocation_status for all involved receipts
            for r in receipts:
                total_alloc = PaymentAllocation.objects.filter(
                    payment=r
                ).aggregate(total=Sum('allocated_amount'))['total'] or 0
                if total_alloc >= r.total_received:
                    r.allocation_status = 'Fully Allocated'
                elif total_alloc > 0:
                    r.allocation_status = 'Partially Allocated'
                else:
                    r.allocation_status = 'Unallocated'
                r.save()

            # Update payment_status for all affected invoices
            for inv in affected_invoices:
                update_invoice_payment_status(inv)
            for exp in affected_expenses:
                update_expense_payment_status(exp)
            for si in affected_sis:
                update_settlement_invoice_status(si)
            # Update opening balance amount to 0 if fully paid
            for ob in affected_obs:
                total_alloc = PaymentAllocation.objects.filter(
                    opening_balance=ob
                ).aggregate(total=Sum('allocated_amount'))['total'] or 0
                if total_alloc >= ob.amount:
                    ob.amount = 0
                    ob.save()

            if saved:
                messages.success(request, f"{saved} allocation(s) saved.")
            else:
                messages.warning(request, "No allocations to save.")
            return redirect('payment_allocation_entry')

    # GET: build split-panel data
    payments_qs = PaymentReceipt.objects.all()
    payment_data = []
    for p in payments_qs:
        total_alloc = PaymentAllocation.objects.filter(
            payment=p
        ).aggregate(total=Sum('allocated_amount'))['total'] or 0
        available = p.total_received - total_alloc
        if available > 0:
            ttype = p.transaction_type or 'Payment'
            prefix = ''
            if ttype == 'Adjustment(Cr)':
                prefix = 'Adj(Cr) '
            elif ttype == 'Adjustment(Dr)':
                prefix = 'Adj(Dr) '
            payment_data.append({
                'payment_id': p.payment_id,
                'receipt_no': p.receipt_no or '',
                'payment_date': str(p.payment_date) if p.payment_date else '',
                'customer': str(p.customer) if p.customer else '',
                'customer_code': p.customer.code if p.customer else '',
                'total_received': str(p.total_received),
                'available': str(available),
                'transaction_type': ttype,
                'display_label': prefix + (p.receipt_no or ''),
                'display_comment': p.display_comment or '',
            })

    invoice_data = []

    # Opening balances first (top of right panel)
    ob_qs = OpeningBalance.objects.all()
    for ob in ob_qs:
        total_alloc = PaymentAllocation.objects.filter(
            opening_balance=ob
        ).aggregate(total=Sum('allocated_amount'))['total'] or 0
        balance = ob.amount - total_alloc
        if balance > 0:
            ob_num = ob.ob_number or f"OBAL-{ob.opening_balance_id}"
            customer_code = ob.customer.code if ob.customer else ''
            invoice_data.append({
                'invoice_number': f'OBAL-{ob.opening_balance_id}',
                'invoice_date': str(ob.opening_date) if ob.opening_date else '',
                'customer_code': customer_code,
                'gross_total': str(ob.amount),
                'balance': str(balance),
                'type': 'opening_balance',
                'ob_id': ob.opening_balance_id,
                'ob_number': ob_num,
                'display_comment': ob.display_comment or '',
            })

    # Then invoices
    invoices_qs = Invoice.objects.all()
    for inv in invoices_qs:
        total_alloc = PaymentAllocation.objects.filter(
            invoice=inv
        ).aggregate(total=Sum('allocated_amount'))['total'] or 0
        balance = inv.gross_total - total_alloc
        if balance > 0:
            invoice_data.append({
                'invoice_number': inv.invoice_number or '',
                'invoice_date': str(inv.invoice_date) if inv.invoice_date else '',
                'customer_code': inv.customer_code or '',
                'gross_total': str(inv.gross_total),
                'balance': str(balance),
                'type': 'invoice',
            })

    # Then customer expenses (bill_to=Customer) with outstanding balance
    expense_qs = Expense.objects.filter(bill_to='Customer')
    for e in expense_qs:
        total_alloc = PaymentAllocation.objects.filter(
            expense=e
        ).aggregate(total=Sum('allocated_amount'))['total'] or 0
        balance = e.expense_amount - total_alloc
        if balance > 0:
            vendor = e.vendor or ''
            customer_code = ''
            if vendor and vendor != 'Not Applicable':
                customer_code = vendor.split('-')[0].strip()
            invoice_data.append({
                'invoice_number': f'EXP-{e.expense_id}',
                'invoice_date': str(e.expense_date) if e.expense_date else '',
                'customer_code': customer_code,
                'gross_total': str(e.expense_amount),
                'balance': str(balance),
                'type': 'expense',
                'expense_id': e.expense_id,
                'expense_category': e.expense_category or '',
                'display_comment': e.display_comment or '',
            })

    # Then settlement invoices with outstanding balance
    si_qs = SettlementInvoice.objects.all()
    for si in si_qs:
        total_alloc = PaymentAllocation.objects.filter(
            settlement_invoice=si
        ).aggregate(total=Sum('allocated_amount'))['total'] or 0
        balance = si.amount - total_alloc
        if balance > 0:
            customer_code = si.customer.code if si.customer else ''
            invoice_data.append({
                'invoice_number': f'SI-{si.settlement_id}',
                'invoice_date': str(si.settlement_date) if si.settlement_date else '',
                'customer_code': customer_code,
                'gross_total': str(si.amount),
                'balance': str(balance),
                'type': 'settlement_invoice',
                'settlement_id': si.settlement_id,
                'settlement_invoice_number': si.settlement_invoice_number or '',
                'description': si.description or '',
                'display_comment': si.display_comment or '',
            })

    # Existing allocations for reference
    existing_allocations = PaymentAllocation.objects.select_related('payment', 'invoice', 'expense', 'opening_balance', 'settlement_invoice').all()

    # Build outstanding summary per customer (only unallocated items)
    balance_history = {}
    for party in parties:
        code = party.code
        entries = []

        # Opening balances with outstanding balance > 0
        for ob in OpeningBalance.objects.filter(customer__code=code):
            alloc_total = PaymentAllocation.objects.filter(
                opening_balance=ob
            ).aggregate(total=Sum('allocated_amount'))['total'] or 0
            balance = float(ob.amount) - float(alloc_total)
            if balance > 0:
                dr_cr = 'Dr' if ob.balance_type == 'Debit' else 'Cr'
                comment = ob.display_comment or ''
                desc = 'Opening Balance'
                if comment:
                    desc += f' ({comment})'
                entries.append({
                    'entry_date': str(ob.opening_date),
                    'description': desc,
                    'type': dr_cr,
                    'amount': balance,
                })

        # Unpaid invoices (balance > 0)
        for inv in Invoice.objects.filter(customer_code=code):
            alloc_total = PaymentAllocation.objects.filter(
                invoice=inv
            ).aggregate(total=Sum('allocated_amount'))['total'] or 0
            balance = float(inv.gross_total) - float(alloc_total)
            if balance > 0:
                entries.append({
                    'entry_date': str(inv.invoice_date) if inv.invoice_date else '',
                    'description': 'Invoice issued',
                    'type': 'Dr',
                    'amount': balance,
                })

        # Customer expenses with outstanding balance > 0
        for exp in Expense.objects.filter(bill_to='Customer'):
            vendor = exp.vendor or ''
            if vendor and vendor != 'Not Applicable':
                exp_code = vendor.split('-')[0].strip()
                if exp_code == code:
                    alloc_total = PaymentAllocation.objects.filter(
                        expense=exp
                    ).aggregate(total=Sum('allocated_amount'))['total'] or 0
                    balance = float(exp.expense_amount) - float(alloc_total)
                    if balance > 0:
                        comment = exp.display_comment or ''
                        desc = exp.expense_category or 'Expense'
                        if comment:
                            desc += f' ({comment})'
                        entries.append({
                            'entry_date': str(exp.expense_date) if exp.expense_date else '',
                            'description': desc,
                            'type': 'Dr',
                            'amount': balance,
                        })

        # Settlement invoices with outstanding balance > 0
        for si in SettlementInvoice.objects.filter(customer__code=code):
            alloc_total = PaymentAllocation.objects.filter(
                settlement_invoice=si
            ).aggregate(total=Sum('allocated_amount'))['total'] or 0
            balance = float(si.amount) - float(alloc_total)
            if balance > 0:
                desc = 'SI'
                comment = si.display_comment or ''
                if comment:
                    desc += f' ({comment})'
                entries.append({
                    'entry_date': str(si.settlement_date) if si.settlement_date else '',
                    'invoice_ref': si.settlement_invoice_number or '',
                    'description': desc,
                    'type': 'Dr',
                    'amount': balance,
                })

        # Unallocated payment receipts (available balance > 0)
        for receipt in PaymentReceipt.objects.filter(customer__code=code):
            alloc_total = PaymentAllocation.objects.filter(
                payment=receipt
            ).aggregate(total=Sum('allocated_amount'))['total'] or 0
            available = float(receipt.total_received) - float(alloc_total)
            if available > 0:
                ttype = receipt.transaction_type or 'Payment'
                comment = receipt.display_comment or ''
                if ttype == 'Payment':
                    desc = 'Payment Received'
                    entry_type = 'Cr'
                elif ttype == 'Adjustment(Cr)':
                    desc = 'Payment Adjustment(Cr)'
                    entry_type = 'Cr'
                elif ttype == 'Adjustment(Dr)':
                    desc = 'Payment Adjustment(Dr)'
                    entry_type = 'Dr'
                else:
                    desc = 'Received Payment'
                    entry_type = 'Cr'
                if comment:
                    desc += f' ({comment})'
                entries.append({
                    'entry_date': str(receipt.payment_date) if receipt.payment_date else '',
                    'description': desc,
                    'type': entry_type,
                    'amount': available,
                })

        # Sort by date
        entries.sort(key=lambda e: e['entry_date'])

        # Compute running balance
        running = 0.0
        for e in entries:
            if e['type'] == 'Dr':
                running += e['amount']
            else:
                running -= e['amount']
            e['running_balance'] = round(running, 2)
            e['amount'] = round(e['amount'], 2)

        balance_history[code.lower()] = entries

    return render(request, 'marania_invoice_app/payment_allocation_entry.html', {
        'parties': parties,
        'payment_data_json': json.dumps(payment_data),
        'invoice_data_json': json.dumps(invoice_data),
        'existing_allocations': existing_allocations,
        'balance_history_json': json.dumps(balance_history, default=str),
    })


def opening_balance_entry(request):
    balances = OpeningBalance.objects.all()
    parties = Parties.objects.all()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "delete":
            pk = request.POST.get("opening_balance_id")
            if pk:
                OpeningBalance.objects.filter(opening_balance_id=pk).delete()
                messages.success(request, "Opening balance deleted.")
            return redirect('opening_balance_entry')

        drafts_raw = request.POST.get("drafts_data")
        if not drafts_raw and request.content_type == 'application/json':
            try:
                body = json.loads(request.body)
                drafts_raw = body.get('drafts_data')
            except (json.JSONDecodeError, AttributeError):
                drafts_raw = None

        saved_count = 0
        if drafts_raw:
            if isinstance(drafts_raw, str):
                try:
                    entries = json.loads(drafts_raw)
                    if not isinstance(entries, list):
                        entries = []
                except json.JSONDecodeError:
                    entries = []
            else:
                entries = drafts_raw if isinstance(drafts_raw, list) else []

            now = datetime.now()
            last_created_id = None
            for entry in entries:
                pk = entry.get("opening_balance_id")
                if pk is not None:
                    pk = str(pk).strip()
                else:
                    pk = ""
                is_update = bool(pk)

                if is_update:
                    try:
                        obj = OpeningBalance.objects.get(opening_balance_id=pk)
                    except OpeningBalance.DoesNotExist:
                        obj = OpeningBalance()
                else:
                    obj = OpeningBalance()

                obj.opening_date = parse_date(entry.get("opening_date")) or now.strftime('%Y-%m-%d')
                customer_val = entry.get("customer") or ""
                if customer_val:
                    party_code = customer_val.split('-')[0] if '-' in customer_val else customer_val
                    party = Parties.objects.filter(code=party_code).first()
                    if party:
                        obj.customer = party
                obj.amount = entry.get("amount") or 0
                obj.balance_type = entry.get("balance_type") or 'Debit'
                obj.reference_no = entry.get("reference_no") or ""
                obj.remarks = entry.get("remarks") or ""
                obj.display_comment = entry.get("display_comment") or ""
                obj.status = entry.get("status") or "Draft"
                obj.updated_at = now
                obj.save()
                # Generate ob_number for new records
                if not is_update and not obj.ob_number:
                    date_str = str(obj.opening_date) if obj.opening_date else now.strftime('%Y%m%d')
                    date_prefix = date_str.replace('-', '')
                    obj.ob_number = f"OB-{date_prefix}-{obj.opening_balance_id}"
                    obj.save(update_fields=['ob_number'])
                last_created_id = obj.opening_balance_id
                saved_count += 1

            if saved_count:
                msg = f"{saved_count} opening balance(s) saved successfully."
                if last_created_id:
                    obj = OpeningBalance.objects.filter(opening_balance_id=last_created_id).first()
                    if obj and obj.ob_number:
                        msg += f" OB Number: {obj.ob_number}"
                messages.success(request, msg)
        else:
            messages.error(request, "No opening balance data received.")

        if request.content_type == 'application/json':
            return JsonResponse({'saved_count': saved_count})
        url = reverse('opening_balance_entry')
        if last_created_id:
            obj = OpeningBalance.objects.filter(opening_balance_id=last_created_id).first()
            ob_num = obj.ob_number if obj else ''
            url += f'?created={last_created_id}&ob_number={ob_num}'
        return redirect(url)

    balances_json = []
    for b in balances:
        balances_json.append({
            'opening_balance_id': b.opening_balance_id,
            'ob_number': b.ob_number or '',
            'opening_date': str(b.opening_date) if b.opening_date else '',
            'customer': str(b.customer) if b.customer else '',
            'amount': str(b.amount) if b.amount else '',
            'balance_type': b.balance_type or 'Debit',
            'reference_no': b.reference_no or '',
            'remarks': b.remarks or '',
            'display_comment': b.display_comment or '',
            'status': b.status or 'Draft',
        })

    return render(request, 'marania_invoice_app/opening_balance_entry.html', {
        'balances': balances,
        'balances_json': json.dumps(balances_json),
        'parties': parties,
    })


def expense_entry(request):
    from datetime import date
    expenses = Expense.objects.all()
    parties = Parties.objects.all()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "delete":
            pk = request.POST.get("expense_id")
            if pk:
                Expense.objects.filter(expense_id=pk).delete()
                messages.success(request, "Expense deleted.")
            return redirect('expense_entry')

        drafts_raw = request.POST.get("drafts_data")
        if not drafts_raw and request.content_type == 'application/json':
            try:
                body = json.loads(request.body)
                drafts_raw = body.get('drafts_data')
            except (json.JSONDecodeError, AttributeError):
                drafts_raw = None

        saved_count = 0
        if drafts_raw:
            if isinstance(drafts_raw, str):
                try:
                    entries = json.loads(drafts_raw)
                    if not isinstance(entries, list):
                        entries = []
                except json.JSONDecodeError:
                    entries = []
            else:
                entries = drafts_raw if isinstance(drafts_raw, list) else []

            now = datetime.now()
            for entry in entries:
                pk = entry.get("expense_id")
                if pk is not None:
                    pk = str(pk).strip()
                else:
                    pk = ""
                is_update = bool(pk)

                if is_update:
                    try:
                        obj = Expense.objects.get(expense_id=pk)
                    except Expense.DoesNotExist:
                        obj = Expense()
                else:
                    obj = Expense()

                obj.expense_date = parse_date(entry.get("expense_date")) or now.strftime('%Y-%m-%d')
                obj.expense_category = entry.get("expense_category") or "Miscellaneous"
                obj.expense_amount = Decimal(str(entry.get("expense_amount") or 0))
                obj.description = entry.get("description") or ""
                obj.display_comment = entry.get("display_comment") or ""
                obj.payment_method = entry.get("payment_method") or "Cash"
                obj.vendor = entry.get("vendor") or ""
                obj.amount_paid = Decimal(str(entry.get("amount_paid") or 0))
                obj.balance_amount = obj.expense_amount - obj.amount_paid
                if obj.balance_amount <= 0:
                    obj.payment_status = 'Paid'
                elif obj.amount_paid > 0:
                    obj.payment_status = 'Partially Paid'
                else:
                    obj.payment_status = 'Pending'
                obj.bill_to = entry.get("bill_to") or "Company"
                obj.updated_at = now
                obj.save()
                saved_count += 1

            if saved_count:
                messages.success(request, f"{saved_count} expense(s) saved successfully.")
        else:
            messages.error(request, "No expense data received.")

        if request.content_type == 'application/json':
            return JsonResponse({'saved_count': saved_count})
        return redirect('expense_entry')

    expenses_json = []
    for e in expenses:
        expenses_json.append({
            'expense_id': e.expense_id,
            'expense_date': str(e.expense_date) if e.expense_date else '',
            'expense_category': e.expense_category or '',
            'expense_amount': str(e.expense_amount) if e.expense_amount else '',
            'description': e.description or '',
            'display_comment': e.display_comment or '',
            'payment_method': e.payment_method or '',
            'vendor': e.vendor or '',
            'amount_paid': str(e.amount_paid) if e.amount_paid else '',
            'balance_amount': str(e.balance_amount) if e.balance_amount else '',
            'payment_status': e.payment_status or 'Pending',
            'bill_to': e.bill_to or 'Company',
        })

    return render(request, 'marania_invoice_app/expense_entry.html', {
        'expenses': expenses,
        'expenses_json': json.dumps(expenses_json),
        'parties': parties,
    })


def settlement_invoice_entry(request):
    from datetime import date
    settlements = SettlementInvoice.objects.all()
    parties = Parties.objects.all()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "delete":
            pk = request.POST.get("settlement_id")
            if pk:
                SettlementInvoice.objects.filter(settlement_id=pk).delete()
                messages.success(request, "Settlement invoice deleted.")
            return redirect('settlement_invoice_entry')

        drafts_raw = request.POST.get("drafts_data")
        if not drafts_raw and request.content_type == 'application/json':
            try:
                body = json.loads(request.body)
                drafts_raw = body.get('drafts_data')
            except (json.JSONDecodeError, AttributeError):
                drafts_raw = None

        saved_count = 0
        if drafts_raw:
            if isinstance(drafts_raw, str):
                try:
                    entries = json.loads(drafts_raw)
                    if not isinstance(entries, list):
                        entries = []
                except json.JSONDecodeError:
                    entries = []
            else:
                entries = drafts_raw if isinstance(drafts_raw, list) else []

            now = datetime.now()
            for entry in entries:
                pk = entry.get("settlement_id")
                if pk is not None:
                    pk = str(pk).strip()
                else:
                    pk = ""
                is_update = bool(pk)

                if is_update:
                    try:
                        obj = SettlementInvoice.objects.get(settlement_id=pk)
                    except SettlementInvoice.DoesNotExist:
                        obj = SettlementInvoice()
                else:
                    obj = SettlementInvoice()
                    obj.settlement_invoice_number = _generate_settlement_invoice_number()

                obj.settlement_date = parse_date(entry.get("settlement_date")) or now.strftime('%Y-%m-%d')
                customer_code = entry.get("customer_code") or ""
                if customer_code:
                    obj.customer = Parties.objects.filter(code=customer_code).first()
                obj.amount = Decimal(str(entry.get("amount") or 0))
                obj.description = entry.get("description") or ""
                obj.display_comment = entry.get("display_comment") or ""
                obj.status = entry.get("status") or "Pending"
                obj.updated_at = now
                obj.save()
                saved_count += 1

            if saved_count:
                messages.success(request, f"{saved_count} settlement invoice(s) saved successfully.")
        else:
            messages.error(request, "No settlement invoice data received.")

        if request.content_type == 'application/json':
            return JsonResponse({'saved_count': saved_count})
        return redirect('settlement_invoice_entry')

    settlements_json = []
    for s in settlements:
        settlements_json.append({
            'settlement_id': s.settlement_id,
            'settlement_invoice_number': s.settlement_invoice_number or '',
            'settlement_date': str(s.settlement_date) if s.settlement_date else '',
            'customer_code': s.customer.code if s.customer else '',
            'customer_name': s.customer.name if s.customer else '',
            'amount': str(s.amount) if s.amount else '',
            'description': s.description or '',
            'display_comment': s.display_comment or '',
            'status': s.status or 'Pending',
        })

    return render(request, 'marania_invoice_app/settlement_invoice_entry.html', {
        'settlements': settlements,
        'settlements_json': json.dumps(settlements_json),
        'parties': parties,
    })


def _generate_settlement_invoice_number():
    from datetime import date
    today = date.today()
    prefix = f"SI-{today.strftime('%Y%m')}-"
    last = SettlementInvoice.objects.filter(
        settlement_invoice_number__startswith=prefix
    ).order_by('-settlement_invoice_number').first()
    if last:
        last_num = int(last.settlement_invoice_number.split('-')[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    return f"{prefix}{new_num:04d}"


def profit_loss_entry(request):
    profit_losses = ProfitLoss.objects.all()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "delete":
            pk = request.POST.get("pl_key")
            if pk:
                ProfitLoss.objects.filter(pl_key=pk).delete()
                messages.success(request, "Profit/Loss entry deleted successfully.")
            return redirect("profit_loss_entry")

        if action == "generate":
            month_year_raw = request.POST.get("month_year") or ""
            month = None
            year = None
            if month_year_raw:
                try:
                    parts = month_year_raw.split("-")
                    year = int(parts[0])
                    month = int(parts[1])
                except (ValueError, IndexError, TypeError):
                    month = year = None

            sales_revenue = Decimal("0")
            other_income = Decimal("0")
            salary_expense = Decimal("0")
            purchase_expense = Decimal("0")
            other_expenses = Decimal("0")
            inhouse_material_value = Decimal("0")

            if month and year:
                sales_start = datetime(year, month, 1)
                if month == 12:
                    sales_end = datetime(year + 1, 1, 1)
                else:
                    sales_end = datetime(year, month + 1, 1)

                sales_qs = Sales.objects.filter(
                    sales_entry_date__gte=sales_start,
                    sales_entry_date__lt=sales_end,
                )

                sales_revenue = sales_qs.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

                salary_categories = ['Employee Salary', 'Mechanic Salary']
                expense_qs = Expense.objects.filter(
                    expense_date__gte=sales_start,
                    expense_date__lt=sales_end,
                    expense_category__in=salary_categories,
                )
                salary_expense = expense_qs.aggregate(total=Sum('expense_amount'))['total'] or Decimal('0')

                purchase_qs = Purchase.objects.filter(
                    delivery_date__gte=sales_start,
                    delivery_date__lt=sales_end,
                )
                purchase_expense = purchase_qs.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

                non_salary_categories = ['Miscellaneous', 'Electricity', 'Spare Parts', 'Transportation', 'Net Processing']
                other_qs = Expense.objects.filter(
                    expense_date__gte=sales_start,
                    expense_date__lt=sales_end,
                    expense_category__in=non_salary_categories,
                )
                other_expenses = other_qs.aggregate(total=Sum('expense_amount'))['total'] or Decimal('0')

                inhouse_material_value = purchase_expense

            pl_json = json.dumps([{
                "pl_key": "",
                "month": month,
                "year": year,
                "month_year": f"{year}-{month:02d}" if (year and month) else "",
                "sales_revenue": str(sales_revenue),
                "other_income": "0",
                "salary_expense": str(salary_expense),
                "purchase_expense": str(purchase_expense),
                "other_expenses": str(other_expenses),
                "inhouse_material_value": str(inhouse_material_value),
                "total_income": str(sales_revenue),
                "total_expenses": str(salary_expense + purchase_expense + other_expenses),
                "profit_loss_amount": str(sales_revenue - (salary_expense + purchase_expense + other_expenses) + inhouse_material_value),
                "profit_loss_status": "NO PROFIT / NO LOSS",
            }])

            return render(request, "marania_invoice_app/profit_loss_entry.html", {
                "profit_losses": profit_losses,
                "pl_json": pl_json,
            })

        month_year_raw = request.POST.get("month_year") or ""
        pl_key = request.POST.get("pl_key") or ""
        month = None
        year = None
        if month_year_raw:
            try:
                parts = month_year_raw.split("-")
                year = int(parts[0])
                month = int(parts[1])
            except (ValueError, IndexError, TypeError):
                month = year = None

        sales_revenue = Decimal(request.POST.get("sales_revenue") or "0")
        other_income = Decimal(request.POST.get("other_income") or "0")
        salary_expense = Decimal(request.POST.get("salary_expense") or "0")
        purchase_expense = Decimal(request.POST.get("purchase_expense") or "0")
        other_expenses = Decimal(request.POST.get("other_expenses") or "0")
        inhouse_material_value = Decimal(request.POST.get("inhouse_material_value") or "0")

        try:
            month = int(month) if month else None
            year = int(year) if year else None
        except (ValueError, TypeError):
            month = year = None

        try:
            sales_revenue = Decimal(sales_revenue)
            other_income = Decimal(other_income)
            salary_expense = Decimal(salary_expense)
            purchase_expense = Decimal(purchase_expense)
            other_expenses = Decimal(other_expenses)
            inhouse_material_value = Decimal(inhouse_material_value)
        except Exception:
            sales_revenue = other_income = salary_expense = purchase_expense = other_expenses = inhouse_material_value = Decimal("0")

        total_income = sales_revenue + other_income
        total_expenses = salary_expense + purchase_expense + other_expenses
        profit_loss_amount = total_income - total_expenses + inhouse_material_value

        if profit_loss_amount > 0:
            profit_loss_status = "PROFIT"
        elif profit_loss_amount < 0:
            profit_loss_status = "LOSS"
        else:
            profit_loss_status = "NO PROFIT / NO LOSS"

        data = {
            "month": month,
            "year": year,
            "sales_revenue": sales_revenue,
            "other_income": other_income,
            "salary_expense": salary_expense,
            "purchase_expense": purchase_expense,
            "other_expenses": other_expenses,
            "inhouse_material_value": inhouse_material_value,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "profit_loss_amount": profit_loss_amount,
            "profit_loss_status": profit_loss_status,
        }

        if pl_key:
            ProfitLoss.objects.filter(pl_key=pl_key).update(**data)
        else:
            # Check if a record with the same month and year already exists
            existing_pl = ProfitLoss.objects.filter(month=month, year=year).first()
            if existing_pl:
                ProfitLoss.objects.filter(pl_key=existing_pl.pl_key).update(**data)
            else:
                ProfitLoss.objects.create(**data)

        messages.success(request, "Profit/Loss entry saved successfully.")
        return redirect("profit_loss_entry")

    pl_data = []
    for pl in profit_losses:
        month_name = ""
        if pl.month:
            month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
            month_name = month_names.get(pl.month, "")
        pl_data.append({
            "pl_key": pl.pl_key,
            "month": pl.month,
            "year": pl.year,
            "month_year": f"{pl.year}-{pl.month:02d}" if (pl.year and pl.month) else "",
            "sales_revenue": str(pl.sales_revenue),
            "other_income": str(pl.other_income),
            "salary_expense": str(pl.salary_expense),
            "purchase_expense": str(pl.purchase_expense),
            "other_expenses": str(pl.other_expenses),
            "inhouse_material_value": str(pl.inhouse_material_value),
            "total_income": str(pl.total_income),
            "total_expenses": str(pl.total_expenses),
            "profit_loss_amount": str(pl.profit_loss_amount),
            "profit_loss_status": pl.profit_loss_status,
        })

    pl_json = json.dumps(pl_data)

    return render(request, "marania_invoice_app/profit_loss_entry.html", {
        "profit_losses": profit_losses,
        "pl_json": pl_json,
    })



def twine_inventory_entry(request):
    from .models import TwineInventory, Materials
    from datetime import datetime, timedelta
    from decimal import Decimal
    from django.http import JsonResponse
    import json

    twine_inventories = TwineInventory.objects.all()
    materials = Materials.objects.all()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "delete":
            pk = request.POST.get("ti_key")
            if pk:
                TwineInventory.objects.filter(ti_key=pk).delete()
                messages.success(request, "Twine Inventory entry deleted successfully.")
            return redirect("twine_inventory_entry")

        if action == "carry_forward":
            month_year_raw = request.POST.get("month_year") or ""
            if month_year_raw:
                try:
                    parts = month_year_raw.split("-")
                    year = int(parts[0])
                    month = int(parts[1])
                except (ValueError, IndexError, TypeError):
                    month = year = None
            
            if month and year:
                # Calculate previous month and year
                prev_month = month - 1
                prev_year = year
                if prev_month == 0:
                    prev_month = 12
                    prev_year = year - 1
                
                # Get all entries from previous month
                prev_entries = TwineInventory.objects.filter(month=prev_month, year=prev_year)
                
                if prev_entries.exists():
                    # Carry forward each entry
                    for prev_ti in prev_entries:
                        # Check if entry already exists for current month and twine
                        existing_ti = TwineInventory.objects.filter(month=month, year=year, twine=prev_ti.twine).first()
                        if not existing_ti:
                            # Create new entry with previous month's balance as opening stock
                            TwineInventory.objects.create(
                                month=month,
                                year=year,
                                twine=prev_ti.twine,
                                opening_stock=prev_ti.balance,
                                stock_in=Decimal("0"),
                                sales_out=Decimal("0"),
                                waste_used=Decimal("0"),
                                daily_usage=prev_ti.daily_usage,
                                usage_basis=prev_ti.usage_basis,
                                days_left=None,
                                est_stock_out_date=None,
                                remark=f"Carried forward from {prev_year}-{prev_month:02d}"
                            )
                    messages.success(request, f"Carried forward {prev_entries.count()} entries from previous month.")
                else:
                    messages.warning(request, "No entries found in previous month to carry forward.")
            else:
                messages.error(request, "Invalid Year-Month selected.")
            return redirect("twine_inventory_entry")

        if action == "carry_forward_selected":
            selected_keys_json = request.POST.get("selected_keys") or "[]"
            target_month = request.POST.get("target_month") or ""
            
            try:
                selected_keys = json.loads(selected_keys_json)
            except json.JSONDecodeError:
                return JsonResponse({"success": False, "error": "Invalid selected keys format"})
            
            if not selected_keys:
                return JsonResponse({"success": False, "error": "No items selected"})
            
            # Parse target month
            try:
                parts = target_month.split("-")
                target_year = int(parts[0])
                target_month_num = int(parts[1])
            except (ValueError, IndexError, TypeError):
                return JsonResponse({"success": False, "error": "Invalid target month format"})
            
            # Get selected inventory entries
            selected_entries = TwineInventory.objects.filter(ti_key__in=selected_keys)
            
            if not selected_entries.exists():
                return JsonResponse({"success": False, "error": "Selected entries not found"})
            
            carried_count = 0
            for entry in selected_entries:
                # Check if entry already exists for target month and twine
                existing_ti = TwineInventory.objects.filter(
                    month=target_month_num,
                    year=target_year,
                    twine=entry.twine
                ).first()
                
                if not existing_ti:
                    # Create new entry with current balance as opening stock
                    TwineInventory.objects.create(
                        month=target_month_num,
                        year=target_year,
                        twine=entry.twine,
                        opening_stock=entry.balance,
                        stock_in=Decimal("0"),
                        sales_out=Decimal("0"),
                        waste_used=Decimal("0"),
                        daily_usage=entry.daily_usage,
                        usage_basis=entry.usage_basis,
                        days_left=None,
                        est_stock_out_date=None,
                        remark=f"Carried forward from {entry.year}-{entry.month:02d}"
                    )
                    carried_count += 1
            
            return JsonResponse({
                "success": True,
                "message": f"Carried forward {carried_count} entries to {target_year}-{target_month_num:02d}"
            })

        month_year_raw = request.POST.get("month_year") or ""
        ti_key = request.POST.get("ti_key") or ""
        month = None
        year = None
        if month_year_raw:
            try:
                parts = month_year_raw.split("-")
                year = int(parts[0])
                month = int(parts[1])
            except (ValueError, IndexError, TypeError):
                month = year = None

        twine = request.POST.get("twine") or ""
        opening_stock = Decimal(request.POST.get("opening_stock") or "0")
        stock_in = Decimal(request.POST.get("stock_in") or "0")
        sales_out = Decimal(request.POST.get("sales_out") or "0")
        waste_used = Decimal(request.POST.get("waste_used") or "0")
        daily_usage = Decimal(request.POST.get("daily_usage") or "0")
        usage_basis = request.POST.get("usage_basis") or "Average"
        days_left = request.POST.get("days_left") or None
        est_stock_out_date = request.POST.get("est_stock_out_date") or None
        remark = request.POST.get("remark") or ""

        try:
            month = int(month) if month else None
            year = int(year) if year else None
        except (ValueError, TypeError):
            month = year = None

        try:
            opening_stock = Decimal(opening_stock)
            stock_in = Decimal(stock_in)
            sales_out = Decimal(sales_out)
            waste_used = Decimal(waste_used)
            daily_usage = Decimal(daily_usage)
        except Exception:
            opening_stock = stock_in = sales_out = waste_used = daily_usage = Decimal("0")

        try:
            days_left = int(days_left) if days_left else None
        except (ValueError, TypeError):
            days_left = None

        if est_stock_out_date:
            try:
                est_stock_out_date = datetime.strptime(est_stock_out_date, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                est_stock_out_date = None

        data = {
            "month": month,
            "year": year,
            "twine": twine,
            "opening_stock": opening_stock,
            "stock_in": stock_in,
            "sales_out": sales_out,
            "waste_used": waste_used,
            "balance": opening_stock + stock_in - sales_out - waste_used,
            "daily_usage": daily_usage,
            "usage_basis": usage_basis,
            "days_left": days_left,
            "est_stock_out_date": est_stock_out_date,
            "remark": remark,
        }

        if ti_key:
            TwineInventory.objects.filter(ti_key=ti_key).update(**data)
        else:
            # Check if a record with the same month, year, and twine already exists
            existing_ti = TwineInventory.objects.filter(month=month, year=year, twine=twine).first()
            if existing_ti:
                TwineInventory.objects.filter(ti_key=existing_ti.ti_key).update(**data)
            else:
                # Carry-forward logic: Get previous month's balance as opening stock
                if month and year and twine:
                    # Calculate previous month and year
                    prev_month = month - 1
                    prev_year = year
                    if prev_month == 0:
                        prev_month = 12
                        prev_year = year - 1
                    
                    # Get previous month's entry for the same twine
                    prev_ti = TwineInventory.objects.filter(month=prev_month, year=prev_year, twine=twine).first()
                    if prev_ti:
                        # Use previous month's balance as opening stock
                        data["opening_stock"] = prev_ti.balance
                        data["balance"] = prev_ti.balance + stock_in - sales_out - waste_used
                
                TwineInventory.objects.create(**data)

        messages.success(request, "Twine Inventory entry saved successfully.")
        return redirect("twine_inventory_entry")

    ti_data = []
    for ti in twine_inventories:
        ti_data.append({
            "ti_key": ti.ti_key,
            "month": ti.month,
            "year": ti.year,
            "month_year": f"{ti.year}-{ti.month:02d}" if (ti.year and ti.month) else "",
            "twine": ti.twine or "",
            "opening_stock": str(ti.opening_stock),
            "stock_in": str(ti.stock_in),
            "sales_out": str(ti.sales_out),
            "waste_used": str(ti.waste_used),
            "balance": str(ti.balance),
            "daily_usage": str(ti.daily_usage),
            "usage_basis": ti.usage_basis,
            "days_left": ti.days_left,
            "est_stock_out_date": ti.est_stock_out_date.strftime("%Y-%m-%d") if ti.est_stock_out_date else "",
            "remark": ti.remark or "",
        })

    ti_json = json.dumps(ti_data)

    return render(request, "marania_invoice_app/twine_inventory_entry.html", {
        "twine_inventories": twine_inventories,
        "ti_json": ti_json,
        "materials": materials,
    })


def get_twine_inventory_data(request):
    from .models import Purchase, Sales, Materials, TwineInventory, Product
    from decimal import Decimal

    month_year = request.GET.get("month_year", "")
    material_code = request.GET.get("material_code", "")

    stock_in = Decimal("0")
    sales_out = Decimal("0")
    opening_stock = Decimal("0")
    debug_info = []

    # Parse month_year to get year and month
    try:
        parts = month_year.split("-")
        year = int(parts[0])
        month = int(parts[1])
    except (ValueError, IndexError, TypeError):
        year = month = None

    debug_info.append(f"Request: month_year={month_year}, material_code={material_code}, parsed_year={year}, parsed_month={month}")

    if year and month and material_code:
        # Get material name for matching
        material_name = None
        try:
            material = Materials.objects.get(code=material_code)
            material_name = material.name
            debug_info.append(f"Material found: code={material.code}, name={material.name}, displayname={material.displayname}")
        except Materials.DoesNotExist:
            debug_info.append("Material not found in Materials table")
        
        # Build synonyms list dynamically from Product-Material relationship
        # Get all Product codes that reference this Material
        synonyms = [material_code]
        if material_name:
            synonyms.append(material_name)
        
        # Find all Products that have this material as their foreign key
        products_with_this_material = Product.objects.filter(material__code=material_code)
        product_codes = list(products_with_this_material.values_list('code', flat=True))
        synonyms.extend(product_codes)
        
        debug_info.append(f"Product codes for material {material_code}: {product_codes}")
        debug_info.append(f"Synonyms for matching: {synonyms}")
        
        # Calculate Stock In from Purchase module
        # Filter purchases where is_twine=True and delivery_date is in the selected month
        purchases = Purchase.objects.filter(
            is_twine=True,
            delivery_date__year=year,
            delivery_date__month=month
        )
        debug_info.append(f"Purchases in month: {purchases.count()} found")
        
        for purchase in purchases:
            debug_info.append(f"  - purchase_key={purchase.purchase_key}, material_code={purchase.material_code}, material={purchase.material}, delivery_date={purchase.delivery_date}, quantity_weight={purchase.quantity_weight}, is_twine={purchase.is_twine}")
            
            # Check if purchase matches any synonym
            match_found = False
            if purchase.material_code and purchase.material_code in synonyms:
                match_found = True
                debug_info.append(f"    -> Matched by material_code")
            elif purchase.material and any(synonym in purchase.material for synonym in synonyms):
                match_found = True
                debug_info.append(f"    -> Matched by material field")
            # Also check if material_code appears in material field (partial match)
            elif purchase.material and material_code in purchase.material:
                match_found = True
                debug_info.append(f"    -> Matched by material_code in material field (partial)")
            # Also check if material name appears in material_code field
            elif purchase.material_code and material_name and material_name in purchase.material_code:
                match_found = True
                debug_info.append(f"    -> Matched by material_name in material_code field")
            
            if match_found and purchase.quantity_weight:
                stock_in += purchase.quantity_weight
                debug_info.append(f"    -> Added quantity_weight: {purchase.quantity_weight}")

        # Calculate Sales Out from Sales module
        # Filter sales where sales_entry_date is in the selected month
        sales = Sales.objects.filter(
            sales_entry_date__year=year,
            sales_entry_date__month=month
        )
        debug_info.append(f"Sales in month: {sales.count()} found")
        
        for sale in sales:
            debug_info.append(f"  - sale_key={sale.sales_key}, twine={sale.twine}, speification={sale.speification}, sales_entry_date={sale.sales_entry_date}, processed_weight={sale.processed_weight}, initial_weight={sale.initial_weight}")
            
            # Check if the twine field contains any synonym
            match_found = False
            for synonym in synonyms:
                if sale.twine and synonym in sale.twine:
                    match_found = True
                    debug_info.append(f"    -> Matched by synonym '{synonym}' in twine field")
                    break
            
            # Also check specification field
            if not match_found and sale.speification:
                for synonym in synonyms:
                    if synonym in sale.speification:
                        match_found = True
                        debug_info.append(f"    -> Matched by synonym '{synonym}' in speification field")
                        break
            
            # Additional fallback: check if material_code appears in twine or speification (partial match)
            if not match_found:
                if sale.twine and material_code in sale.twine:
                    match_found = True
                    debug_info.append(f"    -> Matched by material_code in twine field (partial)")
                elif sale.speification and material_code in sale.speification:
                    match_found = True
                    debug_info.append(f"    -> Matched by material_code in speification field (partial)")
            
            # Additional fallback: check if material name appears in twine or speification
            if not match_found and material_name:
                if sale.twine and material_name in sale.twine:
                    match_found = True
                    debug_info.append(f"    -> Matched by material_name in twine field")
                elif sale.speification and material_name in sale.speification:
                    match_found = True
                    debug_info.append(f"    -> Matched by material_name in speification field")
            
            if match_found:
                if sale.processed_weight:
                    sales_out += sale.processed_weight
                    debug_info.append(f"    -> Added processed_weight: {sale.processed_weight}")
                elif sale.initial_weight:
                    sales_out += sale.initial_weight
                    debug_info.append(f"    -> Added initial_weight: {sale.initial_weight}")

        # Calculate Opening Stock from previous month's Balance
        # Calculate previous month and year
        prev_month = month - 1
        prev_year = year
        if prev_month == 0:
            prev_month = 12
            prev_year = year - 1
        
        debug_info.append(f"Looking for previous month: {prev_year}-{prev_month:02d}")
        
        # Get previous month's inventory entry for the same twine
        prev_inventory = TwineInventory.objects.filter(
            year=prev_year,
            month=prev_month,
            twine__icontains=material_code
        ).first()
        
        daily_usage_prev = Decimal("0")
        if prev_inventory:
            opening_stock = prev_inventory.balance
            daily_usage_prev = prev_inventory.daily_usage or Decimal("0")
            debug_info.append(f"Found previous inventory: ti_key={prev_inventory.ti_key}, balance={prev_inventory.balance}, daily_usage={daily_usage_prev}")
        else:
            debug_info.append("No previous inventory found for this twine")

    return JsonResponse({
        "stock_in": str(stock_in),
        "sales_out": str(sales_out),
        "opening_stock": str(opening_stock),
        "daily_usage": str(daily_usage_prev),
        "debug": debug_info,
    })


def invoice_aging_report(request):
    from .models import Invoice, PaymentAllocation, PaymentReceipt
    from datetime import date, timedelta
    from decimal import Decimal
    import csv
    from django.http import HttpResponse

    # Get filter parameters
    group_by = request.GET.get('group_by', 'customer')  # customer, age, none
    export_format = request.GET.get('export', None)  # csv, pdf, or None

    # Fetch pending and partially paid invoices
    invoices = Invoice.objects.filter(
        payment_status__in=['Pending', 'Partial']
    ).exclude(
        payment_status__in=['Paid', 'WrittenOff', 'Cancelled']
    )

    # Calculate aging for each invoice
    aging_data = []
    today = date.today()

    for invoice in invoices:
        # Calculate total allocated amount
        total_allocated = PaymentAllocation.objects.filter(
            invoice__invoice_number=invoice.invoice_number
        ).aggregate(
            total=Sum('allocated_amount')
        )['total'] or Decimal('0')

        # Calculate outstanding balance
        outstanding = invoice.gross_total - total_allocated

        # Calculate age in days
        if invoice.invoice_date:
            age_days = (today - invoice.invoice_date).days
        else:
            age_days = 0

        # Determine age bucket
        if age_days <= 30:
            age_bucket = '0-30 Days'
        elif age_days <= 60:
            age_bucket = '31-60 Days'
        elif age_days <= 90:
            age_bucket = '61-90 Days'
        elif age_days <= 120:
            age_bucket = '91-120 Days'
        else:
            age_bucket = '120+ Days'

        aging_data.append({
            'invoice_number': invoice.invoice_number,
            'invoice_date': invoice.invoice_date,
            'customer_code': invoice.customer_code,
            'customer_name': invoice.customer_name,
            'gross_total': invoice.gross_total,
            'total_allocated': total_allocated,
            'outstanding': outstanding,
            'age_days': age_days,
            'age_bucket': age_bucket,
            'payment_status': invoice.payment_status,
        })

    # Group data based on selection
    if group_by == 'customer':
        grouped_data = {}
        for item in aging_data:
            customer_key = f"{item['customer_code']}-{item['customer_name']}"
            if customer_key not in grouped_data:
                grouped_data[customer_key] = []
            grouped_data[customer_key].append(item)
    elif group_by == 'age':
        grouped_data = {}
        for item in aging_data:
            if item['age_bucket'] not in grouped_data:
                grouped_data[item['age_bucket']] = []
            grouped_data[item['age_bucket']].append(item)
    else:
        grouped_data = None  # No grouping

    # Calculate summary statistics
    total_outstanding = sum(item['outstanding'] for item in aging_data)
    total_invoices = len(aging_data)
    
    # Calculate outstanding by age buckets
    age_bucket_totals = {
        '0_30_Days': sum(item['outstanding'] for item in aging_data if item['age_bucket'] == '0-30 Days'),
        '31_60_Days': sum(item['outstanding'] for item in aging_data if item['age_bucket'] == '31-60 Days'),
        '61_90_Days': sum(item['outstanding'] for item in aging_data if item['age_bucket'] == '61-90 Days'),
        '91_120_Days': sum(item['outstanding'] for item in aging_data if item['age_bucket'] == '91-120 Days'),
        '120_plus_Days': sum(item['outstanding'] for item in aging_data if item['age_bucket'] == '120+ Days'),
    }

    # Export to CSV
    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="invoice_aging_report.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Invoice Number', 'Invoice Date', 'Customer Code', 'Customer Name',
            'Gross Total', 'Total Allocated', 'Outstanding', 'Age Days',
            'Age Bucket', 'Payment Status'
        ])

        for item in aging_data:
            writer.writerow([
                item['invoice_number'],
                item['invoice_date'],
                item['customer_code'],
                item['customer_name'],
                item['gross_total'],
                item['total_allocated'],
                item['outstanding'],
                item['age_days'],
                item['age_bucket'],
                item['payment_status'],
            ])

        return response

    # Export to PDF
    if export_format == 'pdf':
        from django.template.loader import render_to_string
        from weasyprint import HTML

        html_string = render_to_string('marania_invoice_app/invoice_aging_report_pdf.html', {
            'aging_data': aging_data,
            'grouped_data': grouped_data,
            'group_by': group_by,
            'today': today,
        })

        html = HTML(string=html_string)
        pdf_file = html.write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="invoice_aging_report.pdf"'
        return response

    # Render HTML page
    return render(request, 'marania_invoice_app/invoice_aging_report.html', {
        'aging_data': aging_data,
        'grouped_data': grouped_data,
        'group_by': group_by,
        'today': today,
        'total_outstanding': total_outstanding,
        'total_invoices': total_invoices,
        'age_bucket_totals': age_bucket_totals,
    })


def trend_analytics(request):
    from datetime import date, datetime, timedelta
    from decimal import Decimal
    import csv
    from django.http import HttpResponse
    from django.core.paginator import Paginator
    
    from marania_invoice_app.analytics.services.product_parser import ProductParser
    from marania_invoice_app.analytics.services.specification_parser import SpecificationParser
    from marania_invoice_app.analytics.services.trend_analytics import TrendAnalyticsService
    from marania_invoice_app.analytics.services.season_analyzer import SeasonAnalyzer
    from marania_invoice_app.analytics.services.recommendation_engine import RecommendationEngine
    from marania_invoice_app.analytics.services.models import TrendFilters
    
    # Initialize services
    product_parser = ProductParser()
    spec_parser = SpecificationParser()
    trend_service = TrendAnalyticsService()
    season_analyzer = SeasonAnalyzer()
    recommendation_engine = RecommendationEngine()
    
    # Get filter parameters from request
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')
    product_codes = request.GET.getlist('product_codes')
    mm_values = request.GET.getlist('mm_values')
    md_values = request.GET.getlist('md_values')
    customers = request.GET.getlist('customers')
    metric = request.GET.get('metric', 'sales')
    
    # Export format
    export_format = request.GET.get('export')
    
    # Pagination
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 25)
    
    # Set default dates if not provided (last 6 months)
    if not start_date_str:
        end_date_default = date.today()
        start_date_default = end_date_default - timedelta(days=180)
        start_date_str = start_date_default.isoformat()
        end_date_str = end_date_default.isoformat()
    
    # Parse dates
    start_date = None
    end_date = None
    if start_date_str:
        try:
            start_date = date.fromisoformat(start_date_str)
        except ValueError:
            pass
    if end_date_str:
        try:
            end_date = date.fromisoformat(end_date_str)
        except ValueError:
            pass
    
    # Create filters object
    filters = TrendFilters(
        start_date=start_date,
        end_date=end_date,
        product_codes=product_codes,
        mm_values=[Decimal(mm) if mm else None for mm in mm_values],
        md_values=[Decimal(md) if md else None for md in md_values],
        customers=customers,
        statuses=[],
        metric=metric
    )
    
    # Get base queryset
    from marania_invoice_app.models import Sales
    sales_queryset = Sales.objects.all()
    
    # Apply filters
    filtered_queryset = trend_service.apply_filters(sales_queryset, filters)
    
    # Normalize sales data
    normalized_sales = trend_service.normalize_sales(filtered_queryset)
    
    # Apply MM/MD filters (post-normalization since we need parsed values)
    if filters.mm_values:
        normalized_sales = [s for s in normalized_sales if s.mm in filters.mm_values]
    if filters.md_values:
        normalized_sales = [s for s in normalized_sales if s.md in filters.md_values]
    
    # Calculate analytics
    summary = trend_service.get_summary(normalized_sales)
    monthly_trend = trend_service.get_monthly_trend(normalized_sales, metric)
    product_trends = trend_service.get_product_trends(normalized_sales, metric, top_n=10)
    spec_trends = trend_service.get_specification_trends(normalized_sales, metric, top_n=10)
    product_spec_matrix = trend_service.get_product_specification_matrix(normalized_sales)
    data_quality = trend_service.get_data_quality(normalized_sales)
    
    # Calculate top 10 customers
    customer_data = {}
    for sale in normalized_sales:
        if sale.customer:
            if sale.customer not in customer_data:
                customer_data[sale.customer] = {
                    'customer': sale.customer,
                    'sales': Decimal('0'),
                    'specifications': {}
                }
            customer_data[sale.customer]['sales'] += sale.total_amount
            # Combine product code with normalized specification
            full_spec = f"{sale.product_code}-{sale.normalized_specification}" if sale.product_code and sale.normalized_specification and sale.normalized_specification != "Unknown" else (sale.product_code or sale.normalized_specification or "Unknown")
            # Track weight per specification (use processed_weight if available, otherwise initial_weight)
            weight = sale.processed_weight if sale.processed_weight > 0 else sale.initial_weight
            if full_spec not in customer_data[sale.customer]['specifications']:
                customer_data[sale.customer]['specifications'][full_spec] = Decimal('0')
            customer_data[sale.customer]['specifications'][full_spec] += weight
    
    # Set orders = unique specification count, then sort
    for customer in customer_data.values():
        customer['orders'] = len(customer['specifications'])
    
    top_customers = sorted(
        customer_data.values(),
        key=lambda x: x['orders'],
        reverse=True
    )[:10]
    
    # Convert specifications dict to comma-separated strings with weight in kg
    for customer in top_customers:
        spec_strings = [f"{spec}({weight:.2f} kg)" for spec, weight in sorted(customer['specifications'].items(), key=lambda x: x[1], reverse=True)]
        customer['specifications'] = ', '.join(spec_strings)
    
    # Generate recommendations (without season comparison for now)
    recommendations = []
    executive_summary = ""
    
    if product_spec_matrix:
        # Calculate YoY growth and seasonality for each product-spec combination
        product_spec_trends = []
        
        for item in product_spec_matrix[:20]:  # Top 20 for recommendations
            # Get season data for this combination
            combination_sales = [
                s for s in normalized_sales
                if s.product_code == item['product'] and s.normalized_specification == item['specification']
            ]
            
            if not combination_sales:
                continue
            
            # Calculate YoY growth by year
            yoy_growth = None
            years_in_data = sorted(set(s.sales_entry_date.year for s in combination_sales))
            
            if len(years_in_data) >= 2:
                latest_year = years_in_data[-1]
                prev_year = years_in_data[-2]
                
                latest_sales = sum(
                    s.total_amount for s in combination_sales
                    if s.sales_entry_date.year == latest_year
                )
                prev_sales = sum(
                    s.total_amount for s in combination_sales
                    if s.sales_entry_date.year == prev_year
                )
                
                yoy_growth = season_analyzer.calculate_yoy_growth(latest_sales, prev_sales)
            
            # Calculate seasonality
            seasonality = None
            if combination_sales:
                total_sales = sum(s.total_amount for s in combination_sales)
                
                if len(years_in_data) == 1:
                    # Only one year of data
                    seasonality = 100.0
                else:
                    # Calculate seasonality across years
                    annual_sales = {}
                    for year in years_in_data:
                        annual_sales[year] = sum(
                            s.total_amount for s in combination_sales
                            if s.sales_entry_date.year == year
                        )
                    
                    total_annual = sum(annual_sales.values())
                    if total_annual > 0:
                        seasonality = season_analyzer.calculate_seasonality_score(total_sales, total_annual)
            
            # Get peak month
            peak_month_data = season_analyzer.get_peak_month(combination_sales)
            peak_month = peak_month_data[0] if peak_month_data else None
            
            # Classify trend
            from marania_invoice_app.analytics.services.recommendation_engine import TrendClassification, TrendConfidence
            from marania_invoice_app.analytics.services.models import ProductSpecificationTrend
            trend_class = recommendation_engine.classify_trend(yoy_growth)
            confidence = recommendation_engine.calculate_confidence(len(years_in_data), item['orders'])
            
            product_spec_trends.append(ProductSpecificationTrend(
                product=item['product'],
                specification=item['specification'],
                mm=item['mm'],
                md=item['md'],
                total_sales=item['sales'],
                total_weight=item['weight'],
                total_pieces=item['pieces'],
                order_count=item['orders'],
                yoy_growth=yoy_growth,
                trend_classification=trend_class.value,
                trend_confidence=confidence.value,
                seasonality_score=seasonality,
                peak_month=peak_month
            ))
        
        # Generate recommendations
        if product_spec_trends:
            recommendations = recommendation_engine.rank_recommendations(product_spec_trends)
            executive_summary = recommendation_engine.generate_executive_summary(product_spec_trends)
    
    # Get available filter values
    all_sales = Sales.objects.all()
    all_products = sorted(set(
        product_parser.extract_product_code(s.twine)
        for s in all_sales
        if s.twine
    ))
    all_customers = sorted(set(s.customer for s in all_sales if s.customer))
    
    # Get unique MM and MD values
    all_mm = sorted(set(
        spec_parser.extract_mm(s.speification)
        for s in all_sales
        if spec_parser.extract_mm(s.speification) is not None
    ))
    all_md = sorted(set(
        spec_parser.extract_md(s.speification)
        for s in all_sales
        if spec_parser.extract_md(s.speification) is not None
    ))
    
    # Get date range
    date_range = all_sales.aggregate(
        min_date=models.Min('sales_entry_date'),
        max_date=models.Max('sales_entry_date')
    )
    
    # Pagination for detailed orders
    paginator = Paginator(normalized_sales, int(page_size))
    paginated_orders = paginator.get_page(page)
    
    # Export to CSV
    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="trend_analytics.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Order No', 'Sales Date', 'Customer', 'Product', 'Raw Specification',
            'MM', 'MD', 'Normalized Specification', 'Colour', 'Weight', 'Pieces', 'Amount', 'Status'
        ])
        
        for sale in normalized_sales:
            writer.writerow([
                sale.order_no,
                sale.sales_entry_date,
                sale.customer,
                sale.product_code,
                sale.raw_specification,
                sale.mm,
                sale.md,
                sale.normalized_specification,
                sale.colour,
                sale.processed_weight,
                sale.piece_count,
                sale.total_amount,
                sale.status
            ])
        
        return response
    
    # Export to PDF
    if export_format == 'pdf':
        from django.template.loader import render_to_string
        from weasyprint import HTML
        
        html_string = render_to_string('marania_invoice_app/trend_analytics_pdf.html', {
            'summary': summary,
            'monthly_trend': monthly_trend,
            'product_trends': product_trends,
            'spec_trends': spec_trends,
            'product_spec_matrix': product_spec_matrix,
            'recommendations': recommendations,
            'executive_summary': executive_summary,
            'data_quality': data_quality,
            'top_customers': top_customers,
            'today': date.today(),
        })
        
        html = HTML(string=html_string)
        pdf_file = html.write_pdf()
        
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="trend_analytics.pdf"'
        return response
    
    # Prepare chart data with top customer for each data point
    import json
    
    # Calculate top customer for each month
    monthly_chart_data = {
        'labels': [f"{m['year']}-{m['month']:02d}" for m in monthly_trend],
        'sales': [float(m['sales']) for m in monthly_trend],
        'weight': [float(m['weight']) for m in monthly_trend],
        'pieces': [m['pieces'] for m in monthly_trend],
        'orders': [m['orders'] for m in monthly_trend],
        'top_customers': []
    }
    
    for month_data in monthly_trend:
        month_sales = [
            s for s in normalized_sales
            if s.sales_entry_date.year == month_data['year'] and s.sales_entry_date.month == month_data['month']
        ]
        if month_sales:
            customer_totals = {}
            for sale in month_sales:
                if sale.customer:
                    customer_totals[sale.customer] = customer_totals.get(sale.customer, Decimal('0')) + sale.total_amount
            if customer_totals:
                top_customer = max(customer_totals.items(), key=lambda x: x[1])
                monthly_chart_data['top_customers'].append(top_customer[0])
            else:
                monthly_chart_data['top_customers'].append('')
        else:
            monthly_chart_data['top_customers'].append('')
    
    # Calculate top customer for each product
    product_chart_data = {
        'labels': [p['product'] for p in product_trends],
        'sales': [float(p['sales']) for p in product_trends],
        'weight': [float(p['weight']) for p in product_trends],
        'pieces': [p['pieces'] for p in product_trends],
        'orders': [p['orders'] for p in product_trends],
        'top_customers': []
    }
    
    for product_data in product_trends:
        product_sales = [
            s for s in normalized_sales
            if s.product_code == product_data['product']
        ]
        if product_sales:
            customer_totals = {}
            for sale in product_sales:
                if sale.customer:
                    customer_totals[sale.customer] = customer_totals.get(sale.customer, Decimal('0')) + sale.total_amount
            if customer_totals:
                top_customer = max(customer_totals.items(), key=lambda x: x[1])
                product_chart_data['top_customers'].append(top_customer[0])
            else:
                product_chart_data['top_customers'].append('')
        else:
            product_chart_data['top_customers'].append('')
    
    # Reorder product_spec_matrix by Product, orders, specification
    product_spec_matrix_sorted = sorted(product_spec_matrix, key=lambda x: (x['product'], -x['orders'], x['specification']))
    
    # Render HTML page
    return render(request, 'marania_invoice_app/trend_analytics.html', {
        'summary': summary,
        'monthly_trend': monthly_trend,
        'product_trends': product_trends,
        'spec_trends': spec_trends,
        'product_spec_matrix': product_spec_matrix_sorted,
        'recommendations': recommendations,
        'executive_summary': executive_summary,
        'data_quality': data_quality,
        'top_customers': top_customers,
        'all_products': all_products,
        'all_customers': all_customers,
        'all_mm': all_mm,
        'all_md': all_md,
        'date_range': date_range,
        'paginated_orders': paginated_orders,
        'filters': filters,
        'today': date.today(),
        'monthly_chart_data_json': json.dumps(monthly_chart_data),
        'product_chart_data_json': json.dumps(product_chart_data),
    })


def season_trends(request):
    from .models import Sales
    from datetime import date, datetime
    from decimal import Decimal
    import csv
    from django.http import HttpResponse
    from django.db.models import Sum, Count
    import re

    # Get filter parameters
    group_by = request.GET.get('group_by', 'product')  # product, specification, none
    product_filter = request.GET.get('product', '')
    mm_filter = request.GET.get('mm', '')
    md_filter = request.GET.get('md', '')
    selvage_filter = request.GET.get('selvage', '')
    export_format = request.GET.get('export', None)  # csv, pdf, or None
    year_filter = request.GET.get('year', '')

    # Parse specification to extract MM, MD, Selvage
    def parse_specification(spec):
        if not spec:
            return {'mm': '', 'md': '', 'selvage': ''}
        
        mm = ''
        md = ''
        selvage = ''
        
        # Extract MM (Mesh Size) - typically like "MM-50", "50MM", etc.
        mm_match = re.search(r'MM[-\s]*(\d+)', spec, re.IGNORECASE)
        if mm_match:
            mm = mm_match.group(1)
        
        # Extract MD (Mesh Depth) - typically like "MD-15", "15MD", etc.
        md_match = re.search(r'MD[-\s]*(\d+)', spec, re.IGNORECASE)
        if md_match:
            md = md_match.group(1)
        
        # Extract Selvage - typically like "SEL-2", "2SEL", "Selvage-2", etc.
        selvage_match = re.search(r'(SEL|SELVAGE)[-]*(\d+)', spec, re.IGNORECASE)
        if selvage_match:
            selvage = selvage_match.group(2)
        
        return {'mm': mm, 'md': md, 'selvage': selvage}

    # Fetch sales data
    sales = Sales.objects.all()

    # Apply filters
    if year_filter:
        sales = sales.filter(sales_entry_date__year=int(year_filter))
    
    if product_filter:
        sales = sales.filter(twine__icontains=product_filter)

    # Process sales data with parsed specifications
    trends_data = []
    for sale in sales:
        spec_data = parse_specification(sale.speification)
        
        # Apply specification filters
        if mm_filter and spec_data['mm'] != mm_filter:
            continue
        if md_filter and spec_data['md'] != md_filter:
            continue
        if selvage_filter and spec_data['selvage'] != selvage_filter:
            continue
        
        trends_data.append({
            'sales_key': sale.sales_key,
            'sales_entry_date': sale.sales_entry_date,
            'year': sale.sales_entry_date.year if sale.sales_entry_date else None,
            'month': sale.sales_entry_date.month if sale.sales_entry_date else None,
            'product_code': sale.twine or '',
            'specification': sale.speification or '',
            'mm': spec_data['mm'],
            'md': spec_data['md'],
            'selvage': spec_data['selvage'],
            'colour': sale.colour or '',
            'processed_weight': sale.processed_weight or Decimal('0'),
            'total_amount': sale.total_amount or Decimal('0'),
            'customer': sale.customer or '',
        })

    # Group data based on selection
    if group_by == 'product':
        grouped_data = {}
        for item in trends_data:
            product_key = item['product_code'] or 'Unknown'
            if product_key not in grouped_data:
                grouped_data[product_key] = []
            grouped_data[product_key].append(item)
    elif group_by == 'specification':
        grouped_data = {}
        for item in trends_data:
            spec_key = f"MM:{item['mm']}-MD:{item['md']}-SEL:{item['selvage']}"
            if spec_key not in grouped_data:
                grouped_data[spec_key] = []
            grouped_data[spec_key].append(item)
    else:
        grouped_data = None  # No grouping

    # Calculate summary statistics
    total_sales = sum(item['total_amount'] for item in trends_data)
    total_weight = sum(item['processed_weight'] for item in trends_data)
    total_records = len(trends_data)

    # Get available years for filter
    available_years = sorted(set(item['year'] for item in trends_data if item['year']))

    # Get unique MM, MD, Selvage values for filters
    unique_mm = sorted(set(item['mm'] for item in trends_data if item['mm']))
    unique_md = sorted(set(item['md'] for item in trends_data if item['md']))
    unique_selvage = sorted(set(item['selvage'] for item in trends_data if item['selvage']))

    # Export to CSV
    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="season_trends.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Sales Date', 'Year', 'Month', 'Product Code', 'Specification',
            'MM', 'MD', 'Selvage', 'Colour', 'Processed Weight', 'Total Amount', 'Customer'
        ])

        for item in trends_data:
            writer.writerow([
                item['sales_entry_date'],
                item['year'],
                item['month'],
                item['product_code'],
                item['specification'],
                item['mm'],
                item['md'],
                item['selvage'],
                item['colour'],
                item['processed_weight'],
                item['total_amount'],
                item['customer'],
            ])

        return response

    # Export to PDF
    if export_format == 'pdf':
        from django.template.loader import render_to_string
        from weasyprint import HTML

        html_string = render_to_string('marania_invoice_app/season_trends_pdf.html', {
            'trends_data': trends_data,
            'grouped_data': grouped_data,
            'group_by': group_by,
            'today': date.today(),
            'total_sales': total_sales,
            'total_weight': total_weight,
            'total_records': total_records,
        })

        html = HTML(string=html_string)
        pdf_file = html.write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="season_trends.pdf"'
        return response

    # Prepare chart data
    chart_data = {}
    if group_by == 'product':
        for product, items in grouped_data.items():
            # Group by month
            monthly_data = {}
            for item in items:
                month_key = f"{item['year']}-{item['month']:02d}"
                if month_key not in monthly_data:
                    monthly_data[month_key] = {'weight': 0, 'amount': 0}
                monthly_data[month_key]['weight'] += float(item['processed_weight'])
                monthly_data[month_key]['amount'] += float(item['total_amount'])
            chart_data[product] = monthly_data
    elif group_by == 'specification':
        for spec, items in grouped_data.items():
            monthly_data = {}
            for item in items:
                month_key = f"{item['year']}-{item['month']:02d}"
                if month_key not in monthly_data:
                    monthly_data[month_key] = {'weight': 0, 'amount': 0}
                monthly_data[month_key]['weight'] += float(item['processed_weight'])
                monthly_data[month_key]['amount'] += float(item['total_amount'])
            chart_data[spec] = monthly_data

    # Render HTML page
    import json
    return render(request, 'marania_invoice_app/season_trends.html', {
        'trends_data': trends_data,
        'grouped_data': grouped_data,
        'group_by': group_by,
        'today': date.today(),
        'total_sales': total_sales,
        'total_weight': total_weight,
        'total_records': total_records,
        'available_years': available_years,
        'unique_mm': unique_mm,
        'unique_md': unique_md,
        'unique_selvage': unique_selvage,
        'chart_data': json.dumps(chart_data),
        'product_filter': product_filter,
        'mm_filter': mm_filter,
        'md_filter': md_filter,
        'selvage_filter': selvage_filter,
        'year_filter': year_filter,
    })


# =======================
# Configuration Views
# =======================

@login_required
def material_conversion_ratio_view(request):
    # JSON API for fetching conversion factor by code
    if request.GET.get("code"):
        from django.http import JsonResponse
        code = request.GET.get("code")
        try:
            ratio = MaterialConversionRatio.objects.get(material_code=code)
            return JsonResponse({
                "conversion_ratio": str(ratio.conversion_ratio),
                "base_conversion_ratio": str(ratio.base_conversion_ratio),
                "multiplier": str(ratio.multiplier),
            })
        except MaterialConversionRatio.DoesNotExist:
            return JsonResponse({"conversion_ratio": None, "base_conversion_ratio": None, "multiplier": None})

    if request.method == 'POST':
        action = request.POST.get("action")
        
        # SAVE / UPDATE
        if action == "save":
            rows = zip(
                request.POST.getlist("material_code"),
                request.POST.getlist("base_conversion_ratio"),
                request.POST.getlist("multiplier"),
            )
            
            for material_code, base_conversion_ratio, multiplier in rows:
                if not material_code:
                    continue
                base_val = Decimal(base_conversion_ratio) if base_conversion_ratio else Decimal(0)
                mult_val = Decimal(multiplier) if multiplier else Decimal(1)
                conversion_ratio = base_val * mult_val
                MaterialConversionRatio.objects.update_or_create(
                    material_code=material_code,
                    defaults={
                        "base_conversion_ratio": base_val,
                        "multiplier": mult_val,
                        "conversion_ratio": conversion_ratio,
                    }
                )
            messages.success(request, "Material Conversion Ratio saved successfully.")
        
        # DELETE
        elif action == "delete":
            codes = request.POST.getlist("material_code")
            for code in codes:
                if code:
                    MaterialConversionRatio.objects.filter(material_code=code).delete()
            messages.success(request, "Material Conversion Ratio deleted successfully.")
    
    context = {
        "ratios": MaterialConversionRatio.objects.all(),
        "materials": Materials.objects.all(),
    }
    return render(request, "marania_invoice_app/material_conversion_ratio.html", context)


@login_required
def processing_cost_view(request):
    if request.method == 'POST':
        action = request.POST.get("action")
        
        # SAVE / UPDATE
        if action == "save":
            rows = zip(
                request.POST.getlist("material_code"),
                request.POST.getlist("processing_cost_per_kg"),
                request.POST.getlist("color_cost_per_kg"),
                request.POST.getlist("small_depth_size_cost_per_kg"),
                request.POST.getlist("small_depth_starting_depth"),
            )
            
            for material_code, processing_cost, color_cost, small_size_cost, small_mesh_depth in rows:
                if not material_code:
                    continue
                ProcessingCost.objects.update_or_create(
                    material_code=material_code,
                    defaults={
                        "processing_cost_per_kg": processing_cost or 0,
                        "color_cost_per_kg": color_cost or 0,
                        "small_depth_size_cost_per_kg": small_size_cost or 0,
                        "small_depth_starting_depth": small_mesh_depth or 0,
                    }
                )
            messages.success(request, "Processing Cost saved successfully.")
        
        # DELETE
        elif action == "delete":
            codes = request.POST.getlist("material_code")
            for code in codes:
                if code:
                    ProcessingCost.objects.filter(material_code=code).delete()
            messages.success(request, "Processing Cost deleted successfully.")
    
    context = {
        "costs": ProcessingCost.objects.all(),
        "materials": Materials.objects.all(),
    }
    return render(request, "marania_invoice_app/processing_cost.html", context)


@login_required
def machine_operational_cost_view(request):
    if request.method == 'POST':
        action = request.POST.get("action")
        
        # SAVE / UPDATE
        if action == "save":
            rows = zip(
                request.POST.getlist("machine_number"),
                request.POST.getlist("number_of_shuttles"),
                request.POST.getlist("running_product_code"),
                request.POST.getlist("operator_cost_per_day"),
                request.POST.getlist("bobbin_winder_cost_per_day"),
                request.POST.getlist("mending_cost_per_day"),
                request.POST.getlist("mechanic_cost_per_day"),
                request.POST.getlist("electricity_cost_per_day"),
                request.POST.getlist("maintenance_cost_per_day"),
                request.POST.getlist("miscellaneous_cost_per_day"),
                request.POST.getlist("knots_capacity_per_day"),
            )

            for (machine_number, num_shuttles, product_code,
                 operator_cost, bobbin_cost, mending_cost, mechanic_cost,
                 electricity_cost, maintenance_cost, misc_cost, knots_cap) in rows:
                if not machine_number:
                    continue
                MachineOperationalCost.objects.update_or_create(
                    machine_number=machine_number,
                    defaults={
                        "number_of_shuttles": num_shuttles or 0,
                        "running_product_code": product_code or None,
                        "operator_cost_per_day": operator_cost or 0,
                        "bobbin_winder_cost_per_day": bobbin_cost or 0,
                        "mending_cost_per_day": mending_cost or 0,
                        "mechanic_cost_per_day": mechanic_cost or 0,
                        "electricity_cost_per_day": electricity_cost or 0,
                        "maintenance_cost_per_day": maintenance_cost or 0,
                        "miscellaneous_cost_per_day": misc_cost or 0,
                        "knots_capacity_per_day": knots_cap or 0,
                    }
                )
            messages.success(request, "Machine Operational Cost saved successfully.")
        
        # DELETE
        elif action == "delete":
            numbers = request.POST.getlist("machine_number")
            for number in numbers:
                if number:
                    MachineOperationalCost.objects.filter(machine_number=number).delete()
            messages.success(request, "Machine Operational Cost deleted successfully.")
    
    context = {
        "costs": MachineOperationalCost.objects.all(),
        "product_codes": Product.objects.values_list("code", flat=True).order_by("code"),
    }
    return render(request, "marania_invoice_app/machine_operational_cost.html", context)


@login_required
def additional_cost_view(request):
    if request.method == 'POST':
        action = request.POST.get("action")
        
        # SAVE / UPDATE
        if action == "save":
            # Additional Cost is a single record model
            transportation_cost = request.POST.get("transportation_cost_per_kg", 0)
            packing_cost = request.POST.get("packing_cost_per_kg", 0)
            waste_percentage = request.POST.get("waste_percentage", 2)
            
            # Get or create the single record (id=1)
            obj, created = AdditionalCost.objects.get_or_create(
                id=1,
                defaults={
                    "transportation_cost_per_kg": transportation_cost,
                    "packing_cost_per_kg": packing_cost,
                    "waste_percentage": waste_percentage,
                }
            )
            
            if not created:
                obj.transportation_cost_per_kg = transportation_cost
                obj.packing_cost_per_kg = packing_cost
                obj.waste_percentage = waste_percentage
                obj.save()
            
            messages.success(request, "Additional Cost saved successfully.")
    
    # Get the single record or create default
    cost_obj, _ = AdditionalCost.objects.get_or_create(
        id=1,
        defaults={
            "transportation_cost_per_kg": 0,
            "packing_cost_per_kg": 0,
            "waste_percentage": 2,
        }
    )
    
    context = {
        "cost": cost_obj,
    }
    return render(request, "marania_invoice_app/additional_cost.html", context)


@login_required
def production_entry_view(request):
    from .models import Production, Order, OrderSpecification, Product, MaterialConversionRatio, MachineOperationalCost
    import json

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "save":
            entries_raw = request.POST.get("entries_data")
            if entries_raw:
                entries = json.loads(entries_raw) if isinstance(entries_raw, str) else entries_raw
                saved = 0
                for entry in entries:
                    if not entry.get("machine"):
                        continue
                    production_date = entry.get("production_date") or None
                    if production_date:
                        from datetime import datetime
                        try:
                            production_date = datetime.strptime(production_date, "%Y-%m-%d").date()
                        except:
                            production_date = None
                    
                    product_code = (entry.get("product") or "").strip()
                    conversion = None
                    if product_code:
                        try:
                            conversion = MaterialConversionRatio.objects.get(material_code=product_code).conversion_ratio
                        except MaterialConversionRatio.DoesNotExist:
                            conversion = None
                    
                    quantity = float(entry.get("quantity") or 0)
                    conv = float(conversion) if conversion else 0
                    calc_weight = quantity * conv if conv else 0
                    
                    # Build remarks from twine rows
                    twine_rows_data = entry.get("twine_rows", [])
                    remarks = ""
                    if twine_rows_data:
                        remarks = json.dumps(twine_rows_data)
                    
                    Production.objects.create(
                        production_date=production_date,
                        customer=(entry.get("customer") or "").strip(),
                        specification=(entry.get("specification") or "").strip(),
                        reference=(entry.get("reference") or "").strip(),
                        mm=(entry.get("mm") or "").strip(),
                        md=(entry.get("md") or "").strip(),
                        product=product_code,
                        sel=(entry.get("sel") or "").strip(),
                        pw=(entry.get("pw") or "").strip(),
                        required_weight=quantity or None,
                        est_weight=float(entry.get("est_weight") or 0) or None,
                        quantity_unit=(entry.get("quantity_unit") or "KG").strip(),
                        machine=(entry.get("machine") or "").strip(),
                        knots_capacity_per_day=float(entry.get("knots_capacity_per_day") or 0) or None,
                        total_meshes=int(entry.get("total_meshes") or 0) or None,
                        addl_net_twine=float(entry.get("addl_net_twine") or 0) or None,
                         total_twine=float(entry.get("total_twine") or 0) or None,
                         total_daily_output=float(entry.get("total_daily_output") or 0) or None,
                         required_days=float(entry.get("required_days") or 0) or None,
                         conversion_factor=conversion,
                         calculated_weight=calc_weight or None,
                         remarks=remarks,
                    )
                    saved += 1
                messages.success(request, f"{saved} production entries saved.")

        elif action == "delete":
            pk = request.POST.get("production_key")
            if pk:
                Production.objects.filter(pk=pk).delete()
                messages.success(request, "Production entry deleted.")

        return redirect("production_entry")

    orders = Order.objects.exclude(status__in=["Completed", "Cancelled", "Rejected"]).select_related().prefetch_related("specifications")
    orders_data = []
    for o in orders:
        spec = o.specifications.first()
        orders_data.append({
            "order_key": o.order_key,
            "order_number": o.order_number,
            "customer": o.customer,
            "twine": o.twine,
            "quantity": str(o.quantity),
            "quantity_unit": o.quantity_unit or "KG",
            "unit_price": str(o.unit_price) if o.unit_price else "",
            "specification": f"{spec.mesh_size or ''}MM-{spec.mesh_depth or ''}MD-{spec.salvage or ''}SEL" if spec else "",
            "mm": str(spec.mesh_size) if spec and spec.mesh_size else "",
            "md": spec.mesh_depth if spec else "",
            "sel": spec.salvage if spec else "",
            "pw": spec.piece_weight if spec else "",
            "product_code": o.twine or "",
            "no_of_pcs": spec.no_of_pcs if spec else "",
        })

    products = Product.objects.all().order_by("code")
    machines = MachineOperationalCost.objects.all().order_by("machine_number")
    machines_json = [{"machine_number": m.machine_number, "number_of_shuttles": m.number_of_shuttles or 0, "knots_capacity_per_day": str(m.knots_capacity_per_day) if m.knots_capacity_per_day else ""} for m in machines]

    from .models import MaterialConversionRatio
    conversion_ratios = MaterialConversionRatio.objects.all().order_by("material_code")
    twine_options = [{"code": r.material_code, "ratio": str(r.conversion_ratio), "base_ratio": str(r.base_conversion_ratio), "multiplier": str(r.multiplier), "label": f"{r.material_code}-{r.conversion_ratio}"} for r in conversion_ratios]

    # Get saved production entries
    productions = Production.objects.all().select_related("order").order_by("-production_date", "-production_key")
    productions_data = []
    for p in productions:
        twine_rows = []
        if p.remarks:
            try:
                twine_rows = json.loads(p.remarks)
            except:
                pass
        productions_data.append({
            "production_key": p.production_key,
            "production_date": p.production_date.strftime("%Y-%m-%d") if p.production_date else "",
            "customer": p.customer,
            "specification": p.specification,
            "reference": p.reference,
            "mm": p.mm,
            "md": p.md,
            "product": p.product,
            "sel": p.sel,
            "pw": p.pw,
            "required_weight": str(p.required_weight) if p.required_weight else "",
            "est_weight": str(p.est_weight) if p.est_weight else "",
            "quantity_unit": p.quantity_unit or "KG",
            "machine": p.machine,
            "knots_capacity_per_day": str(p.knots_capacity_per_day) if p.knots_capacity_per_day else "",
            "total_meshes": str(p.total_meshes) if p.total_meshes else "",
            "addl_net_twine": str(p.addl_net_twine) if p.addl_net_twine else "",
            "total_twine": str(p.total_twine) if p.total_twine else "",
            "conversion_factor": str(p.conversion_factor) if p.conversion_factor else "",
            "calculated_weight": str(p.calculated_weight) if p.calculated_weight else "",
            "twine_rows": twine_rows,
            "total_daily_output": str(p.total_daily_output) if p.total_daily_output else "",
            "required_days": str(p.required_days) if p.required_days else "",
        })

    context = {
        "orders_json": orders_data,
        "products": products,
        "machines": machines,
        "machines_json": machines_json,
        "twine_options_json": twine_options,
        "productions": productions_data,
    }
    return render(request, "marania_invoice_app/production_entry.html", context)


@login_required
def load_production_view(request, pk):
    from .models import Production
    import json
    
    try:
        production = Production.objects.get(pk=pk)
        twine_rows = []
        if production.remarks:
            try:
                twine_rows = json.loads(production.remarks)
            except:
                pass
        
        data = {
            "production_key": production.production_key,
            "production_date": production.production_date.strftime("%Y-%m-%d") if production.production_date else "",
            "customer": production.customer,
            "specification": production.specification,
            "reference": production.reference,
            "mm": production.mm,
            "md": production.md,
            "product": production.product,
            "sel": production.sel,
            "pw": production.pw,
            "required_weight": str(production.required_weight) if production.required_weight else "",
            "est_weight": str(production.est_weight) if production.est_weight else "",
            "quantity_unit": production.quantity_unit or "KG",
            "machine": production.machine,
            "knots_capacity_per_day": str(production.knots_capacity_per_day) if production.knots_capacity_per_day else "",
            "total_meshes": str(production.total_meshes) if production.total_meshes else "",
            "addl_net_twine": str(production.addl_net_twine) if production.addl_net_twine else "",
            "total_twine": str(production.total_twine) if production.total_twine else "",
            "total_daily_output": str(production.total_daily_output) if production.total_daily_output else "",
            "required_days": str(production.required_days) if production.required_days else "",
            "conversion_factor": str(production.conversion_factor) if production.conversion_factor else "",
            "calculated_weight": str(production.calculated_weight) if production.calculated_weight else "",
            "twine_rows": twine_rows,
        }
        return JsonResponse(data)
    except Production.DoesNotExist:
        return JsonResponse({"error": "Production not found"}, status=404)


@login_required
def production_detail_view(request):
    from .models import Production

    productions = Production.objects.all().select_related("order")
    productions_data = []
    for p in productions:
        productions_data.append({
            "production_key": p.production_key,
            "production_date": str(p.production_date),
            "order_number": p.order.order_number if p.order else "",
            "customer": p.customer,
            "specification": p.specification or "",
            "reference": p.reference or "",
            "mm": p.mm or "",
            "md": p.md or "",
            "product": p.product or "",
            "sel": p.sel or "",
            "pw": p.pw or "",
            "est_weight": str(p.est_weight) if p.est_weight else "",
            "machine": p.machine or "",
            "knots_capacity_per_day": str(p.knots_capacity_per_day) if p.knots_capacity_per_day else "",
            "total_meshes": p.total_meshes or "",
            "addl_net_twine": str(p.addl_net_twine) if p.addl_net_twine else "",
            "total_twine": str(p.total_twine) if p.total_twine else "",
            "total_daily_output": str(p.total_daily_output) if p.total_daily_output else "",
            "required_days": str(p.required_days) if p.required_days else "",
            "remarks": p.remarks or "",
        })

    context = {
        "productions": productions_data,
    }
    return render(request, "marania_invoice_app/production_detail.html", context)


@login_required
def profit_analytics_view(request):
    from .models import ProfitAnalytics, Production, MachineOperationalCost, ProcessingCost, AdditionalCost

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "save":
            entries_raw = request.POST.get("entries_data")
            if entries_raw:
                entries = json.loads(entries_raw) if isinstance(entries_raw, str) else entries_raw
                saved = 0
                for entry in entries:
                    production_key = entry.get("production_key") or None
                    production_obj = None
                    if production_key:
                        try:
                            production_obj = Production.objects.get(pk=production_key)
                        except Production.DoesNotExist:
                            production_obj = None
                    profit_key = entry.get("profit_key") or None
                    defaults = {
                        "production": production_obj,
                        "profit_date": entry.get("profit_date") or None,
                        "customer": (entry.get("customer") or "").strip(),
                        "product": (entry.get("product") or "").strip(),
                        "machine": (entry.get("machine") or "").strip(),
                        "est_weight": float(entry.get("est_weight") or 0) or None,
                        "total_daily_output": float(entry.get("total_daily_output") or 0) or None,
                        "required_days": float(entry.get("required_days") or 0) or None,
                        "machine_operational_cost_per_day": float(entry.get("machine_operational_cost_per_day") or 0) or None,
                        "machine_operational_total": float(entry.get("machine_operational_total") or 0) or None,
                        "processing_cost_per_kg": float(entry.get("processing_cost_per_kg") or 0) or None,
                        "processing_total": float(entry.get("processing_total") or 0) or None,
                        "color_cost_per_kg": float(entry.get("color_cost_per_kg") or 0) or None,
                        "color_total": float(entry.get("color_total") or 0) or None,
                        "small_depth_size_cost_per_kg": float(entry.get("small_size_cost_per_kg") or 0) or None,
                        "small_size_total": float(entry.get("small_size_total") or 0) or None,
                        "additional_cost_per_kg": float(entry.get("additional_cost_per_kg") or 0) or None,
                        "additional_total": float(entry.get("additional_total") or 0) or None,
                        "raw_material_cost": float(entry.get("raw_material_cost") or 0) or None,
                        "raw_twine_data": entry.get("raw_twine_data", ""),
                        "total_cost": float(entry.get("total_cost") or 0) or None,
                        "sale_price_per_kg": float(entry.get("sale_price_per_kg") or 0) or None,
                        "total_revenue": float(entry.get("total_revenue") or 0) or None,
                        "total_profit": float(entry.get("total_profit") or 0) or None,
                        "profit_per_kg": float(entry.get("profit_per_kg") or 0) or None,
                        "profit_per_day": float(entry.get("profit_per_day") or 0) or None,
                        "profit_margin_pct": float(entry.get("profit_margin_pct") or 0) or None,
                        "remarks": (entry.get("remarks") or "").strip(),
                    }
                    if profit_key:
                        ProfitAnalytics.objects.filter(pk=profit_key).update(**defaults)
                    else:
                        ProfitAnalytics.objects.create(**defaults)
                    saved += 1
                messages.success(request, f"{saved} profit analytics saved.")

        elif action == "delete":
            pk = request.POST.get("profit_key")
            if pk:
                ProfitAnalytics.objects.filter(pk=pk).delete()
                messages.success(request, "Profit analytics deleted.")

        elif action == "delete_bulk":
            keys_raw = request.POST.get("profit_keys")
            if keys_raw:
                keys = json.loads(keys_raw)
                ProfitAnalytics.objects.filter(profit_key__in=keys).delete()
                messages.success(request, "Selected entries deleted.")

        return redirect("profit_analytics")

    # Get all production analytics entries for selection
    productions = Production.objects.all().order_by("-production_date", "-production_key")
    productions_data = []
    for p in productions:
        try:
            twine_rows = json.loads(p.remarks) if p.remarks else []
        except (json.JSONDecodeError, TypeError):
            twine_rows = []
        productions_data.append({
            "production_key": p.production_key,
            "production_date": str(p.production_date) if p.production_date else "",
            "customer": p.customer,
            "specification": p.specification or "",
            "product": p.product or "",
            "machine": p.machine or "",
            "mm": str(p.mm) if p.mm else "",
            "md": str(p.md) if p.md else "",
            "est_weight": str(p.est_weight) if p.est_weight else "",
            "knots_capacity_per_day": str(p.knots_capacity_per_day) if p.knots_capacity_per_day else "",
            "addl_net_twine": str(p.addl_net_twine) if p.addl_net_twine else "",
            "total_daily_output": str(p.total_daily_output) if p.total_daily_output else "",
            "required_days": str(p.required_days) if p.required_days else "",
            "twine_rows": twine_rows,
        })

    # Get machine operational costs
    machines = MachineOperationalCost.objects.all().order_by("machine_number")
    machines_data = []
    for m in machines:
        total_cost_per_day = sum(filter(None, [
            m.operator_cost_per_day or 0,
            m.bobbin_winder_cost_per_day or 0,
            m.mending_cost_per_day or 0,
            m.mechanic_cost_per_day or 0,
            m.electricity_cost_per_day or 0,
            m.maintenance_cost_per_day or 0,
            m.miscellaneous_cost_per_day or 0,
        ]))
        machines_data.append({
            "machine_number": m.machine_number,
            "total_cost_per_day": str(total_cost_per_day),
        })

    # Get processing costs
    processing_costs = ProcessingCost.objects.all().order_by("material_code")
    processing_data = [{"code": pc.material_code, "cost_per_kg": str(pc.processing_cost_per_kg), "color_cost": str(pc.color_cost_per_kg), "small_size_cost": str(pc.small_depth_size_cost_per_kg)} for pc in processing_costs]

    # Get materials for twine name lookup
    from .models import Materials
    materials = Materials.objects.all()
    materials_data = [{"code": m.code, "name": m.name or ""} for m in materials]

    # Get additional costs
    additional = AdditionalCost.objects.first()
    additional_data = {
        "transportation": str(additional.transportation_cost_per_kg) if additional else "",
        "packing": str(additional.packing_cost_per_kg) if additional else "",
        "waste": str(additional.waste_percentage) if additional else "",
    }

    # Get saved profit analytics
    profits = ProfitAnalytics.objects.all()
    profits_data = []
    for pr in profits:
        profits_data.append({
            "profit_key": pr.profit_key,
            "profit_date": str(pr.profit_date) if pr.profit_date else "",
            "customer": pr.customer or "",
            "product": pr.product or "",
            "machine": pr.machine or "",
            "est_weight": str(pr.est_weight) if pr.est_weight else "",
            "total_daily_output": str(pr.total_daily_output) if pr.total_daily_output else "",
            "required_days": str(pr.required_days) if pr.required_days else "",
            "machine_operational_cost_per_day": str(pr.machine_operational_cost_per_day) if pr.machine_operational_cost_per_day else "",
            "machine_operational_total": str(pr.machine_operational_total) if pr.machine_operational_total else "",
            "processing_cost_per_kg": str(pr.processing_cost_per_kg) if pr.processing_cost_per_kg else "",
            "processing_total": str(pr.processing_total) if pr.processing_total else "",
            "color_cost_per_kg": str(pr.color_cost_per_kg) if pr.color_cost_per_kg else "",
            "color_total": str(pr.color_total) if pr.color_total else "",
            "small_size_cost_per_kg": str(pr.small_depth_size_cost_per_kg) if pr.small_depth_size_cost_per_kg else "",
            "small_size_total": str(pr.small_size_total) if pr.small_size_total else "",
            "additional_cost_per_kg": str(pr.additional_cost_per_kg) if pr.additional_cost_per_kg else "",
            "additional_total": str(pr.additional_total) if pr.additional_total else "",
            "raw_material_cost": str(pr.raw_material_cost) if pr.raw_material_cost else "",
            "raw_twine_data": pr.raw_twine_data or "",
            "total_cost": str(pr.total_cost) if pr.total_cost else "",
            "sale_price_per_kg": str(pr.sale_price_per_kg) if pr.sale_price_per_kg else "",
            "total_revenue": str(pr.total_revenue) if pr.total_revenue else "",
            "total_profit": str(pr.total_profit) if pr.total_profit else "",
            "profit_per_kg": str(pr.profit_per_kg) if pr.profit_per_kg else "",
            "profit_per_day": str(pr.profit_per_day) if pr.profit_per_day else "",
            "profit_margin_pct": str(pr.profit_margin_pct) if pr.profit_margin_pct else "",
            "remarks": pr.remarks or "",
        })

    context = {
        "productions_json": productions_data,
        "machines_json": machines_data,
        "processing_json": processing_data,
        "additional_json": additional_data,
        "materials_json": materials_data,
        "profits": profits_data,
    }
    return render(request, "marania_invoice_app/profit_analytics.html", context)


@login_required
def piece_weight_analyser_view(request):
    from .models import Order, OrderSpecification, Product, MaterialConversionRatio, PieceWeightAnalyser
    import json

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "save":
            data_raw = request.POST.get("save_data")
            if data_raw:
                data = json.loads(data_raw) if isinstance(data_raw, str) else data_raw
                PieceWeightAnalyser.objects.create(
                    product=data.get("product", ""),
                    customer=data.get("customer", ""),
                    specification=data.get("specification", ""),
                    mm=data.get("mm", ""),
                    md=data.get("md", ""),
                    sel=data.get("sel", ""),
                    pw=data.get("pw", ""),
                    quantity=data.get("quantity", ""),
                    unit=data.get("unit", "KG"),
                    addl_mesh_size=float(data.get("addl_mesh_size") or 0) or None,
                    groups_data=json.dumps(data.get("groups", [])),
                    exp_piece_weight=float(data.get("exp_piece_weight") or 0) or None,
                    multiplier=float(data.get("multiplier") or 1),
                    knot_count=float(data.get("knot_count") or 0) or None,
                    total_pcs=int(data.get("total_pcs") or 0) or None,
                    all_pcs_weight=float(data.get("all_pcs_weight") or 0) or None,
                    all_specs=data.get("all_specs"),
                    order_date=data.get("order_date", ""),
                    order_number=data.get("order_number", ""),
                    order_key=int(data.get("order_key") or 0) or None,
                )
                messages.success(request, "Piece Weight Analyser entry saved.")

        elif action == "delete":
            pk = request.POST.get("pwa_key")
            if pk:
                PieceWeightAnalyser.objects.filter(pk=pk).delete()
                messages.success(request, "Piece Weight Analyser entry deleted.")

        return redirect("piece_weight_analyser")

    orders = Order.objects.exclude(status__in=["Completed", "Cancelled", "Rejected"]).select_related().prefetch_related("specifications")
    orders_data = []
    for o in orders:
        specs = o.specifications.all()
        specs_list = []
        for sp in specs:
            specs_list.append({
                "mesh_size": str(sp.mesh_size) if sp.mesh_size else "",
                "mesh_depth": sp.mesh_depth or "",
                "salvage": sp.salvage or "",
                "piece_weight": sp.piece_weight or "",
                "no_of_pcs": sp.no_of_pcs or "",
                "colour": sp.colour or "",
            })
        first_spec = specs.first()
        orders_data.append({
            "order_key": o.order_key,
            "order_number": o.order_number,
            "customer": o.customer,
            "twine": o.twine,
            "quantity": str(o.quantity),
            "quantity_unit": o.quantity_unit or "KG",
            "order_date": o.order_date.strftime("%Y-%m-%d") if o.order_date else "",
            "specification": f"{first_spec.mesh_size or ''}MM-{first_spec.mesh_depth or ''}MD-{first_spec.salvage or ''}SEL" if first_spec else "",
            "mm": str(first_spec.mesh_size) if first_spec and first_spec.mesh_size else "",
            "md": first_spec.mesh_depth if first_spec else "",
            "sel": first_spec.salvage if first_spec else "",
            "pw": first_spec.piece_weight if first_spec else "",
            "product_code": o.twine or "",
            "all_specs": specs_list,
        })

    products = Product.objects.all().order_by("code")

    conversion_ratios = MaterialConversionRatio.objects.all().order_by("material_code")
    twine_options = [{"code": r.material_code, "ratio": str(r.conversion_ratio), "base_ratio": str(r.base_conversion_ratio), "multiplier": str(r.multiplier), "label": f"{r.material_code}-{r.conversion_ratio}"} for r in conversion_ratios]

    saved_entries = PieceWeightAnalyser.objects.all()
    saved_data = []
    for s in saved_entries:
        saved_data.append({
            "pwa_key": s.pwa_key,
            "product": s.product or "",
            "customer": s.customer or "",
            "specification": s.specification or "",
            "mm": s.mm or "",
            "md": s.md or "",
            "sel": s.sel or "",
            "pw": s.pw or "",
            "quantity": s.quantity or "",
            "unit": s.unit or "KG",
            "addl_mesh_size": str(s.addl_mesh_size) if s.addl_mesh_size else "",
            "groups_data": s.groups_data or "[]",
            "exp_piece_weight": str(s.exp_piece_weight) if s.exp_piece_weight else "",
            "multiplier": str(s.multiplier) if s.multiplier else "1",
            "knot_count": str(s.knot_count) if s.knot_count else "",
            "total_pcs": s.total_pcs or 0,
            "all_pcs_weight": str(s.all_pcs_weight) if s.all_pcs_weight else "",
            "all_specs": s.all_specs or [],
            "order_date": s.order_date or "",
            "order_number": s.order_number or "",
            "order_key": s.order_key or "",
            "created_at": s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else "",
        })

    context = {
        "orders_json": orders_data,
        "products": products,
        "twine_options_json": twine_options,
        "saved_entries": saved_data,
    }
    return render(request, "marania_invoice_app/piece_weight_analyser.html", context)


@login_required
def load_pwa_view(request, pk):
    from .models import PieceWeightAnalyser, Order, OrderSpecification
    import json

    try:
        entry = PieceWeightAnalyser.objects.get(pk=pk)
        groups = []
        if entry.groups_data:
            try:
                groups = json.loads(entry.groups_data)
            except:
                pass

        all_specs = entry.all_specs or []
        order_date = entry.order_date or ""
        order_number = entry.order_number or ""

        if not all_specs and entry.order_key:
            try:
                order = Order.objects.get(pk=entry.order_key)
                order_date = order.order_date.strftime("%Y-%m-%d") if order.order_date else ""
                order_number = order.order_number or ""
                for sp in order.specifications.all():
                    all_specs.append({
                        "mesh_size": str(sp.mesh_size) if sp.mesh_size else "",
                        "mesh_depth": sp.mesh_depth or "",
                        "salvage": sp.salvage or "",
                        "piece_weight": sp.piece_weight or "",
                        "no_of_pcs": sp.no_of_pcs or "",
                        "colour": sp.colour or "",
                    })
            except Order.DoesNotExist:
                pass

        data = {
            "pwa_key": entry.pwa_key,
            "product": entry.product or "",
            "customer": entry.customer or "",
            "specification": entry.specification or "",
            "mm": entry.mm or "",
            "md": entry.md or "",
            "sel": entry.sel or "",
            "pw": entry.pw or "",
            "quantity": entry.quantity or "",
            "unit": entry.unit or "KG",
            "addl_mesh_size": str(entry.addl_mesh_size) if entry.addl_mesh_size else "",
            "groups": groups,
            "exp_piece_weight": str(entry.exp_piece_weight) if entry.exp_piece_weight else "",
            "multiplier": str(entry.multiplier) if entry.multiplier else "1",
            "knot_count": str(entry.knot_count) if entry.knot_count else "",
            "total_pcs": entry.total_pcs or 0,
            "all_pcs_weight": str(entry.all_pcs_weight) if entry.all_pcs_weight else "",
            "all_specs": all_specs,
            "order_date": order_date,
            "order_number": order_number,
            "order_key": entry.order_key or "",
        }
        return JsonResponse(data)
    except PieceWeightAnalyser.DoesNotExist:
        return JsonResponse({"error": "Entry not found"}, status=404)


@login_required
def outstanding_payment_list_view(request):
    from .models import Parties, Invoice, PaymentReceipt, PaymentAllocation, OpeningBalance, Expense, SettlementInvoice
    from django.db.models import Sum
    from django.http import HttpResponse
    import csv
    import json

    parties = Parties.objects.all().order_by('name')
    from datetime import date
    today = date.today()
    today_str = today.strftime("%d %b %Y")
    export_format = request.GET.get('export', None)

    # Customer filter
    customer_filter = request.GET.get('customer', '')
    if customer_filter:
        parties = parties.filter(code=customer_filter)

    customer_summaries = []

    for party in parties:
        code = party.code
        entries = []

        # Opening balances with outstanding balance > 0
        for ob in OpeningBalance.objects.filter(customer__code=code):
            alloc_total = PaymentAllocation.objects.filter(
                opening_balance=ob
            ).aggregate(total=Sum('allocated_amount'))['total'] or 0
            balance = float(ob.amount) - float(alloc_total)
            if balance > 0:
                dr_cr = 'Dr' if ob.balance_type == 'Debit' else 'Cr'
                ref_no = ob.ob_number or f'OBAL-{ob.opening_balance_id}'
                comment = ob.display_comment or ''
                desc = 'Opening Balance'
                if comment:
                    desc += f' ({comment})'
                entries.append({
                    'entry_date': str(ob.opening_date),
                    'ref_number': ref_no,
                    'description': desc,
                    'type': dr_cr,
                    'amount': round(balance, 2),
                })

        # Unpaid invoices (balance > 0)
        for inv in Invoice.objects.filter(customer_code=code):
            alloc_total = PaymentAllocation.objects.filter(
                invoice=inv
            ).aggregate(total=Sum('allocated_amount'))['total'] or 0
            balance = float(inv.gross_total) - float(alloc_total)
            if balance > 0:
                entries.append({
                    'entry_date': str(inv.invoice_date) if inv.invoice_date else '',
                    'ref_number': inv.invoice_number,
                    'description': 'Invoice issued',
                    'type': 'Dr',
                    'amount': round(balance, 2),
                })

        # Customer expenses with outstanding balance > 0
        for exp in Expense.objects.filter(bill_to='Customer'):
            vendor = exp.vendor or ''
            if vendor and vendor != 'Not Applicable':
                exp_code = vendor.split('-')[0].strip()
                if exp_code == code:
                    alloc_total = PaymentAllocation.objects.filter(
                        expense=exp
                    ).aggregate(total=Sum('allocated_amount'))['total'] or 0
                    balance = float(exp.expense_amount) - float(alloc_total)
                    if balance > 0:
                        comment = exp.display_comment or ''
                        desc = exp.expense_category or 'Expense'
                        if comment:
                            desc += f' ({comment})'
                        entries.append({
                            'entry_date': str(exp.expense_date) if exp.expense_date else '',
                            'ref_number': f'EXP-{exp.expense_id}',
                            'description': desc,
                            'type': 'Dr',
                            'amount': round(balance, 2),
                        })

        # Settlement invoices with outstanding balance > 0
        for si in SettlementInvoice.objects.filter(customer__code=code):
            alloc_total = PaymentAllocation.objects.filter(
                settlement_invoice=si
            ).aggregate(total=Sum('allocated_amount'))['total'] or 0
            balance = float(si.amount) - float(alloc_total)
            if balance > 0:
                comment = si.display_comment or ''
                desc = 'SI'
                if comment:
                    desc += f' ({comment})'
                entries.append({
                    'entry_date': str(si.settlement_date) if si.settlement_date else '',
                    'ref_number': si.settlement_invoice_number,
                    'description': desc,
                    'type': 'Dr',
                    'amount': round(balance, 2),
                })

        # Unallocated payment receipts (available balance > 0)
        for receipt in PaymentReceipt.objects.filter(customer__code=code):
            alloc_total = PaymentAllocation.objects.filter(
                payment=receipt
            ).aggregate(total=Sum('allocated_amount'))['total'] or 0
            available = float(receipt.total_received) - float(alloc_total)
            if available > 0:
                ttype = receipt.transaction_type or 'Payment'
                comment = receipt.display_comment or ''
                if ttype == 'Payment':
                    desc = 'Payment Received'
                    entry_type = 'Cr'
                elif ttype == 'Adjustment(Cr)':
                    desc = 'Payment Adjustment(Cr)'
                    entry_type = 'Cr'
                elif ttype == 'Adjustment(Dr)':
                    desc = 'Payment Adjustment(Dr)'
                    entry_type = 'Dr'
                else:
                    desc = 'Received Payment'
                    entry_type = 'Cr'
                if comment:
                    desc += f' ({comment})'
                entries.append({
                    'entry_date': str(receipt.payment_date) if receipt.payment_date else '',
                    'ref_number': receipt.receipt_no,
                    'description': desc,
                    'type': entry_type,
                    'amount': round(available, 2),
                })

        if not entries:
            continue

        # Sort by date
        entries.sort(key=lambda e: e['entry_date'])

        # Compute running balance
        running = 0.0
        for e in entries:
            if e['type'] == 'Dr':
                running += e['amount']
            else:
                running -= e['amount']
            e['running_balance'] = round(running, 2)

        outstanding_balance = running

        customer_summaries.append({
            'customer_name': party.name,
            'entries': entries,
            'outstanding_balance': outstanding_balance,
        })

    # Sort: positive outstanding descending, then credit (negative) at bottom
    sort_order = request.GET.get('sort', 'desc')
    if sort_order == 'desc':
        # Descending: positive outstanding first (highest first), then credit (negative) at bottom
        customer_summaries.sort(key=lambda c: (0 if c['outstanding_balance'] > 0 else 1, -abs(c['outstanding_balance'])))
    else:
        # Ascending: credit (negative) first (most negative first), then positive outstanding
        customer_summaries.sort(key=lambda c: (1 if c['outstanding_balance'] > 0 else 0, abs(c['outstanding_balance'])))

    total_outstanding = sum(c['outstanding_balance'] for c in customer_summaries if c['outstanding_balance'] > 0)
    total_credit = sum(c['outstanding_balance'] for c in customer_summaries if c['outstanding_balance'] < 0)

    # Export to CSV
    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="outstanding_payment_list.csv"'

        writer = csv.writer(response)
        writer.writerow(['Customer Name', 'Date', 'Invoice/Ref #', 'Description', 'Type', 'Amount', 'Running Balance', 'Outstanding Balance'])

        for cs in customer_summaries:
            for entry in cs['entries']:
                writer.writerow([
                    cs['customer_name'],
                    entry['entry_date'],
                    entry['ref_number'],
                    entry['description'],
                    entry['type'],
                    entry['amount'],
                    entry.get('running_balance', ''),
                    '',
                ])
            writer.writerow(['', '', '', '', '', '', 'Outstanding Balance:', cs['outstanding_balance']])
            writer.writerow([])

        writer.writerow([])
        writer.writerow(['', '', '', '', '', '', 'Total Outstanding:', total_outstanding])
        writer.writerow(['', '', '', '', '', '', 'Total Credit:', total_credit])

        return response

    # Export to PDF
    if export_format == 'pdf':
        from django.template.loader import render_to_string
        from weasyprint import HTML

        html_string = render_to_string('marania_invoice_app/outstanding_payment_list_pdf.html', {
            'customer_summaries': customer_summaries,
            'today': today,
            'total_outstanding': total_outstanding,
            'total_credit': total_credit,
        })

        html = HTML(string=html_string)
        pdf_file = html.write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="outstanding_payment_list.pdf"'
        return response

    return render(request, 'marania_invoice_app/outstanding_payment_list.html', {
        'customer_summaries': customer_summaries,
        'all_parties': Parties.objects.all().order_by('name'),
        'selected_customer': customer_filter,
        'today': today_str,
        'sort_order': sort_order,
        'total_outstanding': total_outstanding,
        'total_credit': total_credit,
    })


# =======================
# Price List Generator
# =======================

@login_required
def price_list_generator(request):
    settings_obj = CompanySettings.objects.get(id=1)
    products = Product.objects.all().order_by("code")
    configs = PriceListConfiguration.objects.all().order_by("-created_at")
    machines = MachineOperationalCost.objects.all().order_by("machine_number")

    default_colour_price = float(settings_obj.colour_charge)
    default_small_mesh_size = int(settings_obj.small_mesh_size)
    default_small_mesh_price = float(settings_obj.small_mesh_size_charge)

    default_additional_cost = Decimal("0")
    addl = AdditionalCost.objects.first()
    if addl:
        default_additional_cost = addl.transportation_cost_per_kg + addl.packing_cost_per_kg

    configs_json = []
    for c in configs:
        configs_json.append({
            "price_list_key": c.price_list_key,
            "product_code": c.product_code or "",
            "twine_price": float(c.twine_price),
            "gst_included": c.gst_included,
            "colour_price_per_kg": float(c.colour_price_per_kg),
            "additional_cost_starting_depth_md": c.additional_cost_starting_depth_md,
            "small_mesh_depth_price_per_kg": float(c.small_mesh_depth_price_per_kg),
            "processing_cost_per_kg": float(c.processing_cost_per_kg),
            "additional_cost_per_kg": float(c.additional_cost_per_kg),
            "machine_number": c.machine_number or "",
            "mesh_depth": float(c.mesh_depth),
            "daily_profit_values": json.loads(c.daily_profit_values) if c.daily_profit_values else [],
            "mesh_size_ranges": json.loads(c.mesh_size_ranges) if c.mesh_size_ranges else [],
            "created_at": c.created_at.strftime("%d-%b-%Y %H:%M") if c.created_at else "",
        })

    if request.method == "POST":
        action = request.POST.get("action", "save")

        if action == "delete":
            pk = request.POST.get("edit_price_list_key")
            if pk:
                PriceListConfiguration.objects.filter(price_list_key=pk).delete()
                messages.success(request, "Configuration deleted successfully.")
            return redirect("price_list_generator")

        product_code = request.POST.get("product_code", "").strip()
        twine_price = request.POST.get("twine_price", "0")
        gst_included = request.POST.get("gst_included") == "on"
        colour_price = request.POST.get("colour_price_per_kg", "10")
        small_mesh_size_val = request.POST.get("additional_cost_starting_depth_md", "50")
        small_mesh_price = request.POST.get("small_mesh_depth_price_per_kg", "10")
        processing_cost = request.POST.get("processing_cost_per_kg", "0")
        additional_cost = request.POST.get("additional_cost_per_kg", "0")
        machine_number = request.POST.get("machine_number", "").strip()
        mesh_depth_val = request.POST.get("mesh_depth", "0")
        daily_profit_raw = request.POST.get("daily_profit_values", "[]")
        mesh_ranges_raw = request.POST.get("mesh_size_ranges", "[]")

        try:
            twine_price_dec = Decimal(twine_price)
        except Exception:
            twine_price_dec = Decimal("0")
        try:
            colour_price_dec = Decimal(colour_price)
        except Exception:
            colour_price_dec = Decimal("10")
        try:
            small_mesh_size_int = int(small_mesh_size_val)
        except Exception:
            small_mesh_size_int = 50
        try:
            small_mesh_price_dec = Decimal(small_mesh_price)
        except Exception:
            small_mesh_price_dec = Decimal("10")
        try:
            processing_cost_dec = Decimal(processing_cost)
        except Exception:
            processing_cost_dec = Decimal("0")
        try:
            additional_cost_dec = Decimal(additional_cost)
        except Exception:
            additional_cost_dec = Decimal("0")
        try:
            mesh_depth_dec = Decimal(mesh_depth_val)
        except Exception:
            mesh_depth_dec = Decimal("0")

        if not product_code:
            messages.error(request, "Product is required.")
            return redirect("price_list_generator")

        try:
            daily_profits = json.loads(daily_profit_raw)
        except Exception:
            daily_profits = []
        try:
            mesh_ranges = json.loads(mesh_ranges_raw)
        except Exception:
            mesh_ranges = []

        if not daily_profits:
            messages.error(request, "At least one daily profit value is required.")
            return redirect("price_list_generator")
        if not mesh_ranges:
            messages.error(request, "At least one mesh size range is required.")
            return redirect("price_list_generator")

        product_obj = Product.objects.filter(code=product_code).first()

        pk_edit = request.POST.get("edit_price_list_key")
        if pk_edit:
            try:
                config = PriceListConfiguration.objects.get(price_list_key=pk_edit)
                config.product = product_obj
                config.product_code = product_code
                config.twine_price = twine_price_dec
                config.gst_included = gst_included
                config.colour_price_per_kg = colour_price_dec
                config.additional_cost_starting_depth_md = small_mesh_size_int
                config.small_mesh_depth_price_per_kg = small_mesh_price_dec
                config.processing_cost_per_kg = processing_cost_dec
                config.additional_cost_per_kg = additional_cost_dec
                config.machine_number = machine_number
                config.mesh_depth = mesh_depth_dec
                config.daily_profit_values = json.dumps(daily_profits)
                config.mesh_size_ranges = json.dumps(mesh_ranges)
                config.save()
                messages.success(request, "Configuration updated successfully.")
            except PriceListConfiguration.DoesNotExist:
                messages.error(request, "Configuration not found.")
        else:
            PriceListConfiguration.objects.create(
                product=product_obj,
                product_code=product_code,
                twine_price=twine_price_dec,
                gst_included=gst_included,
                colour_price_per_kg=colour_price_dec,
                additional_cost_starting_depth_md=small_mesh_size_int,
                small_mesh_depth_price_per_kg=small_mesh_price_dec,
                processing_cost_per_kg=processing_cost_dec,
                additional_cost_per_kg=additional_cost_dec,
                machine_number=machine_number,
                mesh_depth=mesh_depth_dec,
                daily_profit_values=json.dumps(daily_profits),
                mesh_size_ranges=json.dumps(mesh_ranges),
            )
            messages.success(request, "Configuration saved successfully.")

        return redirect("price_list_generator")

    return render(request, "marania_invoice_app/price_list_generator.html", {
        "products": products,
        "configs": configs,
        "configs_json": json.dumps(configs_json),
        "machines": machines,
        "default_colour_price": default_colour_price,
        "default_small_mesh_size": default_small_mesh_size,
        "default_small_mesh_price": default_small_mesh_price,
        "default_additional_cost": float(default_additional_cost),
    })


@login_required
def load_price_list_config(request, pk):
    try:
        config = PriceListConfiguration.objects.get(price_list_key=pk)
        return JsonResponse({
            "price_list_key": config.price_list_key,
            "product_code": config.product_code or "",
            "twine_price": float(config.twine_price),
            "gst_included": config.gst_included,
            "colour_price_per_kg": float(config.colour_price_per_kg),
            "additional_cost_starting_depth_md": config.additional_cost_starting_depth_md,
            "small_mesh_depth_price_per_kg": float(config.small_mesh_depth_price_per_kg),
            "processing_cost_per_kg": float(config.processing_cost_per_kg),
            "additional_cost_per_kg": float(config.additional_cost_per_kg),
            "machine_number": config.machine_number or "",
            "mesh_depth": float(config.mesh_depth),
            "daily_profit_values": json.loads(config.daily_profit_values) if config.daily_profit_values else [],
            "mesh_size_ranges": json.loads(config.mesh_size_ranges) if config.mesh_size_ranges else [],
        })
    except PriceListConfiguration.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)


@login_required
def view_price_list(request, pk):
    try:
        config = PriceListConfiguration.objects.get(price_list_key=pk)
    except PriceListConfiguration.DoesNotExist:
        messages.error(request, "Configuration not found.")
        return redirect("price_list_generator")

    daily_profits = json.loads(config.daily_profit_values) if config.daily_profit_values else []
    mesh_ranges = json.loads(config.mesh_size_ranges) if config.mesh_size_ranges else []

    machine_cost_per_day = Decimal("0")
    knot_capacity_per_day = Decimal("0")
    if config.machine_number:
        try:
            moc = MachineOperationalCost.objects.get(machine_number=config.machine_number)
            machine_cost_per_day = (moc.operator_cost_per_day + moc.bobbin_winder_cost_per_day +
                                    moc.mending_cost_per_day + moc.mechanic_cost_per_day +
                                    moc.electricity_cost_per_day + moc.maintenance_cost_per_day +
                                    moc.miscellaneous_cost_per_day)
            knot_capacity_per_day = moc.knots_capacity_per_day or Decimal("0")
        except MachineOperationalCost.DoesNotExist:
            pass

    processing_cost_per_kg = config.processing_cost_per_kg or Decimal("0")
    additional_cost_per_kg = config.additional_cost_per_kg or Decimal("0")

    waste_percentage = Decimal("0")
    addl = AdditionalCost.objects.first()
    if addl:
        waste_percentage = addl.waste_percentage or Decimal("0")

    twine_price_with_waste = config.twine_price * (Decimal("1") + waste_percentage / Decimal("100"))

    conversion_factor = Decimal("0")
    if config.product and config.product.material:
        try:
            mcr = MaterialConversionRatio.objects.get(material_code=config.product.material.code)
            conversion_factor = mcr.conversion_ratio
        except MaterialConversionRatio.DoesNotExist:
            pass

    price_list_rows = []
    for mesh_range in mesh_ranges:
        mesh_start = int(mesh_range.get("start", 0))
        mesh_end = int(mesh_range.get("end", 0))
        range_label = f"{mesh_start}\u2013{mesh_end}"
        mesh_size_mid = Decimal(str((mesh_start + mesh_end) / 2))

        daily_production = Decimal("0")
        if conversion_factor > 0 and mesh_size_mid > 0 and config.mesh_depth > 0 and knot_capacity_per_day > 0:
            daily_production = conversion_factor * mesh_size_mid * config.mesh_depth * knot_capacity_per_day / Decimal("1000")

        for dp in daily_profits:
            profit_label = dp.get("label", "")
            profit_value = Decimal(str(dp.get("value", 0)))

            if daily_production > 0:
                machine_cost_per_kg = machine_cost_per_day / daily_production
            else:
                machine_cost_per_kg = Decimal("0")

            per_kg_cost = (machine_cost_per_kg + processing_cost_per_kg +
                           additional_cost_per_kg + twine_price_with_waste)

            if daily_production > 0:
                profit_per_kg = profit_value / daily_production
            else:
                profit_per_kg = Decimal("0")

            calculated_price = per_kg_cost + profit_per_kg

            if config.additional_cost_starting_depth_md and mesh_end <= config.additional_cost_starting_depth_md:
                calculated_price += config.small_mesh_depth_price_per_kg

            if config.gst_included:
                gst_rate = company_settings.igst if company_settings.igst else Decimal("0")
                if gst_rate == 0:
                    gst_rate = (company_settings.cgst or Decimal("0")) + (company_settings.sgst or Decimal("0"))
                if gst_rate > 0:
                    calculated_price = calculated_price / (Decimal("1") + gst_rate / Decimal("100"))

            price_list_rows.append({
                "mesh_range": range_label,
                "mesh_start": mesh_start,
                "mesh_end": mesh_end,
                "profit_label": profit_label,
                "profit_value": round(float(profit_per_kg), 2),
                "calculated_price": round(float(calculated_price), 2),
                "daily_production": round(float(daily_production), 2),
            })

    price_list_rows.sort(key=lambda r: (r["mesh_start"], r["profit_value"]))

    return render(request, "marania_invoice_app/price_list_view.html", {
        "config": config,
        "price_list_rows": price_list_rows,
    })


@login_required
def get_twine_price_for_product(request):
    product_code = request.GET.get("product_code", "").strip()
    if not product_code:
        return JsonResponse({"twine_price": ""})

    product = Product.objects.filter(code=product_code).first()
    if not product or not product.material:
        return JsonResponse({"twine_price": ""})

    material_code = product.material.code
    latest_purchase = Purchase.objects.filter(
        material_code=material_code,
        is_twine=True
    ).order_by("-delivery_date", "-purchase_key").first()

    if latest_purchase and latest_purchase.unit_price is not None:
        return JsonResponse({"twine_price": float(latest_purchase.unit_price)})

    return JsonResponse({"twine_price": ""})


@login_required
def get_machine_for_product(request):
    product_code = request.GET.get("product_code", "").strip()
    if not product_code:
        return JsonResponse({"machine_number": "", "mesh_depth": ""})

    moc = MachineOperationalCost.objects.filter(running_product_code=product_code).first()
    if moc:
        return JsonResponse({
            "machine_number": moc.machine_number,
            "mesh_depth": moc.number_of_shuttles,
        })

    return JsonResponse({"machine_number": "", "mesh_depth": ""})


@login_required
def get_processing_cost_for_product(request):
    product_code = request.GET.get("product_code", "").strip()
    if not product_code:
        return JsonResponse({"processing_cost_per_kg": ""})

    product = Product.objects.filter(code=product_code).first()
    if not product or not product.material:
        return JsonResponse({"processing_cost_per_kg": ""})

    try:
        pc = ProcessingCost.objects.get(material_code=product.material.code)
        return JsonResponse({"processing_cost_per_kg": float(pc.processing_cost_per_kg)})
    except ProcessingCost.DoesNotExist:
        return JsonResponse({"processing_cost_per_kg": ""})

    moc = MachineOperationalCost.objects.filter(running_product_code=product_code).first()
    if moc:
        return JsonResponse({
            "machine_number": moc.machine_number,
            "mesh_depth": moc.number_of_shuttles,
        })

    return JsonResponse({"machine_number": "", "mesh_depth": ""})

