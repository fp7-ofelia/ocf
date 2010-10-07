'''
Created on Oct 6, 2010

@author: jnaous
'''
from django import forms

class UploadRSpecForm(forms.Form):
    rspec = forms.FileField(
        help_text="Select the reservation rspec you wish to use.")
    
    