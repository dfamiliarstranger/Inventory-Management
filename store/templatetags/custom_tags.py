from django import template
from django.urls import resolve

register = template.Library()

@register.simple_tag(takes_context=True)
def active_class(context, url_name):
    try:
        current_url_name = resolve(context['request'].path_info).url_name
        if current_url_name == url_name:
            return 'active'
    except:
        pass
    return ''
