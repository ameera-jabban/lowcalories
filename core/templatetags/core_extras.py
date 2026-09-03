from django import template

register = template.Library()


@register.filter
def times(number):
    """يحوّل رقم لـ range عشان نعمل loop عليه بالتمبلت — {% for _ in 5|times %}"""
    return range(int(number))
