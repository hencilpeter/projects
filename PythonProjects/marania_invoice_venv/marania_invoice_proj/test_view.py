import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marania_invoice_proj.settings')
django.setup()
from django.contrib.auth.models import User
from django.test import RequestFactory
from marania_invoice_app.views import profit_analytics_view
import json, re

user = User.objects.first()
factory = RequestFactory()
request = factory.get('/profit-analytics/')
request.user = user
response = profit_analytics_view(request)
content = response.content.decode()

# Check for json_script format
if 'productions-data' in content:
    print('productions-data ID found in HTML')
    # Django json_script uses id="xxx" format
    match = re.search(r'id="productions-data"[^>]*>(.*?)</script>', content, re.DOTALL)
    if match:
        raw = match.group(1).strip()
        print('Raw length:', len(raw))
        print('First 200 chars:', raw[:200])
    else:
        print('No script tag match')
else:
    print('productions-data NOT in HTML')
    # Search for what is there
    for line in content.split('\n'):
        if 'productions' in line.lower():
            print('Found line:', line[:200])
