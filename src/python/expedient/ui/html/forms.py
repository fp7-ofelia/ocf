'''
Created on Jun 20, 2010

@author: jnaous
'''
from django import forms
from openflow.plugin.models import FlowSpaceRule

class FlowSpaceForm(forms.ModelForm):
    """
    Form to edit flowspace.
    """
    class Meta:
        model = FlowSpaceRule

    def __init__(self, sliver_qs, *args, **kwargs):
        super(FlowSpaceForm, self).__init__(*args, **kwargs)
        self.fields["slivers"].queryset = sliver_qs
