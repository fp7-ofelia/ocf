'''
Created on Jul 17, 2010

@author: jnaous
'''
import re
from django.core.validators import RegexValidator
from django.forms import ValidationError

ASCII_RE = "^([0-9a-zA-Z\-\_\ ])+$"
NUMBER_RE = "^([0-9])+$"
RESOURCE_RE = "^([0-9a-zA-iZ\-\_])+$"
TEXT_RE = "^([0-9a-zA-Z\-\_\ \.])+$"

mac_re = re.compile(r'^([\dA-Fa-f]{2}:){5}[\dA-Fa-f]{2}$')
validate_mac_address = RegexValidator(mac_re, u'Enter a valid MAC address (in "xx:xx:xx:xx:xx:xx" format).', 'invalid')

ip_re = ipv4_re = re.compile(r'^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}(/\d?\d)?$')
validate_ip_prefix = RegexValidator(ip_re, u'Enter a valid MAC address (in "xx:xx:xx:xx:xx:xx" format).', 'invalid')

def asciiValidator(s):
    pattern = re.compile(ASCII_RE)
    if (pattern.match(s) == None):
        raise ValidationError("Please do not use accented characters and avoid using \'@\'.")

#def asciiValidator(s):
#    for c in s:
#        if ord(c)>127 or c == '@':
#            raise ValidationError("Please use only non accented characters and avoid using \'@\'.")

def descriptionValidator(s):
    pattern = re.compile(TEXT_RE)
    if (pattern.match(s) == None):
        raise ValidationError("Please do not use accented characters and avoid using \'@\'.")

def numberValidator(s):
    pattern = re.compile(NUMBER_RE)
    if (pattern.match(s) == None):
        raise ValidationError("Please use numbers only.")

def resourceNameValidator(s):
    pattern = re.compile(RESOURCE_RE)
    if (pattern.match(s) == None):
        raise ValidationError("Please do not use accented characters, symbols or whitespaces.")

