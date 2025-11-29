# invoices/templatetags/dict_extras.py
from django import template
import json 

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    if dictionary is None or dictionary == "":
        return {}
    return dictionary.get(key)
