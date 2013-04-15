'''
Created on Jul 17, 2010

@author: jnaous, CarolinaFernandez
'''

from django.core.validators import RegexValidator
from django import forms
import re

ASCII_RE = "^([0-9a-zA-Z\-\_\ ])+$"
# Need to set Unicode string in order to locate accented characters
DESCRIPTION_FORBIDDEN_RE = ur'[\u00C0-\u017F]+' #"/^[\u00C0-\u017F]+$/"
IP_RE = "^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}(/\d?\d)?$"
MAC_RE = "^([\dA-Fa-f]{2}:){5}[\dA-Fa-f]{2}$"
NUMBER_RE = "^([0-9])+$"
RESOURCE_RE = "^([0-9a-zA-Z\-\_])+$"
RESOURCE_VM_RE = "^([0-9a-zA-Z\-]){1,64}$"
TEXT_RE = "^([0-9a-zA-Z\-\_\ \.\!\?\"\'\r\n])+$"

asciiValidator = RegexValidator(re.compile(ASCII_RE),
                                u"Please do not use accented characters and avoid using \'@\'.",
                                "invalid")
#def asciiValidator(s):
#    for c in s:
#        if ord(c)>127 or c == '@':
#            raise ValidationError("Please use only non accented characters and avoid using \'@\'.")

descriptionValidator = RegexValidator(re.compile(TEXT_RE),
                        u"Please do not use accented characters and avoid using \'@\'.",
                        "invalid")

def descriptionLightValidator(description):
    # Raise ValidationError if regexp does match (some accents present)
    if re.search(re.compile(DESCRIPTION_FORBIDDEN_RE, re.UNICODE), description):
        raise forms.ValidationError(u"Please do not use accented characters.", "invalid")

numberValidator = RegexValidator(re.compile(NUMBER_RE),
                        u"Please use numbers only.",
                        "invalid")

resourceNameValidator = RegexValidator(re.compile(RESOURCE_RE),
                        u"Please do not use accented characters, symbols or whitespaces.",
                        "invalid")

resourceVMNameValidator = RegexValidator(re.compile(RESOURCE_VM_RE),
                        u"Please do not use accented characters, symbols, underscores or whitespaces.",
                        "invalid")

validate_ip_prefix = RegexValidator(re.compile(IP_RE),
                        u"Enter a valid IP address (from \"250.20.0.*\" to \"255.24.1.*\").",
                        "invalid")

validate_mac_address = RegexValidator(re.compile(MAC_RE),
                        u"Enter a valid MAC address (in \"xx:xx:xx:xx:xx:xx\" format).",
                        "invalid")

