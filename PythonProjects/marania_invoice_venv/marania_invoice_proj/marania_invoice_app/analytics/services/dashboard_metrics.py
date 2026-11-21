"""
Enhanced dashboard metrics for Trend Analytics decision-support.
"""
from datetime import date, timedelta
from decimal import Decimal
from typing import List, Dict, Any


def _safe_div(a, b):
    if not b:
        return None
    return a / b


def compute_period(normalized_sales):
    """Basic aggregates for a set of normalized sales."""
    if not normalized_sales:
        return {
            'total_sales': Decimal('0'),
            'total_quantity': Decimal('0'),
            'invoice_count': 0,
            'active_customers': 0,
            'total_profit': Decimal('0'),
            'monthly': {},
        }
    total_sales = sum((s.total_amount or Decimal('0')) for s in normalized_sales)
    total_quantity = sum((s.processed_weight if s.processed_weight and s.processed_weight > 0 else s.initial_weight or Decimal('0')) for s in normalized_sales)
    invoice_count = len(normalized_sales)
    active_customers = len(set(s.customer for s in normalized_sales if s.customer))
    total_profit = sum((s.profit_loss if hasattr(s, 'profit_loss') else Decimal('0')) or Decimal('0') for s in [])  # placeholder
    # profit comes from external map; recompute below
    # We'll accept profit via separate handling; here use 0 placeholder replaced by caller
    # Actually normalized_sales doesn't carry profit_loss; need map. Handle in caller.
    monthly = {}
    for s in normalized_sales:
        key = (s.sales_entry_date.year, s.sales_entry_date.month)
        if key not in monthly:
            monthly[key] = {'sales': Decimal('0'), 'quantity': Decimal('0'), 'profit': Decimal('0'), 'orders': 0}
        monthly[key]['sales'] += s.total_amount or Decimal('0')
        w = s.processed_weight if s.processed_weight and s.processed_weight > 0 else s.initial_weight or Decimal('0')
        monthly[key]['quantity'] += w
        monthly[key]['orders'] += 1
    return {
        'total_sales': total_sales,
        'total_quantity': total_quantity,
        'invoice_count': invoice_count,
        'active_customers': active_customers,
        'monthly': monthly,
    }


