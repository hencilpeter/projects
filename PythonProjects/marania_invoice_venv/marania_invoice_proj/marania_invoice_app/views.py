from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from . import forms
from .forms import CustomerForm, InvoiceForm
from .models import Customer, Configuration, Invoice,InvoiceItem
from collections import defaultdict,OrderedDict
#from singleton import singleton
import pdb


# @singleton
class Configurations:
    
    def __init__(self):
        configurations = Configuration.objects.all() 
        self.config = defaultdict()
        self.config['CompanyName'] = 'Marania Filaments'#configurations['CompanyName']
        #self.config['CGST'] = configurations['CGST']
        #self.config['SGST'] = configurations['SGST']
        #self.config['IGST'] = configurations['IGST']




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
    InvoiceItems = InvoiceItem.objects.all()
    invoice_dict = defaultdict()
    for invoiceitem in InvoiceItems:
        invoice_dict[invoiceitem.invoice.invoice_number] = invoiceitem
    
    #ordered_dict = OrderedDict(sorted(invoice_dict.items(), key=lambda x: x[0], reverse=False))

    context = {'invoice_form': forms.InvoiceForm() ,'invoice_item_form':forms.InvoiceItem(),
               'invoices':Invoices, 'invoiceitems':invoice_dict}
    return render(request, 'marania_invoice_app/invoice_entry.html', context)

########################################################




############################-Functions-###################################

def create_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)  # Bind POST data to the form
        if form.is_valid():                # Validate the data
            form.save()                    # Save the form to the database
            return redirect('customer')  # Redirect after save
    else:
        form = CustomerForm()  # Empty form for GET request

    context = {'form': CustomerForm}
    return render(request, 'marania_invoice_app/customer.html', context)

def save_invoice(request):
    
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


