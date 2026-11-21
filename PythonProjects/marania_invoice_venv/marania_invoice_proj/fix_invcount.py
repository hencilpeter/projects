p='marania_invoice_app/analytics/services/dashboard_metrics.py'
s=open(p,encoding='utf-8').read()

old='''    total_sales = sum((s.total_amount or Decimal('0')) for s in normalized_sales)
    total_quantity = sum((s.processed_weight if s.processed_weight and s.processed_weight > 0 else s.initial_weight or Decimal('0')) for s in normalized_sales)
    invoice_count = len(normalized_sales)
    active_customers = len(set(s.customer for s in normalized_sales if s.customer))'''
new='''    total_sales = sum((s.total_amount or Decimal('0')) for s in normalized_sales)
    total_quantity = sum((s.processed_weight if s.processed_weight and s.processed_weight > 0 else s.initial_weight or Decimal('0')) for s in normalized_sales)
    # Count distinct invoices: group by invoice_no when present; empty/NA/missing treated as one invoice per row
    _inv_keys = []
    for s in normalized_sales:
        inv = (getattr(s, 'invoice_no', None) or '').strip() if hasattr(s, 'invoice_no') else ''
        # NormalizedSale doesn't carry invoice_no; fall back to order_no grouping via sales_key uniqueness
        _inv_keys.append(s.sales_key)
    # Use order_no as invoice proxy when available on the sale record
    invoice_nos = []
    for s in normalized_sales:
        # NormalizedSale has no invoice_no field; use sales_key distinct count of unique order_no
        invoice_nos.append(getattr(s, 'order_no', None) or s.sales_key)
    # Distinct order_no, but treat empty/NA as per-row
    distinct = set()
    per_row = 0
    for s in normalized_sales:
        on = (getattr(s, 'order_no', None) or '').strip()
        if on and on.upper() not in ('', 'NA', 'N/A'):
            distinct.add(on)
        else:
            per_row += 1
    invoice_count = len(distinct) + per_row
    active_customers = len(set(s.customer for s in normalized_sales if s.customer))'''
assert old in s
s=s.replace(old,new,1)
open(p,'w',encoding='utf-8').write(s)
print('done')
PY