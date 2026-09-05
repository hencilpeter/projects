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
    "PriceListConfiguration": PriceListConfiguration,
    "ProfitLoss": ProfitLoss,
    "TwineInventory": TwineInventory,
    "ExcelSheet": ExcelSheet,
    "PaymentReceipt": PaymentReceipt,
    "PaymentAllocation": PaymentAllocation,
    "OpeningBalance": OpeningBalance,
    "MaterialConversionRatio": MaterialConversionRatio,
    "ProcessingCost": ProcessingCost,
    "MachineOperationalCost": MachineOperationalCost,
    "AdditionalCost": AdditionalCost,
    "ExtraMeshConfig": ExtraMeshConfig,
    "PriceListColourConfiguration": PriceListColourConfiguration,
    "Production": Production,
    "ProfitAnalytics": ProfitAnalytics,
    "PieceWeightAnalyser": PieceWeightAnalyser,
    "SettlementInvoice": SettlementInvoice,
    "ApplicationModule": ApplicationModule,
    "UserCategory": UserCategory,
    "UserProfile": UserProfile,
    "AuditLog": AuditLog,
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
    "PriceListConfiguration": "",
    "ProfitLoss": "",
    "TwineInventory": "",
    "ExcelSheet": "",
    "PaymentReceipt": "receipt_no",
    "PaymentAllocation": "",
    "OpeningBalance": "",
    "MaterialConversionRatio": "material_code",
    "ProcessingCost": "material_code",
    "MachineOperationalCost": "machine_number",
    "AdditionalCost": "",
    "ExtraMeshConfig": "",
    "PriceListColourConfiguration": "",
    "Production": "",
    "ProfitAnalytics": "",
    "PieceWeightAnalyser": "",
    "SettlementInvoice": "settlement_invoice_number",
    "ApplicationModule": "key",
    "UserCategory": "name",
    "UserProfile": "",
    "AuditLog": "",
}

# Import order for Backup Import All - respects FK dependencies
# Models must be imported in this order to avoid foreign key violations
IMPORT_ORDER = [
    # Level 0: No FK dependencies
    "PartyRole",
    "Configuration",
    "CompanySettings",
    "AdditionalCost",
    "ExtraMeshConfig",
    "MaterialConversionRatio",
    "ProcessingCost",
    "MachineOperationalCost",
    "ExcelSheet",
    "ApplicationModule",

    # Level 1: Depends on PartyRole
    "Parties",

    # Level 2: Depends on Parties
    "Transportation",
    "Materials",
    "UserCategory",

    # Level 3: Depends on Materials, Parties
    "Product",

    # Level 4: Depends on Product, Parties
    "PriceCatalog",
    "PriceListConfiguration",
    "PriceListColourConfiguration",

    # Level 5: Depends on PriceCatalog, Parties
    "CustomerPriceCatalog",

    # Level 6: Depends on Parties (no direct FK but references)
    "Order",

    # Level 7: Depends on Order
    "OrderSpecification",
    "Production",

    # Level 8: Depends on Production
    "ProfitAnalytics",

    # Level 9: Depends on Parties (string references)
    "Invoice",

    # Level 10: Depends on Invoice
    "InvoiceItem",

    # Level 11: Depends on Parties, Order, Invoice (string references)
    "Sales",
    "Purchase",
    "Expense",
    "OpeningBalance",
    "SettlementInvoice",

    # Level 12: Depends on Invoice, Expense, OpeningBalance, SettlementInvoice
    "PaymentReceipt",

    # Level 13: Depends on PaymentReceipt, Invoice, Expense, OpeningBalance, SettlementInvoice
    "PaymentAllocation",

    # Level 14: Standalone financial data
    "ProfitLoss",
    "TwineInventory",
    "PieceWeightAnalyser",

    # Level 15: User management (depends on ApplicationModule)
    "UserProfile",

    # Level 16: Audit log (depends on auth.User - imported last)
    "AuditLog",
]
