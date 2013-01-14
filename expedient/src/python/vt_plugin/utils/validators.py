'''
Created on Jan 14, 2013

@author: CarolinaFernandez
'''

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import re

RESOURCE_VM_RE = "^([0-9a-zA-Z\-]){1,64}$"

def validate_discImage(value):
    if value not in ["test", "default"]:
        raise ValidationError("Invalid input: only test image available")

def validate_hdSetupType(value):
    if value != "file-image":
        raise ValidationError("Invalid input: only File Image supported")

def validate_memory(value):
    if value < 128:
        raise ValidationError("Invalid input: memory has to be higher than 128Mb")

def validate_virtualizationSetupType(value):
    if value != "paravirtualization":
        raise ValidationError("Invalid input: only Paravirtualization supported")

resourceVMNameValidator = RegexValidator(re.compile(RESOURCE_VM_RE),
                        u"Please do not use accented characters, symbols, underscores or whitespaces.",
                        "invalid")

