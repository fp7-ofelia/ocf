'''
Created on Jul 17, 2010

@author: jnaous
'''
import logging
from django import forms
from django import core
from django.utils import formats
from expedient.common.utils import validators
import traceback

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
