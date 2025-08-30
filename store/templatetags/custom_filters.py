from django import template

register = template.Library()

@register.filter
def add_tax(value):
    """Add 8% tax to the value"""
    try:
        return float(value) * 1.08
    except (ValueError, TypeError):
        return value

@register.filter
def add_shipping_and_tax(value):
    """Add shipping ($9.99) and 8% tax to the value"""
    try:
        subtotal = float(value)
        with_shipping = subtotal + 9.99
        return with_shipping * 1.08
    except (ValueError, TypeError):
        return value

@register.filter
def sub(value, arg):
    """Subtract arg from value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def mul(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value
