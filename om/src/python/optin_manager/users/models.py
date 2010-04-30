from django.db import models
from django.contrib import auth

class UserProfile(models.Model):

    user                = models.ForeignKey(auth.models.User, unique=True, related_name = 'profile')
    is_net_admin        = models.BooleanField("Can Confirm Flow Space Requests", default=False)
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
                        max_priority_level = 1,
                        supervisor_id = 0
                        )

        return profile
