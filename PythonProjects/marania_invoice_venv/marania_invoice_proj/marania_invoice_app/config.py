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
            ("quantity_total","Quantity Total"),
            ("subtotal","subtotal"),
            ("cgst_amount","CGST Amount"),
            ("sgst_amount","SGST Amount"),
            ("igst_amount","IGST Amount"),
            ("round_off","round_off"),
            ("gross_total","Gross Total"),
            ("remark","Remarks"),
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


DERIVED_REPORT_CONFIG = {
    "sales":{
        "columns": [("Date","Date"),
                    ("Particulars","Particulars"),	
                    ("Voucher_No","Voucher_No"),	
                    ("GSTIN/UIN","GSTIN/UIN"),
                    ("Gross_Total","Gross_Total"),	
                    ("GST","GST"),
                    ("CGST","CGST"),	
                    ("SGST","SGST"),
                    ("ROUND_OFF","ROUND_OFF"),
                    ],
    }
}


	
