@login_required
def price_list_save_prices(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body) if request.body else {}
    except Exception:
        data = request.POST
    pk = data.get('price_list_key') if isinstance(data, dict) else request.POST.get('price_list_key')
    overrides = data.get('price_overrides') if isinstance(data, dict) else request.POST.get('price_overrides')
    if isinstance(overrides, str):
        try:
            overrides = json.loads(overrides)
        except Exception:
            overrides = {}
    if not isinstance(overrides, dict):
        overrides = {}
    # normalize
    clean = {}
    for k, v in overrides.items():
        try:
            clean[str(k)] = str(Decimal(str(v)).quantize(Decimal('0.01')))
        except Exception:
            continue
    try:
        config = PriceListConfiguration.objects.get(price_list_key=pk)
    except (PriceListConfiguration.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'config not found'}, status=404)
    config.price_overrides = json.dumps(clean)
    config.save(update_fields=['price_overrides', 'updated_at'])
    return JsonResponse({'success': True, 'saved': len(clean)})
PY
