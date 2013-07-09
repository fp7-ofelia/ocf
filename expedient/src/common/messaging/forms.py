'''
Created on Apr 27, 2010

@author: jnaous
'''

from django import forms
from models import DatedMessage
from django.contrib.auth.models import User

class MessageForm(forms.ModelForm):
    '''
    Form that can be used to create messages.
    '''
    
    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['msg_text'].widget = forms.Textarea(
            attrs={'cols': 40, 'rows': 4})
        self.fields['users'].widget.attrs.update({'size': 5})
    class Meta:
        model = DatedMessage
        fields = ['type', 'users', 'msg_text', 'sender']
        widgets = {
            'msg_text': forms.Textarea(attrs={'cols': 40, 'rows': 4}),
            'users': forms.SelectMultiple(attrs={'size': 5}),
        }
     
class MessageFormNoIM(MessageForm):
    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['type']= forms.ChoiceField(choices = ((DatedMessage.TYPE_U2U, 'From User',),))
