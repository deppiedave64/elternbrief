from django import template
from django.template.defaulttags import register

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Returns value corresponding to a certain key in a dictionary.
    Useful if standard 'dot-syntax' lookup in templates does not work.
    """
    return dictionary.get(key)
