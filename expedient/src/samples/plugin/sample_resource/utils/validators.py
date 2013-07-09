'''
Created on Jan 14, 2013

@author: CarolinaFernandez
'''

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import re

RESOURCE_SR_RE = "^([0-9a-zA-Z\-]){1,64}$"
TEMPERATURE_SCALE_CHOICES = (
                        ('C','Celsius'),
                        ('F','Fahrenheit'),
                        ('K','Kelvin'),
                      )

def validate_temperature_scale(scale):
    """
    Validates the chosen temperature scale against the set 'indices'.
    """
    if scale not in [ t[0] for t in TEMPERATURE_SCALE_CHOICES ]:
        raise ValidationError("Invalid scale: please choose one from the list")

validate_resource_name = RegexValidator(re.compile(RESOURCE_SR_RE),
                        u"Please do not use accented characters, symbols, underscores or whitespaces.",
                        "invalid")

