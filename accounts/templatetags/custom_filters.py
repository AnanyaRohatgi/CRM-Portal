from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return []
    return dictionary.get(key, [])

@register.filter
def get_attr(obj, attr):  # <- renamed from getattr
    return getattr(obj, attr, None)
