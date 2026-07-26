from .models import Invoice, InvoiceItem, Sales, Purchase

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

    "sales": {
        "model": Sales,
        "date_field": "sales_entry_date",
        "columns": [
            ("sales_entry_date", "Date"),
            ("invoice_no", "Invoice No"),
            ("order_no", "Order No"),
            ("customer", "Customer"),
            ("twine", "Twine"),
            ("speification", "Specification"),
            ("colour", "Colour"),
            ("piece_weight", "Piece Weight"),
            ("piece_count", "Piece Count"),
            ("initial_weight", "Initial Weight"),
            ("processed_weight", "Processed Weight"),
            ("unit_price", "Unit Price"),
            ("gst_rate", "GST Rate"),
            ("total_amount", "Total Amount"),
            ("delivery_date", "Delivery Date"),
            ("status", "Status"),
            ("payment_date", "Payment Date"),
            ("remarks", "Remarks"),
        ],
    },

    "purchase": {
        "model": Purchase,
        "date_field": "delivery_date",
        "columns": [
            ("delivery_date", "Delivery Date"),
            ("invoice_no", "Invoice No"),
            ("payment_due_date", "Payment Due Date"),
            ("payment_date", "Payment Date"),
            ("vendor", "Vendor"),
            ("order_description", "Order Description"),
            ("quantity_weight", "Quantity/Weight"),
            ("unit", "Unit"),
            ("unit_price", "Unit Price"),
            ("subtotal", "Subtotal"),
            ("gst_percent", "GST %"),
            ("gst_amount", "GST Amount"),
            ("total_amount", "Total Amount"),
            ("payment_status", "Payment Status"),
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


	
