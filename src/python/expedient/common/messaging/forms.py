'''
Created on Apr 27, 2010

@author: jnaous
'''

from django import forms
from models import DatedMessage

class MessageForm(forms.ModelForm):
    '''
    Form that can be used to create messages.
    '''
    
    # TODO: Fix this when switching to Django 1.2
    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['msg_text'].widget = forms.Textarea(
            attrs={'cols': 40, 'rows': 4})
        self.fields['users'].widget.attrs.update({'size': 5})
    class Meta:
        model = DatedMessage
        fields = ['type', 'users', 'msg_text']
#        widgets = {
#            'msg_text': forms.Textarea(attrs={'cols': 80, 'rows': 10})
#        }
