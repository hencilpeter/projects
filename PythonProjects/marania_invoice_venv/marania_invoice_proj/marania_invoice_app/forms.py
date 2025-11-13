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
  # CharField allows typing new values
    customer_code = forms.CharField(
        label='Customer Code',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Customer Code',
            'list': 'customer_code_list',  # links to datalist id in HTML
        }) 
    )

    customer_name = forms.CharField(
        label='Customer Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Customer Name',
            'list': 'customer_name_list',  # links to datalist id in HTML
        }) 
    )

    dispatched_through = forms.CharField(
        label='Dispatched Through',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Dispatched Through',
            'list': 'dispatched_through_list',  # links to datalist id in HTML
        }) 
    )

    class Meta:
        model = Invoice
        fields = [
            'invoice_date',
            'invoice_number',
            'customer_code',
            'customer_name',
            'customer_gst',
            'customer_address_bill_to',
            'customer_address_ship_to',
            'customer_contact',
            'customer_email',
            'dispatched_through'
        ]
            
        widgets = {
            'invoice_date': forms.DateInput(attrs={
                'type': 'date', 'class': 'form-control form-control-sm'
            }),
            'invoice_number': forms.TextInput(attrs={
                'class': 'form-control form-control-sm', 'placeholder': 'Invoice Number'
            }),
            # 'customer_code': forms.ComboField(attrs={
            #      'class': 'form-control form-control-sm', 'placeholder': 'Customer Code'
            # }),
            # 'customer_name': forms.TextInput(attrs={
            #     'class': 'form-control form-control-sm', 'placeholder': 'Customer Name'
            # }),
            'customer_gst': forms.TextInput(attrs={
                'class': 'form-control form-control-sm', 'placeholder': 'GST'
            }),
            'customer_address_bill_to': forms.Textarea(attrs={
                'class': 'form-control form-control-sm', 'rows': 2, 'placeholder': 'Address (Bill To)'
            }),
            'customer_address_ship_to': forms.Textarea(attrs={
                'class': 'form-control form-control-sm', 'rows': 2, 'placeholder': 'Address (Ship To)'
            }),
            'customer_contact': forms.TextInput(attrs={
                'class': 'form-control form-control-sm', 'placeholder': 'Contact'
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control form-control-sm', 'placeholder': 'Email'
            }),
            # 'dispatched_through': forms.TextInput(attrs={
            #     'class': 'form-control form-control-sm', 'placeholder': 'Dispatched Through'
            # }),
        }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
        # Preload existing customers in the dropdown
        # self.fields['customer_code'].widget.choices = [
        #     (c.code, f"{c.code} - {c.name}") for c in Customer.objects.all()
        # ]
        # options_html = "".join(
        #     [f"<option value='{c.code}'>{c.code} - {c.name}</option>" for c in Customer.objects.all()]
        # )
        # # Append datalist HTML to the widget's template
        # self.fields['customer_code'].widget.attrs['data-datalist'] = options_html




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
