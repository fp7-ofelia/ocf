'''
Created on Jul 19, 2010

@author: expedient
'''
from django.contrib.auth.models import User
from openflow.optin_manager.users.models import Priority ,UserProfile
from openflow.optin_manager.opts.models import AdminFlowSpace

def super_user_save(sender, **kwargs):
    instance = kwargs["instance"]
    if (sender==User):
        if (instance.is_superuser):
            p = UserProfile.get_or_create_profile(instance)
            p.is_net_admin = True
            p.max_priority_level = 7000
            p.supervisor = instance
            p.save()
            admfs = AdminFlowSpace.objects.filter(user=instance).all()
            if (len(admfs)==0):
                AdminFlowSpace.objects.create(user=instance)   
                