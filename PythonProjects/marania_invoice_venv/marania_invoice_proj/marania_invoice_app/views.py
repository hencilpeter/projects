from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from . import forms
from .forms import CustomerForm, InvoiceForm
from .models import Customer, Configuration, Invoice,InvoiceItem, Transportation
from collections import defaultdict,OrderedDict
#from singleton import singleton
import pdb
import json
from django.utils.html import escapejs

from decimal import Decimal

# @singleton
class Configurations:
    
    def __init__(self):
        configurations = Configuration.objects.all() 
        self.config = defaultdict()
        self.config['CompanyName'] = 'Marania Filaments'#configurations['CompanyName']
        #self.config['CGST'] = configurations['CGST']
        #self.config['SGST'] = configurations['SGST']
        #self.config['IGST'] = configurations['IGST']


########################################################-Helper Functions-############
def invoice_summary():
    invoice_items = InvoiceItem.objects.select_related('invoice').all()
    invoice_summary = {}

    for invoice_item in invoice_items:
        invoice_number = invoice_item.invoice.invoice_number
        invoice_amount = invoice_item.item_price * (Decimal(1.05))  # item price + 5%

        if invoice_number not in invoice_summary:
            invoice_summary[invoice_number] = {
                'date': invoice_item.invoice.invoice_date,
                'customer': invoice_item.invoice.customer_name,
                'weight': invoice_item.item_quantity,
                'sub_total': invoice_item.item_price,
                'invoice_amount': invoice_amount
            }
        else:
            summary = invoice_summary[invoice_number]
            summary['weight'] += invoice_item.item_quantity
            summary['sub_total'] += invoice_item.item_price
            summary['invoice_amount'] += invoice_amount

    return invoice_summary

#################################

# Create your views here.
#@login_required
def dashboard(request):
    config = Configurations()
    print(config)
    context = {'config':config.config}
    return render(request, 'marania_invoice_app/dashboard.html', context)
    #return render(request, 'marania_invoice_app/customer.html', context)


def customer(request):
    Customers = Customer.objects.all()
    context = {'form': forms.CustomerForm() ,'customers':Customers}
    return render(request, 'marania_invoice_app/customer.html', context)

def invoice_entry(request):
    Invoices = Invoice.objects.all().order_by('-invoice_number')
    Customers = Customer.objects.all()
    customer_dict = defaultdict(lambda:-1)
    transporter_dict = defaultdict(lambda:-1)
    
    # customer details 
    for customer in Customer.objects.all():
        customer_dict[customer.code] = {'name':customer.name, 'gst':customer.gst, 'phone':customer.phone, 'email':customer.email, 
                                        'address_bill_to':customer.address_bill_to, 'address_ship_to':customer.address_ship_to,
                                        'is_within_state':customer.is_within_state,'price_list_tag':customer.price_list_tag}
    
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

    #InvoiceItems = InvoiceItem.objects.all()
    #invoice_dict = defaultdict()
    # Invoice Summary
    # for invoiceitem in InvoiceItems:
    #     invoice_dict[invoiceitem.invoice.invoice_number] = invoiceitem


    summary_data = invoice_summary()
    context = {'invoice_form': forms.InvoiceForm() , #'invoice_item_form':forms.InvoiceItem(),
               'invoices':Invoices, 'invoiceitems':summary_data,
               'customers':Customers, 'customer_dict': json.dumps(customer_dict),
               'transporter_dict':json.dumps(transporter_dict)}
    
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
    
    #pdb.set_trace()

    if request.method == 'POST':
        form = InvoiceForm(request.POST)  # Bind POST data to the form
        if form.is_valid():                # Validate the data
            invoice_instance  = form.save()                    # Save the form to the database

            #invoice items 
            item_spec_list = request.POST.getlist('item_spec[]')
            item_code_list = request.POST.getlist('item_code[]')
            item_description_list = request.POST.getlist('item_description[]')
            item_mesh_size_list = request.POST.getlist('item_mesh_size[]')
            item_mesh_depth_list = request.POST.getlist('item_mesh_depth[]')
            item_quantity_list = request.POST.getlist('item_quantity[]')
            item_price_list = request.POST.getlist('item_price[]')
            
            invoice_item_list = []
            for index in range(len(item_code_list)):
                if item_code_list[index].strip():
                    invoice_item_list.append(InvoiceItem(invoice=invoice_instance,               # mandatory ForeignKey
                            item_spec=item_spec_list[index],
                            item_code=item_code_list[index],
                            item_description=item_description_list[index],
                            item_mesh_size=item_mesh_size_list[index],
                            item_mesh_depth=item_mesh_depth_list[index],
                            item_quantity=item_quantity_list[index],
                            item_price=item_price_list[index],))
            
            if (len(item_code_list) > 0):
                InvoiceItem.objects.bulk_create(invoice_item_list)    # save the invoice items 
                    
            return redirect('invoice_entry')  # Redirect after save
    else:
        form = InvoiceForm()  # Empty form for GET request

    Invoices = Invoice.objects.all()
    context = {'invoice_form': forms.InvoiceForm() ,'invoices':Invoices}
    return render(request, 'marania_invoice_app/invoice_entry.html', context)


