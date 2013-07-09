from django.db import models
from django.contrib.auth.models import User
from django.db.models import signals
from expedient.common.utils.mail import send_mail # Wrapper for django.core.mail__send_mail
from django.conf import settings

class DatedMessageManager(models.Manager):
    '''
    Add some convenience functions for working with messages.
    '''
    
    def post_message_to_users(self, msg_text, sender=None,
                               msg_type='announcement', **kwargs):
        '''
        send a message to users matching the filter arguments in kwargs.
        
        @param msg_text: the text of the message
        @type msg_text: string
        @param sender: the user sending the message. Default None.
        @type sender: L{django.contrib.auth.models.User}
        @param msg_type: the message type. One of DatedMessage.TYPE_*
            Defaults to DatedMessage.TYPE_ANNOUNCE
        @type msg_type: One of DatedMessage.TYPE_*
        @param kwargs: filter arguments (e.g. username='dumbuser')
        '''
        max_length = DatedMessage._meta.get_field("msg_text").max_length
        m = self.create(
            msg_text=msg_text[:max_length], type=msg_type, sender=sender,
        )
        for user in User.objects.filter(**kwargs):
            m.users.add(user)
        
    def post_message_to_user(self, msg_text, user,
                             sender=None, msg_type='announcement'):
        '''
        send a message to a user
        
        @param msg_text: the text of the message
        @type msg_text: string
        @param user: the receiver of the message or her username
        @type user: L{django.contrib.auth.models.User} or string
        @param sender: the user sending the message. Default None.
        @type sender: L{django.contrib.auth.models.User}
        @param msg_type: the message type. One of DatedMessage.TYPE_*
            Defaults to DatedMessage.TYPE_ANNOUNCE
        @type msg_type: One of DatedMessage.TYPE_*
        '''

        max_length = DatedMessage._meta.get_field("msg_text").max_length
        
        if type(user) == User:
            rcvr = user
        else:
            rcvr = User.objects.get(username=user)
            
        m = self.create(msg_text=msg_text[:max_length], type=msg_type, sender=sender)
        m.users.add(rcvr)
        
    def delete_messages_for_user(self, msgs, user):
        '''
        Delete messages for a user.
        
        @param msgs: iterable of msgs to delete for user
        @type msgs: iterable
        @param user: user object whose messages to delete
        '''
        
        user.messages.remove(*list(msgs))
        
    def get_messages_for_user(self, user):
        '''
        Get messages for a particular user.
        
        @param user: user object whose messages to get
        '''
        
        return self.filter(users=user)

class DatedMessage(models.Model):
    
    objects = DatedMessageManager()
    
    TYPE_ERROR = 'error'
    TYPE_SUCCESS = 'success'
    TYPE_WARNING = 'warning'
    TYPE_ANNOUNCE = 'announcement'
    TYPE_INFO = 'info'
    TYPE_U2U = 'user2user'
   
    MSG_TYPE_NOCHOICE={TYPE_U2U: 'From User',}
 
    MSG_TYPE_CHOICES={TYPE_ERROR: 'Error',
                      TYPE_SUCCESS: 'Success',
                      TYPE_WARNING: 'Warning',
                      TYPE_ANNOUNCE: 'Announcement',
                      TYPE_INFO: 'Informational',
                      TYPE_U2U: 'From User',
                     }
    type = models.CharField("Message type", max_length=20,
                            choices=MSG_TYPE_CHOICES.items())
    datetime = models.DateTimeField(auto_now=True, auto_now_add=True,
                                    editable=False)
    users = models.ManyToManyField(User, related_name="messages",
                                   verbose_name="Recipients")
    msg_text = models.CharField("Message", max_length=300)
    sender = models.ForeignKey(User, related_name="sent_messages",
                               null=True, blank=True)
    
    def format_date(self):
        return self.datetime.strftime("%Y-%m-%d")

    def format_time(self):
        return self.datetime.strftime("%H:%M:%S")
    
    def get_type(self):
        return DatedMessage[self.type]
    
    def __unicode__(self):
        return "%s %s - %s" % (self.format_date(), self.format_time(), self.msg_text)

def clean_messages(sender, **kwargs):
    '''
    If there are no more users for this message, delete it from
    the database.
    '''
    if kwargs['created'] == False:
        if kwargs['instance'].users.count() == 0:
            kwargs['instance'].delete()

signals.post_save.connect(clean_messages, DatedMessage)