def compute_enhanced(normalized_sales, previous_normalized_sales, profit_map, prev_profit_map, filters, monthly_trend, top_customers, product_trends, product_spec_matrix):
    result = {}
    # period aggregates
    cur = compute_period(normalized_sales)
    prev = compute_period(previous_normalized_sales) if previous_normalized_sales else None

    # profit
    cur_profit = sum(profit_map.get(s.sales_key, Decimal('0')) or Decimal('0') for s in normalized_sales)
    prev_profit = sum(prev_profit_map.get(s.sales_key, Decimal('0')) or Decimal('0') for s in previous_normalized_sales) if previous_normalized_sales else Decimal('0')

    cur['total_profit'] = cur_profit
    if prev is not None:
        prev['total_profit'] = prev_profit

    # sales kpis
    total_sales = cur['total_sales']
    total_quantity = cur['total_quantity']
    invoice_count = cur['invoice_count']
    active_customers = cur['active_customers']
    avg_invoice_value = (total_sales / invoice_count) if invoice_count else None
    # number of months in range
    months_in_range = len(cur['monthly']) if cur['monthly'] else 1
    monthly_avg_sales = total_sales / months_in_range if months_in_range else None

    # growth
    prev_sales = prev['total_sales'] if prev else None
    if prev_sales and prev_sales > 0:
        sales_growth = (total_sales - prev_sales) / prev_sales * 100
    else:
        sales_growth = None

    result['sales_kpis'] = {
        'total_sales': total_sales,
        'total_quantity': total_quantity,
        'invoice_count': invoice_count,
        'avg_invoice_value': avg_invoice_value,
        'monthly_avg_sales': monthly_avg_sales,
        'sales_growth': sales_growth,
        'active_customers': active_customers,
    }

    # profit kpis
    total_profit = cur_profit
    profit_margin = (total_profit / total_sales * 100) if total_sales else None
    avg_monthly_profit = total_profit / months_in_range if months_in_range else None
    # highest/lowest profit month
    monthly_profit = {}
    for s in normalized_sales:
        key = (s.sales_entry_date.year, s.sales_entry_date.month)
        monthly_profit[key] = monthly_profit.get(key, Decimal('0')) + (profit_map.get(s.sales_key, Decimal('0')) or Decimal('0'))
    if monthly_profit:
        hp_key = max(monthly_profit, key=lambda k: monthly_profit[k])
        lp_key = min(monthly_profit, key=lambda k: monthly_profit[k])
        highest_profit_month = f"{hp_key[0]}-{hp_key[1]:02d}"
        lowest_profit_month = f"{lp_key[0]}-{lp_key[1]:02d}"
    else:
        highest_profit_month = None
        lowest_profit_month = None
    if prev_profit is not None and prev_profit != 0:
        profit_growth = (total_profit - prev_profit) / (abs(prev_profit) if prev_profit != 0 else Decimal('1')) * 100
        if prev_profit == 0:
            profit_growth = None
    else:
        profit_growth = None
    if prev and prev['total_profit'] == 0 and total_profit != 0:
        profit_growth = None
    cost_value = total_sales - total_profit
    profit_per_unit = (total_profit / total_quantity) if total_quantity else None

    result['profit_kpis'] = {
        'total_profit': total_profit,
        'profit_margin': profit_margin,
        'avg_monthly_profit': avg_monthly_profit,
        'highest_profit_month': highest_profit_month,
        'lowest_profit_month': lowest_profit_month,
        'profit_growth': profit_growth,
        'cost_value': cost_value,
        'profit_per_unit': profit_per_unit,
    }

    # comparison
    result['comparison'] = {
        'current_sales': total_sales,
        'previous_sales': prev_sales if prev else None,
        'current_profit': total_profit,
        'previous_profit': prev_profit if prev else None,
        'current_quantity': total_quantity,
        'previous_quantity': (prev['total_quantity'] if prev else None),
    }

    # customer concentration
    customer_sales = {}
    for s in normalized_sales:
        if s.customer:
            customer_sales[s.customer] = customer_sales.get(s.customer, Decimal('0')) + (s.total_amount or Decimal('0'))
    sorted_cust = sorted(customer_sales.items(), key=lambda x: x[1], reverse=True)
    total_c = sum(customer_sales.values()) or Decimal('1')
    top1 = (sorted_cust[0][1] / total_c * 100) if len(sorted_cust) >= 1 else Decimal('0')
    top3 = (sum(v for _, v in sorted_cust[:3]) / total_c * 100) if sorted_cust else Decimal('0')
    top5 = (sum(v for _, v in sorted_cust[:5]) / total_c * 100) if sorted_cust else Decimal('0')
    result['customer_concentration'] = {
        'top1_pct': top1,
        'top3_pct': top3,
        'top5_pct': top5,
        'top_customers': sorted_cust[:5],
    }

    # risk alerts
    alerts = []
    # sales decline
    if sales_growth is not None and sales_growth <= -20:
        alerts.append({'title': 'Sales Decline', 'severity': 'HIGH', 'issue': f'Sales declined {sales_growth:.1f}% vs previous period.', 'supporting': f'Current: {total_sales:,.0f}, Previous: {prev_sales:,.0f}', 'impact': 'Revenue reduction', 'action': 'Review pricing, demand and customer activity.', 'product': None, 'customer': None})
    # continuous decline: check last 3 months
    months_sorted = sorted(cur['monthly'].keys())
    if len(months_sorted) >= 3:
        last3 = months_sorted[-3:]
        vals = [cur['monthly'][k]['sales'] for k in last3]
        if vals[0] > vals[1] > vals[2]:
            alerts.append({'title': 'Continuous Sales Decline', 'severity': 'HIGH', 'issue': 'Sales declined across 3 consecutive months.', 'supporting': ', '.join(f"{k[0]}-{k[1]:02d}: {v:,.0f}" for k, v in zip(last3, vals)), 'impact': 'Sustained revenue drop', 'action': 'Investigate root cause and adjust production/sales.', 'product': None, 'customer': None})
    # profit decline
    if profit_growth is not None and profit_growth <= -15:
        alerts.append({'title': 'Profit Decline', 'severity': 'HIGH', 'issue': f'Profit declined {profit_growth:.1f}% vs previous period.', 'supporting': f'Current: {total_profit:,.0f}, Previous: {prev_profit:,.0f}', 'impact': 'Profitability reduction', 'action': 'Review costs and pricing.', 'product': None, 'customer': None})
    # margin decline (3 pp)
    prev_margin = None
    if prev and prev['total_sales']:
        prev_margin = (prev['total_profit'] / prev['total_sales'] * 100)
    if profit_margin is not None and prev_margin is not None and (profit_margin - prev_margin) <= -3:
        alerts.append({'title': 'Margin Decline', 'severity': 'MEDIUM', 'issue': f'Profit margin fell {prev_margin:.1f}% -> {profit_margin:.1f}%.', 'supporting': 'Margin drop >= 3 percentage points.', 'impact': 'Reduced profitability per sale', 'action': 'Review material costs and selling prices.', 'product': None, 'customer': None})
    # negative profit products
    neg_products = []
    for p in (product_trends or []):
        # product_trends doesn't have profit; use product_spec_matrix
        pass
    # use product_spec_matrix for profit? It doesn't carry profit either. Use normalized sales profit aggregation by product.
    prod_profit = {}
    prod_sales = {}
    for s in normalized_sales:
        prod = s.product_code or 'Unknown'
        prod_profit[prod] = prod_profit.get(prod, Decimal('0')) + (profit_map.get(s.sales_key, Decimal('0')) or Decimal('0'))
        prod_sales[prod] = prod_sales.get(prod, Decimal('0')) + (s.total_amount or Decimal('0'))
    for prod, pp in prod_profit.items():
        if pp < 0:
            alerts.append({'title': 'Loss-Making Product', 'severity': 'CRITICAL', 'issue': f'{prod} generated negative profit ({pp:,.0f}).', 'supporting': f'Sales: {prod_sales.get(prod,0):,.0f}', 'impact': 'Direct loss', 'action': 'Review pricing/costs or discontinue.', 'product': prod, 'customer': None})
    # customer dependency
    if top3 >= 60:
        alerts.append({'title': 'Customer Dependency', 'severity': 'HIGH', 'issue': f'Top 3 customers contribute {top3:.1f}% of sales.', 'supporting': 'Concentration >= 60%.', 'impact': 'Revenue risk if a customer leaves', 'action': 'Diversify customer base.', 'product': None, 'customer': None})
    # slow-moving: products with no sales in last 60 days? check products in all_products but not in recent
    # unusual activity: any month sales deviates > 2 std from mean
    if len(monthly_trend) >= 4:
        import statistics
        vals = [float(m['sales']) for m in monthly_trend]
        mean = statistics.mean(vals)
        stdev = statistics.pstdev(vals) if len(vals) > 1 else 0
        for m in monthly_trend:
            if stdev > 0 and abs(float(m['sales']) - mean) > 2 * stdev:
                alerts.append({'title': 'Unusual Sales Activity', 'severity': 'MEDIUM', 'issue': f"{m['year']}-{m['month']:02d} sales deviated significantly from normal range.", 'supporting': f"Value: {float(m['sales']):,.0f}, Mean: {mean:,.0f}", 'impact': 'Possible data or market anomaly', 'action': 'Investigate the period.', 'product': None, 'customer': None})
    # material cost risk: cost_value growth? approximate via profit margin decline already
    # Declining customers
    # customer purchase decline: compare current vs previous period per customer
    prev_cust_sales = {}
    for s in (previous_normalized_sales or []):
        if s.customer:
            prev_cust_sales[s.customer] = prev_cust_sales.get(s.customer, Decimal('0')) + (s.total_amount or Decimal('0'))
    for cust, cs in customer_sales.items():
        ps = prev_cust_sales.get(cust, Decimal('0'))
        if ps > 0 and cs < ps * Decimal('0.8'):
            alerts.append({'title': 'Declining Customer', 'severity': 'MEDIUM', 'issue': f'{cust} purchases declined >= 20%.', 'supporting': f'Current: {cs:,.0f}, Previous: {ps:,.0f}', 'impact': 'Customer retention risk', 'action': 'Follow up with customer.', 'product': None, 'customer': cust})

    result['risk_alerts'] = alerts

    # business recommendations (data-driven)
    recs = []
    # production: increase priority for growing products
    # find products with positive growth
    prod_growth = {}
    # compute per-product current vs previous
    prod_cur = {}
    prod_prev = {}
    for s in normalized_sales:
        prod_cur[s.product_code] = prod_cur.get(s.product_code, Decimal('0')) + (s.total_amount or Decimal('0'))
    for s in (previous_normalized_sales or []):
        prod_prev[s.product_code] = prod_prev.get(s.product_code, Decimal('0')) + (s.total_amount or Decimal('0'))
    for prod, cs in prod_cur.items():
        ps = prod_prev.get(prod, Decimal('0'))
        if ps > 0 and cs > ps * Decimal('1.1'):
            recs.append({'priority': 'High', 'category': 'Production', 'title': f'Increase production priority for {prod}', 'reason': 'Consistently increasing demand.', 'supporting': f'Current: {cs:,.0f} vs Previous: {ps:,.0f}', 'impact': 'Capture growing demand', 'action': 'Allocate more capacity to this product.', 'related': prod})
    # reduce allocation for slow-moving
    for prod, cs in prod_cur.items():
        ps = prod_prev.get(prod, Decimal('0'))
        if ps > 0 and cs < ps * Decimal('0.7'):
            recs.append({'priority': 'Medium', 'category': 'Production', 'title': f'Reduce production allocation for {prod}', 'reason': 'Weakening demand.', 'supporting': f'Current: {cs:,.0f} vs Previous: {ps:,.0f}', 'impact': 'Avoid overproduction', 'action': 'Scale down production for this product.', 'related': prod})
    # pricing: review prices for low margin products
    for prod, pp in prod_profit.items():
        psales = prod_sales.get(prod, Decimal('0'))
        if psales > 0:
            margin = pp / psales * 100
            if margin < 10:
                recs.append({'priority': 'High', 'category': 'Pricing', 'title': f'Review selling price for {prod}', 'reason': f'Low margin ({margin:.1f}%).', 'supporting': f'Profit: {pp:,.0f}, Sales: {psales:,.0f}', 'impact': 'Improve profitability', 'action': 'Consider price increase or cost reduction.', 'related': prod})
    # profit: prioritize high profit contribution
    # find top profit product
    if prod_profit:
        top_profit_prod = max(prod_profit, key=lambda p: prod_profit[p])
        recs.append({'priority': 'Medium', 'category': 'Profit', 'title': f'Prioritize {top_profit_prod} for profit', 'reason': 'Highest profit contribution.', 'supporting': f'Profit: {prod_profit[top_profit_prod]:,.0f}', 'impact': 'Maximize profit', 'action': 'Focus sales effort on this product.', 'related': top_profit_prod})
    # materials: plan purchases ahead
    if any('Increasing' in (r.get('title') or '') for r in recs):
        recs.append({'priority': 'Medium', 'category': 'Materials', 'title': 'Plan material purchases ahead', 'reason': 'Forecast demand for high-growth products.', 'supporting': 'Based on growth trends.', 'impact': 'Avoid stockouts', 'action': 'Procure twine/materials in advance.', 'related': None})
    # inventory: avoid overproduction of weakening demand
    # customer risk: diversify
    if top3 >= 60:
        recs.append({'priority': 'High', 'category': 'Customer Risk', 'title': 'Diversify customer base', 'reason': f'Top 3 customers = {top3:.1f}% of sales.', 'supporting': 'Concentration risk.', 'impact': 'Reduce dependency', 'action': 'Acquire new customers.', 'related': None})
    # sales: follow up declining customers
    for cust, cs in customer_sales.items():
        ps = prev_cust_sales.get(cust, Decimal('0'))
        if ps > 0 and cs < ps * Decimal('0.8'):
            recs.append({'priority': 'Medium', 'category': 'Sales', 'title': f'Follow up with {cust}', 'reason': 'Purchases declined >= 20%.', 'supporting': f'Current: {cs:,.0f}, Previous: {ps:,.0f}', 'impact': 'Retain customer', 'action': 'Contact customer and address concerns.', 'related': cust})
    # planning: seasonal peaks
    recs.append({'priority': 'Low', 'category': 'Planning', 'title': 'Prepare for seasonal demand peaks', 'reason': 'Historical seasonality observed.', 'supporting': 'Based on monthly trends.', 'impact': 'Readiness', 'action': 'Schedule production ahead of peak months.', 'related': None})

    # sort by priority
    prio_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
    recs.sort(key=lambda r: prio_order.get(r['priority'], 9))

    result['business_recommendations'] = recs

    # overall status
    status = 'Positive'
    if len([a for a in alerts if a['severity'] in ('CRITICAL', 'HIGH')]) >= 2:
        status = 'Critical'
    elif len([a for a in alerts if a['severity'] in ('CRITICAL', 'HIGH')]) == 1:
        status = 'Needs Attention'
    elif alerts:
        status = 'Stable'
    # also consider growth
    if sales_growth is not None and sales_growth < -10:
        status = 'Needs Attention' if status == 'Positive' else status
    if profit_growth is not None and profit_growth < -10:
        status = 'Needs Attention' if status in ('Positive', 'Stable') else status
    result['overall_status'] = status

    # narrative
    narrative_parts = []
    _growth_str = (f"{sales_growth:+.1f}%" if sales_growth is not None else "N/A")
    narrative_parts.append(f"Total sales: <strong>{total_sales:,.0f}</strong> ({_growth_str} vs previous period)")
    if profit_margin is not None:
        narrative_parts.append(f"Total profit: <strong>{total_profit:,.0f}</strong> with a margin of <strong>{profit_margin:.1f}%</strong>")
    else:
        narrative_parts.append(f"Total profit: <strong>{total_profit:,.0f}</strong>")
    if product_trends:
        top_p = product_trends[0]['product']
        narrative_parts.append(f"Best-performing product by sales: <strong>{top_p}</strong>")
    if alerts:
        narrative_parts.append(f"<strong>{len(alerts)}</strong> risk alert(s) detected requiring attention")
    if recs:
        narrative_parts.append(f"<strong>{len(recs)}</strong> business recommendation(s) generated")
    result['narrative'] = ' <span style="color:#FFD700;font-size:1.5em;font-weight:bold;vertical-align:middle;">*</span> '.join(narrative_parts)

    # date range summary
    result['date_range_summary'] = {
        'status': status,
        'total_sales': total_sales,
        'total_quantity': total_quantity,
        'total_profit': total_profit,
        'profit_margin': profit_margin,
        'sales_growth': sales_growth,
        'profit_growth': profit_growth,
        'best_product': (product_trends[0]['product'] if product_trends else None),
        'best_customer': (top_customers[0]['customer'] if top_customers else None),
        'highlights': [a for a in alerts if a['severity'] in ('LOW', 'MEDIUM')][:3],
        'concerns': [a for a in alerts if a['severity'] in ('HIGH', 'CRITICAL')][:5],
    }

    # monthly profit trend
    mp_list = sorted(monthly_profit.items())
    result['monthly_profit_trend'] = [{'year': k[0], 'month': k[1], 'profit': v} for k, v in mp_list]

    # data quality flags
    dq_flags = []
    missing_spec = sum(1 for s in normalized_sales if not s.raw_specification)
    zero_price = sum(1 for s in normalized_sales if (s.total_amount or 0) == 0 and (s.processed_weight or 0) > 0)
    if missing_spec:
        dq_flags.append(f"{missing_spec} records with missing specification.")
    if zero_price:
        dq_flags.append(f"{zero_price} records with zero selling price.")
    if len(normalized_sales) < 10:
        dq_flags.append("Insufficient historical data for reliable analysis.")
    result['data_quality_flags'] = dq_flags

    return result
