import re
from django import template

register = template.Library()

@register.filter
def extract_number(value):
    match = re.search(r'\d+', str(value))
    return match.group() if match else ''
