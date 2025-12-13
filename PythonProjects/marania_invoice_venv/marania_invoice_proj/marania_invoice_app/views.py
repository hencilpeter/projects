from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from . import forms
from .forms import CustomerForm, InvoiceForm, CompanySettingsForm, CustomerPriceCatalogForm
from .models import Parties, Configuration, Invoice,InvoiceItem, Transportation, PriceCatalog, CompanySettings,Product, CustomerPriceCatalog
from collections import defaultdict,OrderedDict
#from singleton import singleton
import pdb
import json
from django.utils.html import escapejs
#from num2words import num2words
from django.http import HttpResponse
from django.template import TemplateDoesNotExist

from decimal import Decimal, ROUND_DOWN
import pdfkit
#from weasyprint import HTML
from django.template.loader import render_to_string

from django.http import HttpResponse
from django.template.loader import render_to_string
#from xhtml2pdf import pisa
import io


from django.http import HttpResponse
from django.template.loader import render_to_string
#from weasyprint import HTML, CSS

from django.http import HttpResponse
from django.template.loader import render_to_string
#from xhtml2pdf import pisa
import io


import imgkit
from PIL import Image
from django.http import HttpResponse
from django.template.loader import render_to_string
import io

import pdfkit
from django.http import HttpResponse
from django.template.loader import render_to_string


from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO

from django.db import transaction


from django.http import JsonResponse
#from .models import Invoice, InvoiceItem
from .forms import PriceListFormSet

from django.db.models import Count
from django.db.models.functions import TruncMonth

# @singleton
class Configurations:
    
    def __init__(self):
        configurations = Configuration.objects.all() 
        self.config = defaultdict()
        self.config['CompanyName'] = 'Marania Filaments'#configurations['CompanyName']
        #self.config['CGST'] = configurations['CGST']
        #self.config['SGST'] = configurations['SGST']
        #self.config['IGST'] = configurations['IGST']

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
       
        # for field in invoice._meta.fields:
        #     print(field.name, getattr(invoice, field.name))
#"ship_to_customer_address":invoice.ship_to_customer_address,

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

    return render(request, "marania_invoice_app/dashboard.html", context)

# def customer(request):
#     Customers = Parties.objects.all()
#     context = {'form': forms.CustomerForm() ,'customers':Customers}
#     return render(request, 'marania_invoice_app/customer.html', context)

def customer(request):
    customers = Parties.objects.prefetch_related("roles").all()

    if request.method == "POST":
        form = forms.CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.save()
            form.save_m2m()  # IMPORTANT for ManyToMany
            return redirect("customer")
    else:
        form = forms.CustomerForm()

    context = {
        "form": form,
        "customers": customers,
    }
    return render(request, "marania_invoice_app/customer.html", context)


def show_gst_calculator(request):
     return render(request, "marania_invoice_app/gst_calculator.html") 

def invoice_entry(request):
    Invoices = Invoice.objects.all().order_by('-invoice_number')
    Customers = Parties.objects.all()
    customer_dict = defaultdict(lambda:-1)
    transporter_dict = defaultdict(lambda:-1)
    price_dict = defaultdict(lambda:-1)
    
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
    
    # price list details  
    for price_item in PriceCatalog.objects.all():
        size_range = price_item.mesh_size_start+"-"+price_item.mesh_size_end
        price_item_dict = {size_range:str(price_item.price)}
        
        if price_item.twine_code not in price_dict:
            price_dict[price_item.twine_code]={price_item.code:[price_item_dict]}
        elif price_item.code not in price_dict[price_item.twine_code]:
            price_dict[price_item.twine_code][price_item.code] = [price_item_dict]
        else:
            price_dict[price_item.twine_code][price_item.code].append(price_item_dict)

        #if price_item.twine_code not in price_dict:
        #    price_dict[price_item.twine_code]={price_item.customer_group:[price_item_dict]}
        #elif price_item.customer_group not in price_dict[price_item.twine_code]:
        #    price_dict[price_item.twine_code][price_item.customer_group] = [price_item_dict]
        #else:
        #    price_dict[price_item.twine_code][price_item.customer_group].append(price_item_dict)

    #print(price_dict)

    summary_data = invoice_summary()
    context = {'invoice_form': forms.InvoiceForm(initial={'invoice_number':get_next_invoice_number}) , 
               'invoices':Invoices, 'invoiceitems':summary_data,
               'customers':Customers, 'customer_dict': json.dumps(customer_dict),
               'transporter_dict':json.dumps(transporter_dict), 'price_dict':json.dumps(price_dict)
               }
    
    return render(request, 'marania_invoice_app/invoice_entry.html', context)

      
############################-Functions-###################################
from django.contrib import messages

