from django import template

register = template.Library()

@register.filter
def replace_underscores(value):
    """Replaces underscores with spaces."""
    return value.replace('_', ' ')

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
