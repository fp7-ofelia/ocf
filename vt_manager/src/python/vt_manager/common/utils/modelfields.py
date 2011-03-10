'''
Created on Jul 18, 2010

@author: jnaous
'''
from django.db import models
from django import forms
import formfields

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
        defaults = {'form_class': forms.IntegerField,
                    'max_value': self.max_value,
                    'min_value': self.min_value,
                    }
        defaults.update(kwargs)
        return super(LimitedIntegerField, self).formfield(**defaults)
    