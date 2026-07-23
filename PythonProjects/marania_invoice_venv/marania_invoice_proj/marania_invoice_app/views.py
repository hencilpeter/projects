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

    # -------- LATEST CUSTOMERS --------
    latest_customers = Parties.objects.order_by("-created_at")[:5]

    # -------- RECENT INVOICES --------
    recent_invoices = Invoice.objects.order_by("-invoice_date")[:5]

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

        "latest_customers": latest_customers,
        "recent_invoices": recent_invoices,

        "invoice_months": invoice_months,
        "invoice_counts": invoice_counts,
        "total_gst_amount": total_gst_amount,
        "total_amount_with_gst":total_amount_with_gst,

        "catalog_groups": catalog_groups,
        "catalog_group_counts": catalog_group_counts,
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

    AUTO_FIELDS = {"id", "created_at", "updated_at"}

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
                if rel_field =="id": # TODO- fix the issue later
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
        for row in reader:
            save(row)

    # ---------- JSON ----------
    elif file_type == "json":
        records = json.load(file)
        model.objects.all().delete()
        for record in records:
            save(record)

    else:
        raise ValueError("Unsupported file type")
    


@transaction.atomic
def import_data(model_name, file_type, file):
    model = MODEL_REGISTRY[model_name]

    AUTO_FIELDS = {"id", "created_at", "updated_at"}
    UNIQUE_KEY = "code"  # explicitly use 'code' as lookup
    if model_name == 'Invoice':
        UNIQUE_KEY = "invoice_number"


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
                if rel_field == "id": #TODO - temp fix 
                    rel_field = 'code' 
                # elif model_name == 'Invoice':
                #     rel_field = "invoice_number"
                

                # Extract code from CSV like "LINGF-LINGESWARI FILAMENTS"
                if  str(value) != "":
                    code_value = str(value).split("-", 1)[0].strip()
                else:
                    code_value =""

                try:
                    if code_value == "":
                        clean[key] = ""    
                    else:
                        clean[key] = rel_model.objects.get(**{rel_field: code_value})
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
        # print(f'raw file {raw}')
        decoded = None
        for enc in ("utf-8-sig", "utf-16", "cp1252", "latin1"):
            try:
                decoded = raw.decode(enc)
                #print(f'decoded {decoded}')
                break
            except UnicodeDecodeError:
                continue
        if decoded is None:
            raise ValueError("Unable to decode CSV file")

        reader = csv.DictReader(io.StringIO(decoded))
        for row in reader:
            #print(f'row {row}')
            save(row)
        #print("call done...")

    # ---------- JSON ----------
    elif file_type == "json":
        records = json.load(file)
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
    report_key = request.GET.get("report", "invoice")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

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
            batch_sequence = None
            batch_order_number = None
            base_twine = None
            now = datetime.now()
            saved_count = 0

            # Determine batch order_number and collect existing order_keys
            submitted_keys = set()
            for entry in entries:
                twine = (entry.get("twine") or "").strip()
                if not twine:
                    continue
                order_key = entry.get("order_key")
                if order_key is not None:
                    order_key = str(order_key).strip()
                    if order_key:
                        submitted_keys.add(order_key)
                        if batch_order_number is None:
                            try:
                                batch_order_number = Order.objects.values_list('order_number', flat=True).get(order_key=order_key)
                            except Order.DoesNotExist:
                                pass
                if batch_order_number is None:
                    on = (entry.get("order_number") or "").strip()
                    if on:
                        batch_order_number = on

            # Remove old orders with same order_number that are not in the submitted set
            if batch_order_number:
                Order.objects.filter(order_number=batch_order_number).exclude(order_key__in=submitted_keys).delete()

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
    sales_list = Sales.objects.all()
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
                twine = (entry.get("twine") or "").strip()
                if not twine:
                    continue

                sales_key = entry.get("sales_key")
                if sales_key is not None:
                    sales_key = str(sales_key).strip()
                else:
                    sales_key = ""
                is_update = bool(sales_key)

                if is_update:
                    try:
                        obj = Sales.objects.get(sales_key=sales_key)
                    except Sales.DoesNotExist:
                        obj = Sales()
                else:
                    obj = Sales()

                obj.order_no = entry.get("order_no") or ""
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
                obj.updated_at = now
                if not is_update:
                    obj.created_at = now
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
        sales_json.append({
            'sales_key': s.sales_key,
            'order_no': s.order_no,
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


def copy_order_to_sales(request, order_key):
    try:
        order = Order.objects.prefetch_related('specifications').get(order_key=order_key)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('order_entry')

    spec = order.specifications.first()
    mesh_size = spec.mesh_size if spec else ''
    mesh_depth = spec.mesh_depth if spec else ''
    salvage = spec.salvage if spec else ''
    md_disp = mesh_depth if mesh_depth and 'MD' in mesh_depth.upper() else (mesh_depth + 'MD' if mesh_depth else '')
    sal_disp = salvage if salvage and 'SEL' in salvage.upper() else (salvage + 'Sel' if salvage else '')
    spec_text = f"{mesh_size}MM-{md_disp}-{sal_disp}" if mesh_size or md_disp or sal_disp else ""

    now = datetime.now()
    seq = (Sales.objects.aggregate(max_seq=Max('sales_sequence'))['max_seq'] or 0) + 1

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

    messages.success(request, f"Order {order.order_number} copied to Sales as {sales.order_no}.")
    return redirect('order_entry')


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

            spec = order.specifications.first()
            mesh_size = spec.mesh_size if spec else ''
            mesh_depth = spec.mesh_depth if spec else ''
            salvage = spec.salvage if spec else ''
            md_disp = mesh_depth if mesh_depth and 'MD' in mesh_depth.upper() else (mesh_depth + 'MD' if mesh_depth else '')
            sal_disp = salvage if salvage and 'SEL' in salvage.upper() else (salvage + 'Sel' if salvage else '')
            spec_text = f"{mesh_size}MM-{md_disp}-{sal_disp}" if mesh_size or md_disp or sal_disp else ""

            now = datetime.now()
            seq = (Sales.objects.aggregate(max_seq=Max('sales_sequence'))['max_seq'] or 0) + 1

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

                Purchase.objects.create(
                    invoice_no=entry.get("invoice_no") or "",
                    delivery_date=entry.get("delivery_date") or None,
                    payment_date=entry.get("payment_date") or None,
                    vendor=vendor,
                    is_twine=entry.get("is_twine") in (True, "True", "true", "on"),
                    material=entry.get("material") or "",
                    order_description=entry.get("order_description") or "",
                    quantity_weight=entry.get("quantity_weight") or None,
                    unit=entry.get("unit") or "weight",
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
    materials = list(Purchase.objects.exclude(material__isnull=True).exclude(material='').values_list('material', flat=True).distinct().order_by('material'))
    purchases_json = json.dumps(list(purchases.values(
        'purchase_key', 'invoice_no', 'delivery_date', 'payment_date', 'vendor',
        'is_twine', 'material', 'order_description', 'quantity_weight', 'unit',
        'unit_price', 'subtotal', 'gst_percent', 'gst_amount', 'total_amount',
        'amount_paid', 'payment_status', 'balance', 'comments',
    )), default=str)

    context = {
        "purchases": purchases,
        "purchases_json": purchases_json,
        "parties": parties,
        "materials_list": materials,
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
        })

    # Compute outstanding balance per customer
    from django.db.models import Sum, Q
    customer_balance = {}
    for p in parties:
        code = p.code
        # Total invoiced
        inv_total = Invoice.objects.filter(customer_code=code).aggregate(
            total=Sum('gross_total'))['total'] or 0
        # Total allocated to invoices of this customer
        alloc_total = PaymentAllocation.objects.filter(
            invoice__customer_code=code
        ).aggregate(total=Sum('allocated_amount'))['total'] or 0
        # Opening balance (debit amounts - credit amounts)
        ob_debit = OpeningBalance.objects.filter(
            customer__code=code, balance_type='Debit'
        ).aggregate(total=Sum('amount'))['total'] or 0
        ob_credit = OpeningBalance.objects.filter(
            customer__code=code, balance_type='Credit'
        ).aggregate(total=Sum('amount'))['total'] or 0
        ob_net = ob_debit - ob_credit
        balance = ob_net + inv_total - alloc_total
        customer_balance[code] = float(balance)

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
                    alloc.delete()
                    if invoice:
                        update_invoice_payment_status(invoice)
                    if expense_obj:
                        update_expense_payment_status(expense_obj)
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
                elif inv_no.startswith('EXP-'):
                    exp_id = inv_no.replace('EXP-', '')
                    expense_obj = Expense.objects.filter(expense_id=exp_id).first()
                    if not expense_obj:
                        continue
                    affected_expenses.add(expense_obj)
                    target_invoice = None
                    target_expense = expense_obj
                    target_ob = None
                else:
                    invoice_obj = Invoice.objects.filter(invoice_number=inv_no).first()
                    if not invoice_obj:
                        continue
                    affected_invoices.add(invoice_obj)
                    target_invoice = invoice_obj
                    target_expense = None
                    target_ob = None

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
                    elif target_expense:
                        filter_kwargs['expense'] = target_expense
                        filter_kwargs['invoice__isnull'] = True
                        filter_kwargs['opening_balance__isnull'] = True
                    else:
                        filter_kwargs['invoice'] = target_invoice
                        filter_kwargs['expense__isnull'] = True
                        filter_kwargs['opening_balance__isnull'] = True

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
            # Opening balances don't have a status field to update

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
            })

    # Existing allocations for reference
    existing_allocations = PaymentAllocation.objects.select_related('payment', 'invoice', 'expense', 'opening_balance').all()

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
                entries.append({
                    'entry_date': str(ob.opening_date),
                    'description': f"Opening Balance ({ob.ob_number or f'OBAL-{ob.opening_balance_id}'})",
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
                    'description': f"Invoice ({inv.invoice_number})",
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
                        entries.append({
                            'entry_date': str(exp.expense_date) if exp.expense_date else '',
                            'description': f"Expense ({exp.expense_category} EXP-{exp.expense_id})",
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
                if ttype == 'Payment':
                    desc = f"Payment Received ({receipt.receipt_no})"
                elif ttype == 'Adjustment(Cr)':
                    desc = f"Payment Adjustment(Cr) ({receipt.receipt_no})"
                elif ttype == 'Adjustment(Dr)':
                    desc = f"Payment Adjustment(Dr) ({receipt.receipt_no})"
                else:
                    desc = f"Received Payment ({receipt.receipt_no})"
                entries.append({
                    'entry_date': str(receipt.payment_date) if receipt.payment_date else '',
                    'description': desc,
                    'type': 'Cr',
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