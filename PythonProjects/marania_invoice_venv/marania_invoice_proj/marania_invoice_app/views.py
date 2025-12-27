# Django core
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import render_to_string, get_template
from django.template import TemplateDoesNotExist
from django.db import transaction
from django.conf import settings
from django.apps import apps

# Django ORM utilities
from django.db.models import Count
from django.db.models.functions import TruncMonth, Lower, Trim

# Forms
from . import forms
from .forms import (
    CustomerForm,
    InvoiceForm,
    CompanySettingsForm,
    CustomerPriceCatalogForm,
    PriceListFormSet,
)

# Models
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
)

# Services & serializers
from .services import export_data
from .serializers import MODEL_REGISTRY, UNIQUE_KEY_MODEL

# Utilities
from collections import defaultdict, OrderedDict
from decimal import Decimal, ROUND_DOWN
import json
import csv
import io
import os
from datetime import datetime
from zipfile import ZipFile

# PDF generation
# from weasyprint import HTML, CSS
# from xhtml2pdf import pisa

# Image / PDF helpers (used)
import pdfkit
import imgkit
# from PIL import Image

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
                    "invoice_items":invice_item_dict[invoice.invoice_number]}
    
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

# def get_product_dict():
    
#     products_dict = defaultdict(dict)

#     products = Product.objects.select_related('material').all()

#     for product in products:
#         products_dict[product.code] = {
#             "name": product.name,
#             "display_name": product.display_name,
#             "hsn": product.hsn,

#             # Material reference
#             "material_code": product.material.code if product.material else None,
#             "material_name": product.material.name if product.material else None,

#             # Tax rates
#             "cgst": product.cgst,
#             "sgst": product.sgst,
#             "igst": product.igst,

#             "description": product.description,
#         }

#     return products_dict

