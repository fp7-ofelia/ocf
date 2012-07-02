'''
Created on Jun 18, 2010

@author: jnaous
'''
from django import forms
from models import Slice
from django.conf import settings

class SliceCrudForm(forms.ModelForm):
    class Meta:
        model = Slice
        exclude = ["project", "aggregates", "owner", "reserved", "expiration_date"]
