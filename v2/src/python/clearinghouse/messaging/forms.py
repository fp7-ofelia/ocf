'''
Created on Apr 27, 2010

@author: jnaous
'''

from django.forms import ModelForm
from clearinghouse.messaging.models import DatedMessage

class MessageForm(ModelForm):
    '''
    Form that can be used to create messages.
    '''
    class Meta:
        model = DatedMessage
