from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def iconify(value):
    if value =="Placed":
        return 'icon-time'
    elif value == "Cancelled" :
        return 'icon-exclamation-sign'
    elif value == "Won":
        return 'icon-plus'
    elif value == "Lost":
        return 'icon-minus'