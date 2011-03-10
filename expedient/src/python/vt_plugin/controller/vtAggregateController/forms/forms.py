'''
Created on Apr 29, 2010

@author: jnaous
'''

from django import forms
from vt_plugin.models import VtPlugin
from expedient.common.utils import create_or_update
from django.forms.models import ModelChoiceField
from vt_plugin.models import xmlrpcServerProxy

class VTAggregateForm(forms.ModelForm):
    '''
    A form to create and edit OpenFlow Aggregates.
    '''

    class Meta:
        model = VtPlugin
        exclude = ['client', 'owner', 'users', "leaf_name"]

class xmlrpcServerProxyForm(forms.ModelForm):
    '''
    A form to create and edit OpenFlow Aggregates.
    '''

    class Meta:
        model = xmlrpcServerProxy



DISC_IMAGE_CHOICES = (
            ('default', 'Default'),
            ('other', 'Other'),                      
                      )

class CreateVMForm(forms.Form):

    ale = forms.CharField()
    memory = forms.IntegerField()
    disc_image = forms.ChoiceField(choices= DISC_IMAGE_CHOICES)