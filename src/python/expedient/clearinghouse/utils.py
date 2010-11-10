'''
Created on Nov 9, 2010

@author: jnaous
'''
from expedient.common.messaging.models import DatedMessage
from expedient.common.middleware import threadlocals

def post_message_to_current_user(msg_text, sender=None,
                                 msg_type=DatedMessage.TYPE_ANNOUNCE):
    """Post a message to the user whose request is being processed.
    
    This function depends on the threadlocals middleware to find the current
    user, so it must be installed.
    
    @param msg_text: The message to post for the user.
    @type msg_text: C{str}
    @keyword sender: The message sender. Defaults to None.
    @type sender: C{django.contrib.auth.models.User}
    @keyword msg_type: The type of the message. Defaults to
        L{DatedMessage.TYPE_ANNOUNCE}.
    @type msg_type: C{str} limited to one of L{DatedMessage}.TYPE_*
    
    """
    
    user = threadlocals.get_thread_locals()["user"]
    DatedMessage.objects.post_message_to_user(
        msg_text, user, sender, msg_type)
    
    