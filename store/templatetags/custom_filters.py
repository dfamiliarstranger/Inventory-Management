from django import template
from num2words import num2words

register = template.Library()

@register.filter(name='format_with_commas')
def format_with_commas(value):
    try:
        value = int(value)
        return "{:,}".format(value)
    except (TypeError, ValueError):
        return value
    

@register.filter
def int_to_words(value):
    return num2words(value)