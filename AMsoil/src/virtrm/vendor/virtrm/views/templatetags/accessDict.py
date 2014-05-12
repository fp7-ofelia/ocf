from django import template
register = template.Library()

@register.filter
def dictKeyLookup(the_dict, key):
       return the_dict[key]

