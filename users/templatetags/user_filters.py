from django import template

register = template.Library()


@register.filter(name='get_item')
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    return dictionary.get(key)


@register.filter(name='attr')
def attr(obj, attr_name):
    """Get attribute from object"""
    return getattr(obj, attr_name, None)
