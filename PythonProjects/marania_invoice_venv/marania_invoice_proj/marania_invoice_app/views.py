from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from . import forms
from .forms import CustomerForm
from .models import Customer, Configuration
from collections import defaultdict
#from singleton import singleton



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
    Customers = Customer.objects.all()
    context = {} #{'form': forms.CustomerForm() ,'customers':Customers}
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


# def create_invoice(request):
#     if request.method == 'POST':
#         form = CustomerForm(request.POST)  # Bind POST data to the form
#         if form.is_valid():                # Validate the data
#             form.save()                    # Save the form to the database
#             return redirect('customer')  # Redirect after save
#     else:
#         form = CustomerForm()  # Empty form for GET request

#     context = {'form': CustomerForm}
#     return render(request, 'marania_invoice_app/customer.html', context)


