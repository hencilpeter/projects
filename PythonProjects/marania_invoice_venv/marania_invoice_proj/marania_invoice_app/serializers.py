from .models import *

MODEL_REGISTRY = {
    "PartyRole": PartyRole,
    "Parties": Parties,
    "Materials": Materials,
    "Product": Product,
    "PriceCatalog": PriceCatalog,
    "CustomerPriceCatalog": CustomerPriceCatalog,
    "Invoice": Invoice,
    "InvoiceItem": InvoiceItem,
    "Transportation": Transportation,
    "Configuration": Configuration,
    "CompanySettings": CompanySettings,
    "Order": Order,
    "Sales": Sales,
}

UNIQUE_KEY_MODEL = {
    "PartyRole": "",
    "Parties": "code",
    "Materials": "code",
    "Product": "code",
    "PriceCatalog": "",
    "CustomerPriceCatalog": "",
    "Invoice": "invoice_number",
    "InvoiceItem": "",
    "Transportation": "",
    "Configuration": "",
    "CompanySettings": "",
    "Order": "order_key",
    "Sales": "sales_key",
}