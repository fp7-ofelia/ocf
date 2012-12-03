'''
Created on Jul 17, 2010

@author: jnaous, CarolinaFernandez
'''

import re
from django.core.validators import RegexValidator
from django.forms import ValidationError

ASCII_RE = "^([0-9a-zA-Z\-\_\ ])+$";
DATAPATH_RE = "^([0-9a-fA-F]{2}[:-]){7}([0-9a-fA-F]{2})$";
MAC_RE = "^([\dA-Fa-f]{2}:){5}[\dA-Fa-f]{2}$";
NOTBLANK_RE = "^.+$";
NUMBER_RE = "^([0-9])+$";
RESOURCE_RE = "^([0-9a-zA-Z\-\_])+$";
TEXT_RE = "^([0-9a-zA-Z\-\_\ \.])+$";

mac_re = re.compile(r'^([\dA-Fa-f]{2}:){5}[\dA-Fa-f]{2}$')
validate_mac_address = RegexValidator(mac_re, u'Enter a valid MAC address (in "xx:xx:xx:xx:xx:xx" format).', 'invalid')

def asciiValidator(s):
    pattern = re.compile(ASCII_RE)
    if (pattern.match(s) == None):
        raise ValidationError("Please do not use accented characters and avoid using \'@\'.")

def checkBlank(value):
    if value=='': 
        raise ValidationError("Field required")

def datapathValidator(s):
    pattern = re.compile(DATAPATH_RE)
    if (pattern.match(s) == None):
        raise ValidationError("Please provide a valid datapath ID.")

def macValidator(s):
    pattern = re.compile(MAC_RE)
    if (pattern.match(s) == None):
        raise ValidationError("Please provide a valid MAC address.")

def numberValidator(s):
    pattern = re.compile(NUMBER_RE)
    if (pattern.match(str(s)) == None):
        raise ValidationError("Please use numbers only.")

def resourceNameValidator(s):
    pattern = re.compile(RESOURCE_RE)
    if (pattern.match(s) == None):
        raise ValidationError("Please do not use accented characters, symbols or whitespaces.")
