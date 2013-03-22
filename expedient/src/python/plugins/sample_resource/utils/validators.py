'''
Created on Jan 14, 2013

@author: CarolinaFernandez
'''

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import re
#from sample_resource.models.SampleResource import TEMPERATURE_SCALE_CHOICES

RESOURCE_SR_RE = "^([0-9a-zA-Z\-]){1,64}$"

#def validate_discImage(value):
#    if value not in ["test", "default"]:
#        raise ValidationError("Invalid input: only test image available")

#def validate_hdSetupType(value):
#    if value != "file-image":
#        raise ValidationError("Invalid input: only File Image supported")

#def validate_memory(value):
#    if value < 128:
#        raise ValidationError("Invalid input: memory has to be higher than 128Mb")


def validate_temperature_scale(scale, scales):
#    if scale not in ["celsius", "fahrenheit", "kelvin"]:
    if scale not in scales:
        raise ValidationError("Invalid scale: please choose one from the list")

#validate_temperature_scale = RegexValidator(re.compile("^(celsius|fahrenheit|kelvin)$"),
#                        u"Please choose one of the available scales.",
#                        "invalid")




#def validate_virtualizationSetupType(value):
#    if value != "paravirtualization":
#        raise ValidationError("Invalid input: only Paravirtualization supported")

validate_resource_name = RegexValidator(re.compile(RESOURCE_SR_RE),
                        u"Please do not use accented characters, symbols, underscores or whitespaces.",
                        "invalid")

