'''Increase the username length.
Created on Oct 5, 2010

@author: jnaous
'''

from django.db.models.signals import class_prepared

def longer_username(sender, *args, **kwargs):
    # You can't just do `if sender == django.contrib.auth.models.User`
    # because you would have to import the model
    # You have to test using __name__ and __module__
    if sender.__name__ == "User" and sender.__module__ == "django.contrib.auth.models":
        sender._meta.get_field("username").max_length = 255

class_prepared.connect(longer_username)
