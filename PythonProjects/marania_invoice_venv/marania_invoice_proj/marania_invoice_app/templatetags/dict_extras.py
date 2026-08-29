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


def indian_grouping(value):
    """Group digits using the Indian numbering system (###,##,##,##...###.##).

    The last three digits are grouped, then groups of two from there on,
    e.g. 100000 -> 1,00,000 and 1234567.89 -> 12,34,567.89.
    """
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value
    neg = "-" if value < 0 else ""
    value = abs(value)
    rounded = round(value, 2)
    integer = int(rounded)
    decimal = int(round((rounded - integer) * 100))
    # Guard against rounding carry (e.g. 1.999 -> integer stays 1, decimal 100).
    if decimal == 100:
        integer += 1
        decimal = 0
    int_str = str(integer)
    if len(int_str) > 3:
        head = int_str[:-3]
        tail = int_str[-3:]
        # Group the head in pairs from the right.
        chars = [head[i:i+2] for i in range(len(head) % 2, len(head), 2)]
        if head[:len(head) % 2]:
            chars.insert(0, head[:len(head) % 2])
        int_str = ",".join(chars) + "," + tail
    return f"{neg}{int_str}.{decimal:02d}"


@register.filter
def inr(value):
    """Format a number as an Indian Rupee amount (e.g. Rs 1,00,000.00)."""
    formatted = indian_grouping(value)
    return f"{formatted}" if isinstance(formatted, str) else value
