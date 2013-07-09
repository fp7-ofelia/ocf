import sys
import re

from django import template
from django.template import TemplateSyntaxError
from django.template.defaulttags import URLNode

from expedient.common.utils.ExpedientThemeManager import ExpedientThemeManager

'''
        @author: omoya

        OCF Custom URL templatetag to support different themes with transparency 
'''
#registering
register = template.Library()
# Regex for token keyword arguments
kwarg_re = re.compile(r"(?:(\w+)=)?(.+)")

def url(parser, token):

    bits = token.split_contents()
    if len(bits) < 2: 
        raise TemplateSyntaxError("'%s' takes at least one argument"
                                  " (path to a view)" % bits[0])
    viewname = bits[1]
    args = []
    kwargs = {}
    asvar = None
    bits = bits[2:]
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    # Backwards compatibility: check for the old comma separated format
    # {% url urlname arg1,arg2 %}
    # Initial check - that the first space separated bit has a comma in it
    if bits and ',' in bits[0]:
        check_old_format = True
        # In order to *really* be old format, there must be a comma
        # in *every* space separated bit, except the last.
        for bit in bits[1:-1]:
            if ',' not in bit:
                # No comma in this bit. Either the comma we found
                # in bit 1 was a false positive (e.g., comma in a string),
                # or there is a syntax problem with missing commas
                check_old_format = False
                break
    else:
        # No comma found - must be new format.
        check_old_format = False

    if check_old_format:
        # Confirm that this is old format by trying to parse the first
        # argument. An exception will be raised if the comma is
        # unexpected (i.e. outside of a static string).
        match = kwarg_re.match(bits[0])
        if match:
            value = match.groups()[1]
            try:
                parser.compile_filter(value)
            except TemplateSyntaxError:
                bits = ''.join(bits).split(',')

    # Now all the bits are parsed into new format,
    # process them as template vars

    if len(bits):
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise TemplateSyntaxError("Malformed arguments to url tag")
            name, value = match.groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                args.append(parser.compile_filter(value))
    
    viewname =  ExpedientThemeManager.getThemeStaticUrl(viewname, args)
    return URLNode(viewname, args, kwargs, asvar)

url = register.tag(url)

