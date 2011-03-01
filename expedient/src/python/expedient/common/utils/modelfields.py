'''
Created on Jul 18, 2010

@author: jnaous
'''
import logging
from django.db import models
import formfields
from expedient.common.utils.formfields import validate_datetime

logger = logging.getLogger("common.utils.modelfields")

class MACAddressField(models.CharField):
    """
    A field that validates MAC addresses in XX:XX:XX:XX:XX:XX format.
    """
    empty_strings_allowed = False
    description = "MAC address"
    
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 17
        super(MACAddressField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'form_class': formfields.MACAddressField}
        defaults.update(kwargs)
        return super(MACAddressField, self).formfield(**defaults)

class LimitedIntegerField(models.IntegerField):
    """
    An IntegerField with min and max values.
    """
    def __init__(self, *args, **kwargs):
        self.max_value = kwargs.pop("max_value", None)
        self.min_value = kwargs.pop("min_value", None)
        super(LimitedIntegerField, self).__init__(*args, **kwargs)
        
    def formfield(self, **kwargs):
        defaults = {'form_class': formfields.DecOrHexIntegerField,
                    'max_value': self.max_value,
                    'min_value': self.min_value,
                    }
        defaults.update(kwargs)
        return super(LimitedIntegerField, self).formfield(**defaults)
    
class IPNetworkField(models.CharField):
    """
    A field that accepts either IP address or IP prefixes (192.168.0.0/16).
    """
    empty_strings_allowed = False
    description = "IP address or prefix"
    
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 18
        super(IPNetworkField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'form_class': formfields.IPNetworkField}
        defaults.update(kwargs)
        return super(IPNetworkField, self).formfield(**defaults)
    
class LimitedDateTimeField(models.DateTimeField):
    """A date time field that is limited between a min and max."""
    
    description = "Date and time"
    
    def __init__(self, max_date=None, min_date=None, *args, **kwargs):
        self.max_date = max_date
        self.min_date = min_date
        super(LimitedDateTimeField, self).__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        super(LimitedDateTimeField, self).validate(value, model_instance)
        validate_datetime(value, self.min_date, self.max_date)
    
    def formfield(self, **kwargs):
        defaults = {
            "form_class": formfields.LimitedSplitDateTimeField,
            "max_date": self.max_date,
            "min_date": self.min_date,
        }
        defaults.update(kwargs)
        return super(LimitedDateTimeField, self).formfield(**defaults)

