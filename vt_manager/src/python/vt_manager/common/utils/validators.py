'''
Created on Jul 17, 2010

@author: jnaous, CarolinaFernandez
'''

from django.core.validators import RegexValidator
import re

ASCII_RE = "^([0-9a-zA-Z\-\_\ ])+$";
DATAPATH_RE = "^([0-9a-fA-F]{2}[:-]){7}([0-9a-fA-F]{2})$";
MAC_RE = "^([\dA-Fa-f]{2}:){5}[\dA-Fa-f]{2}$";
NOTBLANK_RE = "^.+$";
NUMBER_RE = "^([0-9])+$";
RESOURCE_RE = "^([0-9a-zA-Z\-\_])+$";
RESOURCE_VM_RE = "^([0-9a-zA-Z\-]){1,64}$"
TEXT_RE = "^([0-9a-zA-Z\-\_\ \.\!\?\"\'\r\n])+$"

asciiValidator = RegexValidator(re.compile(ASCII_RE),
                                u"Please do not use accented characters and avoid using \'@\'.",
                                "invalid")
#def asciiValidator(s):
#    for c in s:
#        if ord(c)>127 or c == '@':
#            raise ValidationError("Please use only non accented characters and avoid using \'@\'    .")

checkBlank = RegexValidator(re.compile(NOTBLANK_RE),
                        u"Required field",
                        "invalid")

datapathValidator = RegexValidator(re.compile(DATAPATH_RE),
                        u"Please provide a valid datapath ID.",
                        "invalid")

descriptionValidator = RegexValidator(re.compile(TEXT_RE),
                        u"Please do not use accented characters and avoid using \'@\'.",
                        "invalid")
                        
numberValidator = RegexValidator(re.compile(NUMBER_RE),
                        u"Please use numbers only.",
                        "invalid")

resourceNameValidator = RegexValidator(re.compile(RESOURCE_RE),
                        u"Please do not use accented characters, symbols or whitespaces.",
                        "invalid")

resourceVMNameValidator = RegexValidator(re.compile(RESOURCE_VM_RE),
                        u"Please do not use accented characters, symbols, underscores or whitespa    ces.",
                        "invalid")

validate_mac_address = RegexValidator(re.compile(MAC_RE),
                        u"Enter a valid MAC address (in \"xx:xx:xx:xx:xx:xx\" format).",
                        "invalid")

