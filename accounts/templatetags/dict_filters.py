from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Gets item from dictionary safely."""
    if dictionary and key in dictionary:
        return dictionary.get(key)
    return []

@register.filter
def split(value, delimiter=','):
    """Splits a string into a list."""
    return value.split(delimiter)
