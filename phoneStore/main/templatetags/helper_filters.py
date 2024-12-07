from django import template

register = template.Library()


@register.simple_tag
def concat_strings(*args):
    """Concatenate all arguments into a single string."""
    return ''.join(args)
