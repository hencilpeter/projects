from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
#@login_required
def show_dashboard(request):
    context = {}
    return render(request, 'marania_invoice_app/dashboard.html', context)