def print_dict(d, indent=0):
    for key, value in d.items():
        print(" " * indent + str(key) + ":")
        if isinstance(value, dict):
            print_dict(value, indent + 4)
        else:
            print(" " * (indent + 4) + str(value))


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

        product_code = customer_price_catalog.price_catalog.product.code

        if customer_price_dict[customer_code][product_code] == -1:
            customer_price_dict[customer_code][product_code] = {}

        price_code = customer_price_catalog.price_catalog.code

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
    invoice_summary = {}

    for invoice_item in invoice_items:
        invoice_number = invoice_item.invoice.invoice_number
        item_subtotal = invoice_item.item_quantity * invoice_item.item_price
        item_amount = item_subtotal * (Decimal(1.05))
        #invoice_amount = invoice_item.item_price * (Decimal(1.05))  # item price + 5%

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
    invoice_data = (
        Invoice.objects
        .annotate(month=TruncMonth("invoice_date"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    invoice_months = [d["month"].strftime("%b %Y") for d in invoice_data]
    invoice_counts = [d["count"] for d in invoice_data]

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
    print(data)
    return JsonResponse(data)

def show_gst_calculator(request):
     return render(request, "marania_invoice_app/gst_calculator.html") 

def show_gst_calculator_from_main_UI(request):
     return render(request, "marania_invoice_app/view_gst_calculator.html") 

def invoice_entry(request):
    Invoices = Invoice.objects.all().order_by('-invoice_number')
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
    context = {'invoice_form': forms.InvoiceForm(initial={'invoice_number':get_next_invoice_number}) , 
               'invoices':Invoices, 'invoiceitems':summary_data,
               'customers':Customers, 'customer_dict': json.dumps(customer_dict),
               'transporter_dict':json.dumps(transporter_dict), 
               #'price_dict':json.dumps(price_dict),
               'customer_price_dict':json.dumps(customer_price_dict),
               'product_dict':json.dumps(product_dict),
               }

    return render(request, 'marania_invoice_app/invoice_entry.html', context)

      
############################-Functions-###################################
from django.contrib import messages
from django.db import IntegrityError


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

            if invoice_instance:
                form = InvoiceForm(request.POST, instance=invoice_instance)
            else:
                form = InvoiceForm(request.POST)

            # Validate form
            if form.is_valid():

                invoice_instance = form.save()   # Creates or updates

                # --- SAVE CURRENT INVOICE NUMBER ---
                invoice_number_int = int(form.cleaned_data['invoice_number'])

                try:
                    with transaction.atomic():
                        settings = CompanySettings.objects.select_for_update().get(id=1)
                        settings.current_invoice_number = invoice_number_int
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

def decimal_to_str(value):
    return format(Decimal(str(value)).normalize(), 'f')

def get_invoice_dictonaries(invoice_number):
    # TODO - hencil current change 
    invoice_dict = get_invoices_dict()
    partices_dict = get_parties_dict()
    product_dict = get_product_dict()
    # Hencil - current 
    #company details 
    company_dict = {"logo_url": "/static/images/marania_eagle_logo.png",
                    "name": "MARANIA FILAMENTS", # TODO
                    "address": "5/118a, Elavuvillai, Kilaattu Villai, Kallu Kuttom, Killiyoor, Kanniyakumari", # TODO
                    "gstin": "33AGAPJ9143P1Z4",
                    "state_name": "Tamil Nadu",
                    "state_code": "33",
                    "contact": "94898 58997,94877 86997",
                    "bank_account_name": "MARANIA FILAMENTS",
                    "bank_name": "ICICI ",
                    "bank_account_no": "250105500252",
                    "bank_branch": "VETTURNIMADAM,NAGERCOIL",
                    "bank_ifsc": "ICIC0002501",
                    }
    consignee_dict= {
            "name": invoice_dict[invoice_number]["ship_to_customer_name"],
            "address": invoice_dict[invoice_number]["ship_to_customer_address"],
            "gstin": invoice_dict[invoice_number]["ship_to_customer_gst"],
            "contact":invoice_dict[invoice_number]["ship_to_customer_contact"],
            "state_name": "Tamil Nadu",
            "state_code": "33"
        }
    
    buyer_dict= {
            "name": invoice_dict[invoice_number]["customer_name"],
            "address": invoice_dict[invoice_number]["customer_address"],
            "gstin": invoice_dict[invoice_number]["customer_gst"],
            "contact":invoice_dict[invoice_number]["customer_contact"],
            "state_name": "Tamil Nadu",
            "state_code": "33"
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
        items.append({"packages": "1", "description": description,"hsn": hsn, "gst_rate": gst_rate, "quantity": str(invoice_item.item_quantity) + " KGS", 
                      "rate": invoice_item.item_price, "unit": "KGS", "amount": amount})
        
       
    if is_within_state :
        cgst = Decimal(Decimal(sub_total) * Decimal(company_settings.cgst/100)).quantize(Decimal("0.00"), rounding=ROUND_DOWN)
        sgst = Decimal(Decimal(sub_total) * Decimal(company_settings.sgst/100)).quantize(Decimal("0.00"), rounding=ROUND_DOWN)
    else:
        igst = Decimal(Decimal(sub_total) * Decimal(company_settings.igst/100)).quantize(Decimal("0.00"), rounding=ROUND_DOWN)

    total = sub_total + cgst + sgst + igst
    rounded_total = round(total,2)
    round_off_amount = rounded_total - total
    tax_words =""
    amount_words = number_to_words(Decimal(rounded_total))
    invoice_date = invoice_dict[invoice_number]["invoice_date"]
    invoice= {
            "invoice_no": invoice_number,
            "date": invoice_date.strftime("%d-%m-%Y"),
            "delivery_note": "",
            "payment_terms": "",
            "reference_no": "",
            "other_ref": "",
            "order_no": "",
            "order_date": "",
            "dispatch_doc": "",
            "delivery_date": "",
            "dispatch_mode": "",
            "destination": "",
            "lr_no": "",
            "vehicle_no": "",
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

from weasyprint import HTML,CSS

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
    response['Content-Disposition'] = f'attachment; filename="Marania_Invoice_{invoice_number}.pdf"'

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
            "vehicle_name_number":invoice.vehicle_name_number,
            "transporter_gst": invoice.transporter_gst,
        },
        "items": list(items)
    })

from django.db.models.functions import Lower, Trim

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

    filter_header = {
        'product_names': unique_product_names,
        'customer_groups': unique_customer_group,
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

    # UNIQUE FILTER LISTS
    unique_customers = list({str(c.customer) for c in catalogs})
    unique_item_code_customer = list({str(c.price_catalog) for c in catalogs})
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
    price_code = get_first_part(str(catalog.price_catalog))
    price_catalog_object = PriceCatalog.objects.filter(code=price_code).first()

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


import csv
import io
import json
from django.db import transaction
from django.db.models import BooleanField, ForeignKey

AUTO_FIELDS = {"id", "created_at", "updated_at"}

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
    
from django.db import models

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

import csv, json, io,os
from django.db import transaction
from django.apps import apps
from zipfile import ZipFile
from datetime import datetime
from django.conf import settings

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