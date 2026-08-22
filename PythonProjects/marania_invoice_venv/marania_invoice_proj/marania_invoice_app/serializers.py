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
    "OrderSpecification": OrderSpecification,
    "Sales": Sales,
    "Purchase": Purchase,
    "Expense": Expense,
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
    "Order": "",
    "OrderSpecification": "",
    "Sales": "",
    "Purchase": "",
    "Expense": "",
}