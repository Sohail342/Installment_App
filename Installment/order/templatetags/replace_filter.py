from django import template

register = template.Library()

@register.filter
def remove_underscore(value):
    return value.replace('_', ' ')