def create_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)  # Bind POST data to the form
        if form.is_valid():                # Validate the data
            customer_instance = form.save()                    # Save the form to the database
            # save transportation details 
            delivery_place_list = request.POST.getlist('delivery_place[]')
            transporter_name_list = request.POST.getlist('transporter_name[]')
            transporter_gst_list = request.POST.getlist('transporter_gst[]')
            vehicle_name_number_list = request.POST.getlist('vehicle_name_number[]')
            default_transport_index = request.POST.get('default_transport')
            transporter_list = []

            for index in range(len(delivery_place_list)):
                if delivery_place_list[index].strip():
                    # Only mark as True if checkbox was checked
                    is_default = (str(index) == default_transport_index)

                    transporter_list.append(Transportation(customer=customer_instance,               
                            delivery_place=delivery_place_list[index],
                            transporter_name=transporter_name_list[index],
                            transporter_gst=transporter_gst_list[index],
                            vehicle_name_number=vehicle_name_number_list[index],
                            is_default_transport=is_default,
                            ))
                    
            if (len(transporter_list) > 0):
                Transportation.objects.bulk_create(transporter_list)    # save the transporter items     

            return redirect('customer')  # Redirect after save
    else:
        form = CustomerForm()  # Empty form for GET request

    context = {'form': CustomerForm}
    return render(request, 'marania_invoice_app/customer.html', context)

def invoice_save(request):

    if request.method == 'POST':
        try:
            # Check if invoice_id exists → UPDATE MODE
            invoice_number = request.POST.get('invoice_number')
            invoice_instance = Invoice.objects.filter(invoice_number=invoice_number).first()

            if invoice_instance:
                print("^^^UPDATE MODE^^^^")
                #invoice_instance = Invoice.objects.get(id=invoice_id)
                form = InvoiceForm(request.POST, instance=invoice_instance)
            else:
                print("^^^INSERT MODE^^^^")
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
                item_gst_amount_list       = request.POST.getlist('item_gst_amount[]')
                item_total_with_gst_list   = request.POST.getlist('item_total_with_gst[]')
                item_hsn_code_list         = request.POST.getlist('item_hsn_code[]')

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
                                item_gst_amount       = item_gst_amount_list[index],
                                item_total_with_gst   = item_total_with_gst_list[index],
                                item_hsn_code         = item_hsn_code_list[index],
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


def get_invoice_dictonaries(invoice_number):

    invoice_dict = get_invoices_dict()
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
    for invoice_item in invoice_items:
        amount = invoice_item.item_quantity * invoice_item.item_price 
        amount = Decimal(amount).quantize(Decimal("0.00"), rounding=ROUND_DOWN)
        sub_total += amount
        total_quantity += invoice_item.item_quantity
        description =  f"{invoice_item.item_description}" 
        items.append({"packages": "1", "description": description,"hsn": "5608", "gst_rate": 5, "quantity": str(invoice_item.item_quantity) + " KGS", 
                      "rate": invoice_item.item_price, "unit": "KGS", "amount": amount})
        

    # taxes= [
    #         {"hsn": "5608", "taxable_value": "47,667.19", "cgst_rate": 2.5, "cgst_amount": "1,191.68", "sgst_rate": 2.5, "sgst_amount": "1,191.68", "total_tax": "2,383.36"}
    #     ]

    cgst = Decimal(Decimal(sub_total) * Decimal(.025)).quantize(Decimal("0.00"), rounding=ROUND_DOWN)
    sgst = Decimal(Decimal(sub_total) * Decimal(.025)).quantize(Decimal("0.00"), rounding=ROUND_DOWN)
    total = sub_total + cgst + sgst
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
            "igst_rate":"5",
            "sgst_rate":"2.5",
            "cgst_rate":"2.5",
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

    invoice_data_dict = defaultdict(lambda:-1)
    # print("Invoice Date ########################"+str(invoice_dict[invoice_number]["invoice_date"]))
    #print(invoice_dict[invoice_number])

    company_dict, invoice, consignee_dict, buyer_dict, items = get_invoice_dictonaries(invoice_number)
    context = {"company":company_dict, "invoice":invoice, "consignee":consignee_dict, "buyer":buyer_dict, "items":items}

    return render(request, 'marania_invoice_app/invoice_view.html', context) 


from weasyprint import HTML,CSS
def invoice_pdf(request, invoice_number):
    company_dict, invoice, consignee_dict, buyer_dict, items = get_invoice_dictonaries(invoice_number)
    context = {"company": company_dict, "invoice": invoice, "consignee": consignee_dict, "buyer": buyer_dict, "items": items}
    
    template = get_template('marania_invoice_app/invoice_view.html')
    html_string = template.render(context)
    
    # CSS to remove margins
    css_string = """
        @page {
            size: A4;
            margin: 0;
        }
        body {
            margin: 0;
            padding: 0;
        }
    """
    
    # Generate PDF with custom CSS
    html = HTML(string=html_string)
    css = CSS(string=css_string)
    pdf_file = html.write_pdf(stylesheets=[css])
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice_number}.pdf"'
    
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
        'item_quantity', 'item_price' , 'item_gst_amount', 'item_total_with_gst', 'item_hsn_code'
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
    unique_twine_codes = {f"{p.code}" for p in products}
    unique_customer_group = {f"{p.customer_group}" for p in saved_prices}
    filter_header = {'product_names':unique_product_names,
                     'customer_groups':unique_customer_group,
                     'twine_codes':unique_twine_codes}
    
    unique_customer_group = PriceCatalog

   
    return render(request, "marania_invoice_app/price_catalog.html", {"formset": formset, 
                                                                        'saved_prices': saved_prices,
                                                                        'filter_header':filter_header,})


