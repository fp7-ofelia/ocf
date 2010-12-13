from django.db import models
from django.contrib import auth
from django.db.models.signals import post_save

class Priority(object):
    Aggregate_Admin        = 12000
    Campus_Admin           = 10000
    Department_Admin       = 8000
    Building_Admin         = 6000
    Group_Admin            = 4000
    Strict_User            = 2000
    Nice_User              = 1000
    
    Priority_Margin         = 2000
    Strict_Priority_Offset  = 1000
    Priority_Scale          = 1000
    
    Admins = ["Aggragate Admin", "Campus Admin", "Department Admin",
              "Building Admin", "Group Admin"]
 
class UserProfile(models.Model):
    user                   = models.ForeignKey(auth.models.User, unique=True, related_name = 'profile')
    is_net_admin           = models.BooleanField("Can Confirm Flow Space Requests", default=False)
    is_clearinghouse_user  = models.BooleanField("Clearinghouse account", default=False)
    max_priority_level     = models.IntegerField()
    supervisor             = models.ForeignKey(auth.models.User, related_name = 'supervisor')
    admin_position         = models.CharField(max_length = 1024, default="")

    def __unicode__(self):
        try:
            return "Profile for %s" % self.user
        except:
            return "No user"

    @classmethod
    def get_or_create_profile(cls, user):

        try:
            profile = user.get_profile()
        except UserProfile.DoesNotExist:
            profile = cls.objects.create(
                        user=user,
                        is_net_admin = False,
                        max_priority_level = Priority.Strict_User,
                        supervisor = user,
                        is_clearinghouse_user = False,
                        )

        return profile

from openflow.optin_manager.users.user_signal_handler import super_user_save       
post_save.connect(super_user_save, sender=auth.models.User)
