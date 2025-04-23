import re
from django import template

register = template.Library()

@register.filter
def extract_number(value):
    match = re.search(r'\d+', str(value))
    return match.group() if match else ''

@register.filter
def get_item(dictionary, key):
    """
    Gets an item from a dictionary using the key.
    Usage: {{ dictionary|get_item:key }}
    """
    return dictionary.get(key, None)
