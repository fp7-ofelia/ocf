'''
Created on Dec 3, 2009

@author: jnaous
'''

from django.db import models
from django.contrib import auth

class UserProfile(models.Model):
    '''
    Additional information about a user.
    
    @param user: the user to whom this UserProfile belongs
    @type user: L{auth.models.User}
    @param affiliation: The organization to which the user is affiliated
    @type affiliation: L{str}
    @param is_clearinghouse_admin: Can this user cross ownership boundaries?
    @type is_clearinghouse_admin: L{bool}
    '''

    user                   = models.ForeignKey(auth.models.User, unique=True)
    affiliation            = models.CharField(max_length=200, default="")
    is_clearinghouse_admin = models.BooleanField("Can cross ownership" \
                                                 " boundaries",
                                                 default=False)

    def __unicode__(self):
        try:
            return "Profile for %s" % self.user
        except:
            return "No user"
    
    @classmethod
    def get_or_create_profile(cls, user):
        '''
        Gets the user's profile if available or creates one if one doesn't exist
        
        @param user: the User whose UserProfile to get or create
        @type user: L{auth.models.User}
        
        @return user_profile: user's profile
        @rtype user_profile: L{UserProfile} 
        '''
        
        try:
            profile = user.get_profile()
        except UserProfile.DoesNotExist:
            if user.is_staff or user.is_superuser:
                profile = cls.objects.create(
                                user=user,
                                is_clearinghouse_admin=True,
                                )
            else:
                profile = cls.objects.create(
                                user=user,
                                )
        return profile
