'''
Created on Nov 4, 2009

@author: jnaous
'''

from egeni.clearinghouse.models import DatedMessage
from django.contrib.auth.models import User

def get_user_messages(user):
    '''return a queryset of all messages for a particular user'''
    
    return user.messages

def get_and_delete_user_messages(user):
    '''
    return a queryset of all messages for a particular user and delete
    the messages for that user
    '''
    
    msgs = get_user_messages(user)
    msgs.delete()
    
    return msgs

def add_msg_for_user(user, text, type):
    '''
    users is a list of User instances and msg is a string
    '''
    
    user.messages.create(type=type, text=msg)

