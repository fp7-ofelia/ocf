from django.db import models
from django.contrib import auth
 
class Priority(object):
     Aggregate_Admin        = 7000
     Campus_Admin           = 6000
     Department_Admin       = 5000
     Building_Admin         = 4000
     Group_Admin            = 3000
     Strict_User            = 2000
     Nice_User              = 1000
     
     Priority_Margin        = 999
     Priority_Scale          = 1000
     
     Admins = ["Aggragate Admin", "Campus Admin", "Department Admin", "Building Admin", "Group Admin"]
 
class UserProfile(models.Model):
    user                    = models.ForeignKey(auth.models.User, unique=True, related_name = 'profile')
    is_net_admin        = models.BooleanField("Can Confirm Flow Space Requests", default=False)
    is_clearinghouse_user   = models.BooleanField("Clearinghouse account", default=False)
    max_priority_level  = models.IntegerField()
    supervisor          = models.ForeignKey(auth.models.User, related_name = 'supervisor')


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
                        supervisor_id = 0,
                        is_clearinghouse_user = False,
                        )

        return profile
