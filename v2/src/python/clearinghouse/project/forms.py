'''
Created on Feb 20, 2010

@author: jnaous
'''

from django import forms

class SliceNameForm(forms.ModelForm):
    '''
    A form for creating a slice using just a name
    '''
    
    class Meta:
        model = Slice
        exclude = ('user')
