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
}