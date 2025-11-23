from django import forms
from .models import Customer
from .models import Invoice, InvoiceItem
from .models import Transportation
from django.forms import inlineformset_factory

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        # Include all editable fields
        fields = [
            'code', 'name', 'gst', 'phone', 'email',
            'address_bill_to', 'address_ship_to', 'is_within_state',
            'price_list_tag'
            #, 'default_delivery_transport', 'default_delivery_location'
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
            # 'default_delivery_transport': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Delivery Transport'}),
            # 'default_delivery_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Delivery Location'}),
        }

class InvoiceForm(forms.ModelForm):
    # Manually declare only fields that need datalist / custom placeholder
    print("Form1")
    customer_code = forms.CharField(
        label='Customer Code',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Customer Code (Bill to)',
            'list': 'customer_code_list',  # links to datalist id in HTML
        })
    )
    print("Form2")
    customer_name = forms.CharField(
        label='Customer Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Customer Name (Bill to)',
            'list': 'customer_name_list',  # links to datalist id in HTML
        })
    )
    print("Form3")
    ship_to_customer_code = forms.CharField(
        label='Customer Code',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Customer Code (Ship to)',
            'list': 'ship_to_customer_code_list',  # links to datalist id in HTML
        })
    )
    print("Form4")
    ship_to_customer_name = forms.CharField(
        label='Customer Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Customer Name (Ship to)',
            'list': 'ship_to_customer_name_list',  # links to datalist id in HTML
        })
    )
    print("Form5")
    dispatched_through = forms.CharField(
        label='Dispatched Through',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Dispatched Through',
            'list': 'dispatched_through_list',  # links to datalist id in HTML
        })
    )
    print("Form6")
    class Meta:
        model = Invoice
        fields = [
            'invoice_date',
            'invoice_number',
            'customer_code',
            'customer_name',
            'customer_gst',
            'customer_address',
            'customer_contact',
            'customer_email',
            'ship_to_customer_code',
            'ship_to_customer_name',
            'ship_to_customer_gst',
            'ship_to_customer_address',
            'ship_to_customer_contact',
            'ship_to_customer_email',
            'dispatched_through'
        ]

        widgets = {
            'invoice_date': forms.DateInput(attrs={
                'class': 'form-control form-control-sm',
                'type': 'date'
            }),
            'invoice_number': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Invoice Number'
            }),
            'customer_gst': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'GST Number (Bill to)'
            }),
            'customer_address': forms.Textarea(attrs={
                'class': 'form-control form-control-sm',
                'rows': 3,
                'placeholder': 'Customer Address (Bill to)'
            }),
            'customer_contact': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Contact Number (Bill to)'
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Email (Bill to)'
            }),
            'ship_to_customer_gst': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'GST Number (Ship to)'
            }),
            'ship_to_customer_address': forms.Textarea(attrs={
                'class': 'form-control form-control-sm',
                'rows': 3,
                'placeholder': 'Address (Ship to)'
            }),
            'ship_to_customer_contact': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Contact Number (Ship to)'
            }),
            'ship_to_customer_email': forms.EmailInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Email (Ship to)'
            }),
        }
            



class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['item_spec','item_code', 'item_description','item_mesh_size','item_mesh_depth', 'item_quantity', 'item_price']

        widgets = {
            'item_spec': forms.TextInput(attrs={
                'class': 'form-control form-control-sm item-spec',
                'placeholder': 'Specification',
                'style': 'flex: 1.6;'
            }),
            'item_code': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Code',
                'style': 'flex: 0.3;'
            }),
            'item_description': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Description',
                'style': 'flex: 1.5;'
            }),
            'item_mesh_size': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'MM',
                'style': 'flex: 0.3;'
            }),
            'item_mesh_depth': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'MD',
                'style': 'flex: 0.3;'
            }),
            'item_quantity': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Qty',
                'style': 'flex: 0.4;'
            }),
            'item_price': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Q.Price',
                'step': '1',
                'style': 'flex: 0.4;'
            }),
        }
        

class TransportationForm(forms.ModelForm):
    class Meta:
        model = Transportation
        fields = ['delivery_place', 'transporter_name', 'transporter_gst',  'vehicle_name_number', 'is_default_transport']
        widgets = {
             'delivery_place': forms.TextInput(attrs={
                'class': 'form-control form-control-sm delivery-place',
                'placeholder': 'Delivery place'
            }),
            'transporter_name': forms.TextInput(attrs={
                'class': 'form-control form-control-sm transporter-name',
                'placeholder': 'Transporter Name'
            }),
            'transporter_gst': forms.TextInput(attrs={
                'class': 'form-control form-control-sm transporter-gst',
                'placeholder': 'Transporter GST'
            }),
            'vehicle_name_number': forms.TextInput(attrs={
                'class': 'form-control form-control-sm vehicle-name-number',
                'placeholder': 'Vehicle Name & Number'
            }),
            'is_default_transport': forms.CheckboxInput(attrs={
                'class': 'form-check-input is-default-transport'
            }),
        }



# 👇 This creates a formset of items linked to an Invoice
InvoiceItemFormSet = inlineformset_factory(
    Invoice, InvoiceItem,
    form=InvoiceItemForm,
    extra=1,  # how many blank forms to show initially
    can_delete=True
)