def load_price_list(request, price_code):
    items = PriceCatalog.objects.filter(code=price_code).order_by("sequence_id")
    print(items);
    data = {
        "items": [
            {
                "product":  f"{p.twine_code}-{p.product.name}",  # adjust if FK
                "sequence_id": p.sequence_id,
                "code": p.code,
                "customer_group": p.customer_group,
                "twine_code": p.twine_code,
                "mesh_size_start": p.mesh_size_start,
                "mesh_size_end": p.mesh_size_end,
                "price": str(p.price)
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

        # 1️⃣ Get the price code from first item
        price_code = items[0].get("code")
        if not price_code:
            return JsonResponse({"error": "Price code missing"}, status=400)
       
        # Convert to JSON string (optional)
        action = data.get("action")

        # 2️⃣ DELETE ALL rows belonging to this price code
        PriceCatalog.objects.filter(code=price_code).delete()
        # print(f"5.save price list called....{action}")
        if action == "delete":
            return JsonResponse({"status": "deleted"})

    
        # 3️⃣ INSERT NEW ROWS
        new_objs = []
        for item in items:
            twine_code = item.get("twine_code")
            product_name = item.get("product")
            product_code = product_name.split("-")[0]
                        
            try:
                product_obj = Product.objects.get(code=product_code)
            except Product.DoesNotExist:
                raise ValueError(f"Invalid product: {product_code}")

            new_objs.append(PriceCatalog(
                product=product_obj,
                sequence_id=item.get("sequence_id"),
                code=item.get("code"),
                customer_group=item.get("customer_group"),
                twine_code=item.get("twine_code"),
                mesh_size_start=item.get("mesh_size_start"),
                mesh_size_end=item.get("mesh_size_end"),
                price=item.get("price"),
            ))

        PriceCatalog.objects.bulk_create(new_objs)
        return JsonResponse({"status": "saved", "deleted_old": True, "count": len(new_objs)})       

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

   
def customer_price_catalog(request):
    customers = Parties.objects.all()
    price_catalogs = PriceCatalog.objects.all()
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
            cust = customer_vals[idx]
            cat = catalog_vals[idx]

            # Skip blank rows
            if not cust or not cat:
                continue

            if action == "delete":
                CustomerPriceCatalog.objects.filter(customer_id=cust,price_catalog_id = cat).delete()
                continue

            # SAVE ACTION
            try:
                # update logic - get the existing object 
                obj = CustomerPriceCatalog.objects.get(customer_id=cust, price_catalog_id=cat)
            except CustomerPriceCatalog.DoesNotExist:
                # new entry - create new object
                obj = CustomerPriceCatalog()
            
            print(gst_vals)
            obj.customer_id = cust
            obj.price_catalog_id = cat
            obj.gst_included = True if (  idx < len(gst_vals)  and gst_vals[idx] == "on" ) else False
            obj.colour_extra_price = float(colour_vals[idx] or 0)
            obj.small_mesh_size_extra_price = float(mesh_vals[idx] or 0)
            obj.remark = remark_vals[idx]
            obj.save()

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
    data = {
        "customer": catalog.customer.id,
        "price_catalog": catalog.price_catalog.id,
        "gst_included": catalog.gst_included,
        "colour_extra_price": catalog.colour_extra_price,
        "small_mesh_size_extra_price": catalog.small_mesh_size_extra_price,
        "remark": catalog.remark
    }
    return JsonResponse(data)



def product_master(request):
    products = Product.objects.all()

    if request.method == "POST":
        action = request.POST.get("action")

        codes = request.POST.getlist("code")
        names = request.POST.getlist("name")
        display_names = request.POST.getlist("display_name")
        hsn_codes = request.POST.getlist("hsn")
        cgsts = request.POST.getlist("cgst")
        sgsts = request.POST.getlist("sgst")
        igsts = request.POST.getlist("igst")
        descriptions = request.POST.getlist("description")

        for idx in range(len(codes)):
            code = codes[idx].strip()
            name = names[idx].strip()

            if not code or not name:
                continue

            # DELETE
            if action == "delete":
                Product.objects.filter(code=code).delete()
                continue

            # SAVE logic
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

            obj.save()

        return redirect("product_master")

    # Unique filter lists
    unique_codes = sorted(list({p.code for p in products}))
    unique_names = sorted(list({p.name for p in products}))
    unique_hsn = sorted(list({p.hsn or "-" for p in products}))

    return render(request, "marania_invoice_app/product_master.html", {
        "products": products,
        "unique_codes": unique_codes,
        "unique_names": unique_names,
        "unique_hsn": unique_hsn,
    })


def load_product(request, id):
    p = Product.objects.get(id=id)
    return JsonResponse({
        "code": p.code,
        "name": p.name,
        "display_name": p.display_name,
        "hsn": p.hsn,
        "cgst": str(p.cgst),
        "sgst": str(p.sgst),
        "igst": str(p.igst),
        "description": p.description,
    })
