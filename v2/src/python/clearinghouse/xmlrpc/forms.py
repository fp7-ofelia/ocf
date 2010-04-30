'''
Created on Apr 29, 2010

@author: jnaous
'''

from django import forms
from clearinghouse.xmlrpc.models import PasswordXMLRPCClient

class PasswordXMLRPCClientForm(forms.ModelForm):
    '''
    A form that can be used to create/edit info on a PasswordXMLRPCClient
    '''
    class Meta:
        model = PasswordXMLRPCClient
