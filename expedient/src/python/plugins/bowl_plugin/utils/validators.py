#
# BOWL expedient plugin for the Berlin Open Wireless Lab
# based on the sample plugin
#
# Authors: Theresa Enghardt (tenghardt@inet.tu-berlin.de)
#          Robin Kuck (rkuck@net.t-labs.tu-berlin.de)
#          Julius Schulz-Zander (julius@net.t-labs.tu-berlin.de)
#          Tobias Steinicke (tsteinicke@net.t-labs.tu-berlin.de)
#
# Copyright (C) 2013 TU Berlin (FG INET)
# All rights reserved.
#
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

