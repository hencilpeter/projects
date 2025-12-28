from django import forms
from .models import Parties
from .models import Invoice, InvoiceItem
from .models import Transportation
from .models import CompanySettings
from .models import PriceCatalog
from .models import CustomerPriceCatalog
from .models import PartyRole

from django.forms import inlineformset_factory
from django.forms import modelformset_factory

class CustomerForm(forms.ModelForm):
    # Use a separate field for selecting roles in the form
    partyroles = forms.ModelMultipleChoiceField(
        queryset=PartyRole.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Parties
        fields = [
            'code', 'name', 'gst', 'phone', 'email',
            'address_bill_to', 'address_ship_to', 'is_within_state',
            'partyroles'
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Code'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'gst': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'GST'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'address_bill_to': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'style': 'width:400px;', 'placeholder': 'Billing address'}),
            'address_ship_to': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'style': 'width:400px;', 'placeholder': 'Shipping address'}),
            'is_within_state': forms.Select(attrs={'class': 'form-select'}, choices=[(True, 'Yes'), (False, 'No')]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Prepopulate partyroles field with existing roles
        if self.instance.pk:
            self.fields['partyroles'].initial = self.instance.roles.all()

    def save(self, commit=True):
        # Save the Parties instance first
        instance = super().save(commit=False)
        if commit:
            instance.save()
        # Save ManyToMany field
        instance.roles.set(self.cleaned_data['partyroles'])
       
        return instance


class InvoiceForm(forms.ModelForm):
    # Manually declare only fields that need datalist / custom placeholder
    
    customer_code = forms.CharField(
        label='Customer Code',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Customer Code (Bill to)',
            'list': 'customer_code_list',  # links to datalist id in HTML
        })
    )
    
    customer_name = forms.CharField(
        label='Customer Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Customer Name (Bill to)',
            'list': 'customer_name_list',  # links to datalist id in HTML
        })
    )
    
    ship_to_customer_code = forms.CharField(
        label='Customer Code',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Customer Code (Ship to)',
            'list': 'ship_to_customer_code_list',  # links to datalist id in HTML
        })
    )
    
    ship_to_customer_name = forms.CharField(
        label='Customer Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Customer Name (Ship to)',
            'list': 'ship_to_customer_name_list',  # links to datalist id in HTML
        })
    )
    
    dispatched_through = forms.CharField(
        label='Dispatched Through',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Dispatched Through',
            'list': 'dispatched_through_list',  # links to datalist id in HTML
        }),
        required=False,
    )

    vehicle_name_number = forms.CharField(
        label='Vehicle Namd & Number',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Vehicle Name & Number',
            'list': 'vehicle_name_number_list',  # links to datalist id in HTML
        }),
        required=False,
    )
    
    transporter_gst = forms.CharField(
        label='Transporter GST',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Transporter GST',
            'list': 'transporter_gst_list',  # links to datalist id in HTML
        }),
        required=False,
    )

    
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
            'dispatched_through',
            'vehicle_name_number',
            'transporter_gst'
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
        fields = ['item_spec','item_code', 'item_description','item_mesh_size','item_mesh_depth', 'item_quantity', 'item_price',
                  'item_gst_amount','item_total_with_gst','item_hsn_code']

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
            'item_gst_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'GST Amount',
                'step': '0.01'
            }),

            'item_total_with_gst': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total Price (with GST)',
                'step': '0.01'
            }),

            'item_hsn_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'HSN Code'
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

class CompanySettingsForm(forms.ModelForm):

    class Meta:
        model = CompanySettings
        fields = [
            "current_invoice_number",
            "invoice_prefix",
            "igst",
            "cgst",
            "sgst",
            "finance_year",
            "company_title",
            "company_address",
            "company_gst",
            "company_state",
            "company_state_code",
            "company_phone",
            "company_email",
            "bank_account_name",
            "bank_name",
            "bank_account_number",
            "bank_branch",
            "bank_ifsc",
            "colour_charge",
            "small_mesh_size_charge",

        ]

        labels = {
            "current_invoice_number": "Current Invoice Number",
            "invoice_prefix": "Invoice Prefix",
            "igst": "IGST ( Integrated Goods and Services Tax % )",
            "cgst": "CGST ( Central Goods and Services Tax % )",
            "sgst": "SGST ( State Goods and Services Tax %)",
            "finance_year": "Finance Year",
            "company_title": "Company Name",
            "company_address": "Company Address",
            "company_gst":"Company GST",
            "company_state":"Company State",
            "company_state_code":"State Code",
            "company_phone": "Contact Number",
            "company_email": "Email Address",
            "bank_account_name":"Account Holder Name",
            "bank_name":"Bank Name",
            "bank_account_number":"Account Number",
            "bank_branch": "Bank Branch Name",
            "bank_ifsc": "Branch IFSC",
            "colour_charge":"Colour Charge",
            "small_mesh_size_charge":"Small Mesh Size Charge",
        }

        widgets = {
            "company_address": forms.Textarea(
                attrs={
                    "rows": 4,                 # Show 4-line height
                    "class": "form-control",   # Bootstrap styling
                    "placeholder": "company address",
                }
            ),
            "company_title": forms.TextInput(attrs={"class": "form-control"}),
            "current_invoice_number": forms.NumberInput(attrs={"class": "form-control"}),
            "invoice_prefix": forms.TextInput(attrs={"class": "form-control"}),
            "igst": forms.NumberInput(attrs={"class": "form-control"}),
            "cgst": forms.NumberInput(attrs={"class": "form-control"}),
            "sgst": forms.NumberInput(attrs={"class": "form-control"}),
            "company_phone": forms.TextInput(attrs={"class": "form-control"}),
            "company_email": forms.EmailInput(attrs={"class": "form-control"}),
            "bank_account_name":forms.TextInput(attrs={"class": "form-control"}),
            "bank_name":forms.TextInput(attrs={"class": "form-control"}),
            "bank_account_number":forms.TextInput(attrs={"class": "form-control"}),
            "bank_branch": forms.TextInput(attrs={"class": "form-control"}),
            "bank_ifsc": forms.TextInput(attrs={"class": "form-control"}),
            "colour_charge":forms.NumberInput(attrs={"class": "form-control"}),
            "small_mesh_size_charge":forms.NumberInput(attrs={"class": "form-control"}),

        }


# 👇 This creates a formset of items linked to an Invoice
InvoiceItemFormSet = inlineformset_factory(
    Invoice, InvoiceItem,
    form=InvoiceItemForm,
    extra=1,  # how many blank forms to show initially
    can_delete=True
)




class PriceListForm(forms.ModelForm):
    class Meta:
        model = PriceCatalog
        fields = [
            "product",
            "code",
            "customer_group",
            "sequence_id",
            "mesh_size_start",
            "mesh_size_end",
            "price",
            "is_active",
            "note",
        ]

PriceListFormSet = modelformset_factory(
    PriceCatalog,
    form=PriceListForm,
    extra=1,          # at least one empty row
    can_delete=True   # optional delete checkbox
)


class CustomerPriceCatalogForm(forms.ModelForm):
    class Meta:
        model = CustomerPriceCatalog
        fields = ['customer', 'price_catalog', 'gst_included', 'colour_extra_price', 'small_mesh_size_extra_price', 'remark']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'price_catalog': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'gst_included': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'colour_extra_price': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01'}),
            'small_mesh_size_extra_price': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01'}),
            'remark': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 2}),
        }

