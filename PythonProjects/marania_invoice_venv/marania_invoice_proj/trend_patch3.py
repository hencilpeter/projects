# Monthly best-performing product analysis (all products per month)
# Historical range filter (default: last 5 years)
_all_years = sorted(set(s.sales_entry_date.year for s in normalized_sales))
_best_start_year_str = request.GET.get('best_start_year', '')
_best_end_year_str = request.GET.get('best_end_year', '')
if _best_start_year_str:
    try:
        _best_start_year = int(_best_start_year_str)
    except (ValueError, TypeError):
        _best_start_year = (_all_years[-1] - 4) if _all_years else None
else:
    _best_start_year = (_all_years[-1] - 4) if _all_years else None
if _best_end_year_str:
    try:
        _best_end_year = int(_best_end_year_str)
    except (ValueError, TypeError):
        _best_end_year = _all_years[-1] if _all_years else None
else:
    _best_end_year = _all_years[-1] if _all_years else None
if _best_start_year is not None and _best_end_year is not None and _best_start_year > _best_end_year:
    _best_start_year, _best_end_year = _best_end_year, _best_start_year

_best_sales = [s for s in normalized_sales
               if (_best_start_year is None or s.sales_entry_date.year >= _best_start_year)
               and (_best_end_year is None or s.sales_entry_date.year <= _best_end_year)]

_profit_map = {s.sales_key: (s.profit_loss or Decimal('0')) for s in filtered_queryset
               if (_best_start_year is None or s.sales_entry_date.year >= _best_start_year)
               and (_best_end_year is None or s.sales_entry_date.year <= _best_end_year)}

monthly_groups = {}
for sale in _best_sales:
    ym_key = (sale.sales_entry_date.year, sale.sales_entry_date.month)
    prod = sale.product_code or 'Unknown'
    spec = sale.normalized_specification or sale.specification or 'Unknown'
    weight = sale.processed_weight if sale.processed_weight > 0 else sale.initial_weight
    profit = _profit_map.get(sale.sales_key, Decimal('0')) or Decimal('0')
    if ym_key not in monthly_groups:
        monthly_groups[ym_key] = {}
    if prod not in monthly_groups[ym_key]:
        monthly_groups[ym_key][prod] = {'product': prod, 'sales': Decimal('0'), 'weight': Decimal('0'), 'orders': 0, 'profit': Decimal('0'), 'specs': {}}
    monthly_groups[ym_key][prod]['sales'] += sale.total_amount
    monthly_groups[ym_key][prod]['weight'] += weight
    monthly_groups[ym_key][prod]['orders'] += 1
    monthly_groups[ym_key][prod]['profit'] += profit
    if spec not in monthly_groups[ym_key][prod]['specs']:
        monthly_groups[ym_key][prod]['specs'][spec] = {'spec': spec, 'sales': Decimal('0'), 'weight': Decimal('0'), 'orders': 0, 'profit': Decimal('0')}
    monthly_groups[ym_key][prod]['specs'][spec]['sales'] += sale.total_amount
    monthly_groups[ym_key][prod]['specs'][spec]['weight'] += weight
    monthly_groups[ym_key][prod]['specs'][spec]['orders'] += 1
    monthly_groups[ym_key][prod]['specs'][spec]['profit'] += profit

monthly_best_products = []
for ym_key in sorted(monthly_groups.keys()):
    products = sorted(monthly_groups[ym_key].values(), key=lambda p: (p['sales'], p['profit']), reverse=True)
    if not products:
        continue
    top_product = products[0]['product']
    for p in products:
        p['top_specs'] = sorted(p['specs'].values(), key=lambda s: (s['sales'], s['profit']), reverse=True)[:3]
        p['is_top'] = (p['product'] == top_product)
    monthly_best_products.append({
        'month': f"{ym_key[0]}-{ym_key[1]:02d}",
        'year': ym_key[0],
        'month_num': ym_key[1],
        'products': products,
    })

# pass to context via these names (already referenced)
_best_start_year_ctx = _best_start_year
_best_end_year_ctx = _best_end_year
_available_years_ctx = _all_years
PY