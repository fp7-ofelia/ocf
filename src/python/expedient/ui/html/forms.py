'''
Created on Jun 20, 2010

@author: jnaous
'''
from django import forms
from expedient.ui.html.models import SliceFlowSpace

class FlowSpaceForm(forms.ModelForm):
    """
    Form to edit flowspace.
    """
    class Meta:
        model = SliceFlowSpace
        exclude = ["slice"]
