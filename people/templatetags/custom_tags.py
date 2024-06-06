from django import template

register = template.Library()

@register.filter
def custom_range(start, end):
    return range(start, end)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

