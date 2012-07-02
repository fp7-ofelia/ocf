'''
Created on Jul 17, 2010

@author: jnaous
'''
import logging
from django import forms
from django import core
from expedient.common.utils import validators
from django.core.exceptions import ValidationError

logger = logging.getLogger("common.utils.formfields")

class DecOrHexIntegerField(forms.IntegerField):
    def to_python(self, value):
        """
        Validates that int() can be called on the input. Returns the result
        of int(). Returns None for empty values.
        """
        
        try:
            value = super(DecOrHexIntegerField, self).to_python(value)
        except core.exceptions.ValidationError:
            try:
                value = int(str(value), 0)
            except (ValueError, TypeError):
                raise core.exceptions.ValidationError(
                    self.error_messages['invalid'])
        
        return value

class MACAddressField(forms.CharField):
    """
    A MAC Address form field.
    """
    
    default_error_messages = {
        'invalid': u'Enter a valid MAC address in "xx:xx:xx:xx:xx:xx" format.',
    }
    default_validators = [validators.validate_mac_address]

class IPNetworkField(forms.CharField):
    """
    An IP address or prefix field.
    """
    
    default_error_messages = {
        'invalid': u'Enter a valid IP address in "w.x.y.z[/l]" format.',
    }
    default_validators = [validators.validate_ip_prefix]

class LimitedSplitDateTimeField(forms.SplitDateTimeField):
    """Adds limits to the default SplitDateTimeField"""
    
    def validate(self, value):
        validate_datetime(value, self.min_date, self.max_date)
    
    def __init__(self, max_date=None, min_date=None, *args, **kwargs):
        self.max_date = max_date
        self.min_date = min_date
        super(LimitedSplitDateTimeField, self).__init__(*args, **kwargs)
        
def validate_datetime(value, min_date, max_date):
    max_date = max_date() if callable(max_date) else max_date
    min_date = min_date() if callable(min_date) else min_date
    
    if max_date and value > max_date:
        raise ValidationError(
            "The entered date is too late. "
            "Maximum is %s" % max_date)

    if min_date and value < min_date:
        raise ValidationError(
            "The entered date is too early. "
            "Minumum is %s" % min_date)

    
    