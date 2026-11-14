@login_required
def price_list_update_config(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body) if request.body else {}
    except Exception:
        data = request.POST
    pk = data.get('price_list_key') if isinstance(data, dict) else request.POST.get('price_list_key')
    try:
        config = PriceListConfiguration.objects.get(price_list_key=pk)
    except (PriceListConfiguration.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'config not found'}, status=404)

    def _dec(key, default=None):
        v = data.get(key) if isinstance(data, dict) else request.POST.get(key)
        if v is None or v == '':
            return default
        try:
            return Decimal(str(v))
        except Exception:
            return default

    if 'twine_price' in data or 'twine_price' in request.POST:
        v = _dec('twine_price')
        if v is not None: config.twine_price = v
    if 'colour_price_per_kg' in data or 'colour_price_per_kg' in request.POST:
        v = _dec('colour_price_per_kg')
        if v is not None: config.colour_price_per_kg = v
    if 'additional_cost_starting_depth_md' in data or 'additional_cost_starting_depth_md' in request.POST:
        v = data.get('additional_cost_starting_depth_md') if isinstance(data, dict) else request.POST.get('additional_cost_starting_depth_md')
        if v not in (None, ''):
            try:
                config.additional_cost_starting_depth_md = int(v)
            except (ValueError, TypeError):
                pass
    if 'small_mesh_depth_price_per_kg' in data or 'small_mesh_depth_price_per_kg' in request.POST:
        v = _dec('small_mesh_depth_price_per_kg')
        if v is not None: config.small_mesh_depth_price_per_kg = v
    if 'processing_cost_per_kg' in data or 'processing_cost_per_kg' in request.POST:
        v = _dec('processing_cost_per_kg')
        if v is not None: config.processing_cost_per_kg = v
    if 'additional_cost_per_kg' in data or 'additional_cost_per_kg' in request.POST:
        v = _dec('additional_cost_per_kg')
        if v is not None: config.additional_cost_per_kg = v
    if 'mesh_depth' in data or 'mesh_depth' in request.POST:
        v = _dec('mesh_depth')
        if v is not None: config.mesh_depth = v
    if 'gst_included' in data or 'gst_included' in request.POST:
        v = data.get('gst_included') if isinstance(data, dict) else request.POST.get('gst_included')
        if isinstance(v, str):
            config.gst_included = v.lower() in ('true', '1', 'on', 'yes')
        elif v is not None:
            config.gst_included = bool(v)
    if 'machine_number' in data or 'machine_number' in request.POST:
        v = data.get('machine_number') if isinstance(data, dict) else request.POST.get('machine_number')
        if v is not None:
            config.machine_number = v
    config.save()
    return JsonResponse({'success': True})
PY
