'''
Created on Apr 29, 2010

@author: jnaous
'''

from django import forms
from sample_resource.models import xmlrpcServerProxy

class xmlrpcServerProxy(forms.ModelForm):
    '''
    A form to create and edit OpenFlow Aggregates.
    '''

    def __init__(self, check_available=False, *args, **kwargs):
        super(xmlrpcServerProxy, self).__init__(*args, **kwargs)
        self.check_available = check_available

    class Meta:
        model = xmlrpcServerProxy

