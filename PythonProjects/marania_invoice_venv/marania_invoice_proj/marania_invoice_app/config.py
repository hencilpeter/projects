from .models import Invoice, InvoiceItem

REPORT_CONFIG = {
    "invoice": {
        "model": Invoice,
        "date_field": "invoice_date",
        "columns": [
            ("invoice_date", "Date"),
            ("invoice_number", "Invoice No"),
            ("customer_name", "Customer"),
            ("customer_gst", "GST"),
        ],
    },

    "invoice_item": {
        "model": InvoiceItem,
        "date_field": "invoice__invoice_date",
        "columns": [
            ("invoice__invoice_date", "Invoice Date"),
            ("invoice__invoice_number", "Invoice No"),
            ("invoice__customer_name","Customer"),
            ("item_description", "Description"),
            ("item_quantity", "Qty"),
            ("item_price", "Price"),
            ("item_gst_amount", "GST"),
            ("item_total_with_gst", "Total"),
        ],
    },
}
