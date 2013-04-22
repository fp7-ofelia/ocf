"""
Functionality related to mail delivery.

@date: Apr 18, 2013
@author: CarolinaFernandez
"""

from django.core.mail import send_mail as django__send_mail
from ServiceThread import ServiceThread

def send_mail(subject, message, from_email, recipient_list):
    """
    Wrapper for the send_mail method within django.core.mail
    which uses a thread to decouple its execution from the
    main program. This is specially useful if mail server
    configuration is erroneus, server is very busy, etc; so
    normal flow will not be affected.
    """
    ServiceThread.start_method_new_thread(
                                          django__send_mail,
                                          None, 
                                          None, 
                                          subject, 
                                          message, 
                                          from_email, 
                                          recipient_list,
                                         )