def invoice_view(request, invoice_number):
    context = {
        "company": {
            "logo_url": "/static/images/logo.png",
            "name": "SUN NETS",
            "address": "33/N, HENTRY STREET, NAGERCOIL - 629001, KANNIYAKUMARI DISTRICT",
            "gstin": "33ADJPL6559R1ZP",
            "state_name": "Tamil Nadu",
            "state_code": "33",
            "contact": "9443389998",
            "bank_name": "SUN NETS",
            "bank_bank": "STATE BANK OF INDIA",
            "bank_account": "67122303997",
            "bank_branch": "KANYAKUMARI",
            "ifsc": "SBIN0070013",
        },
        "invoice": {
            "invoice_no": "2025-26/177",
            "date": "3-Oct-25",
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
            "vehicle_no": "TN75R4178",
            "terms_delivery": "",
            "subtotal": "47,667.19",
            "cgst": "1,191.68",
            "sgst": "1,191.68",
            "round_off": "0.45",
            "total": "₹50,051.00",
            "tax_words": "INR Two Thousand Three Hundred Eighty Three and Thirty Six paise Only",
            "amount_words": "INR Fifty Thousand Fifty One Only"
        },
        "consignee": {
            "name": "Marania Filaments",
            "address": "5/118a, Elavuvillai, Kilaattu Villai, Kallu Kuttom, Killiyoor, Kanniyakumari",
            "gstin": "33AGAPJ9143P1Z4",
            "state_name": "Tamil Nadu",
            "state_code": "33"
        },
        "buyer": {
            "name": "Marania Filaments",
            "address": "5/118a, Elavuvillai, Kilaattu Villai, Kallu Kuttom, Killiyoor, Kanniyakumari",
            "gstin": "33AGAPJ9143P1Z4",
            "state_name": "Tamil Nadu",
            "state_code": "33"
        },
        "items": [
            {"packages": "1", "description": ".20DK/34MM/150MD", "hsn": "5608", "gst_rate": 5, "quantity": "50.700 KGS", "rate": "476.19", "unit": "KGS", "amount": "24,142.83"},
            {"packages": "1", "description": ".20DK/36MM/150MD", "hsn": "5608", "gst_rate": 5, "quantity": "49.900 KGS", "rate": "471.43", "unit": "KGS", "amount": "23,524.36"},
        ],
        "taxes": [
            {"hsn": "5608", "taxable_value": "47,667.19", "cgst_rate": 2.5, "cgst_amount": "1,191.68", "sgst_rate": 2.5, "sgst_amount": "1,191.68", "total_tax": "2,383.36"}
        ]
    }
    
    #Invoices = Invoice.objects.all()
    return render(request, 'marania_invoice_app/invoice_view.html', context) 

