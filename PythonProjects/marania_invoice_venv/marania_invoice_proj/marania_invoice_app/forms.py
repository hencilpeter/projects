from django import forms
from .models import Customer
from .models import Invoice

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        # Include all editable fields
        fields = [
            'code', 'name', 'gst', 'phone', 'email',
            'address_bill_to', 'address_ship_to', 'is_within_state',
            'price_list_tag', 'default_delivery_transport', 'default_delivery_location'
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Code'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'gst': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'GST'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'address_bill_to': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Billing address'}),
            'address_ship_to': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Shipping address'}),
            'is_within_state': forms.Select(attrs={'class': 'form-select'}, choices=[(True, 'Yes'), (False, 'No')]),
            'price_list_tag': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Price List Tag'}),
            'default_delivery_transport': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Delivery Transport'}),
            'default_delivery_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Delivery Location'}),
        }

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'invoice_date',
            'invoice_number',
            'customer_code',
            'customer_name',
            'gst',
            'customer_address_bill_to',
            'customer_address_ship_to',
            'contact',
            'email',
            'dispatched_through'
        ]
        
        widgets = {
            'invoice_date': forms.DateInput(attrs={
                'type': 'date', 'class': 'form-control form-control-sm'
            }),
            'invoice_number': forms.TextInput(attrs={
                'class': 'form-control form-control-sm', 'placeholder': 'Invoice Number'
            }),
            'customer_code': forms.TextInput(attrs={
                'class': 'form-control form-control-sm', 'placeholder': 'Customer Code'
            }),
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control form-control-sm', 'placeholder': 'Customer Name'
            }),
            'gst': forms.TextInput(attrs={
                'class': 'form-control form-control-sm', 'placeholder': 'GST'
            }),
            'customer_address_bill_to': forms.Textarea(attrs={
                'class': 'form-control form-control-sm', 'rows': 2, 'placeholder': 'Address (Bill To)'
            }),
            'customer_address_ship_to': forms.Textarea(attrs={
                'class': 'form-control form-control-sm', 'rows': 2, 'placeholder': 'Address (Ship To)'
            }),
            'contact': forms.TextInput(attrs={
                'class': 'form-control form-control-sm', 'placeholder': 'Contact'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-sm', 'placeholder': 'Email'
            }),
            'dispatched_through': forms.TextInput(attrs={
                'class': 'form-control form-control-sm', 'placeholder': 'Dispatched Through'
            }),
        }