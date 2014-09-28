"""
Created on Jul 11, 2013

@author: CarolinaFernandez
"""

from django import forms

class RemoveVM(forms.Form):
    """
    Form to remove VM given its Expedient identifier.
    """

    vm_id = forms.CharField(max_length=50, label="VM ID")
