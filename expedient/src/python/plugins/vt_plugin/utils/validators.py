'''
Created on Jan 14, 2013

@author: CarolinaFernandez
@author: lbergesio 
'''

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import re

RESOURCE_VM_RE = "^([0-9a-zA-Z\-]){1,64}$"

def validate_discImage(value):
    from vt_plugin.models.VM import DISC_IMAGE_CHOICES
    if value not in [x[0] for x in DISC_IMAGE_CHOICES]:
        raise ValidationError("Invalid input: only test image available")

def validate_hdSetupType(value):
    from vt_plugin.models.VM import HD_SETUP_TYPE_CHOICES 
    if value not in [x[0] for x in HD_SETUP_TYPE_CHOICES]:
        raise ValidationError("Invalid input: only File Image supported")

def validate_memory(value):
    if value < 128:
        raise ValidationError("Invalid input: memory has to be higher than 128Mb")

def validate_virtualizationSetupType(value):
    from vt_plugin.models.VM import VIRTUALIZATION_SETUP_TYPE_CHOICES 
    if value not in [x[0] for x in VIRTUALIZATION_SETUP_TYPE_CHOICES]:
        raise ValidationError("Invalid input: only Paravirtualization supported")

resourceVMNameValidator = RegexValidator(re.compile(RESOURCE_VM_RE),
                        u"Please do not use accented characters, symbols, underscores or whitespaces.",
                        "invalid")

