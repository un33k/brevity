from django.conf import settings
from django import template

register = template.Library()


@register.filter
def human_format(num):
    """
    Returns formated string 999, 1.1K, 99.9K, 100K, 101K 999K, 1.1M
    """
    if num < 1000:
        suffix = ''
        formated = num
    if num >= 1000 and num < 1000000:
        suffix = 'k'
        formated = format(float(num) / 1000, '.1f')
    elif num >= 1000000 and num < 1000000000:
        suffix = 'm'
        formated = format(float(num) / 1000000, '.1f')
    return "{} {}".format(formated, suffix)
