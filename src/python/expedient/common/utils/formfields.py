'''
Created on Jul 17, 2010

@author: jnaous
'''
from django import forms
from expedient.common.utils import validators

class MACAddressField(forms.CharField):
    """
    A MAC Address form field.
    """
    
    default_error_messages = {
        'invalid': u'Enter a valid MAC address in "xx:xx:xx:xx:xx:xx" format.',
    }
    default_validators = [validators.validate_mac_address]
