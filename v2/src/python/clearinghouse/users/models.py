'''
Created on Dec 3, 2009

@author: jnaous
'''

from django.db import models
from django.contrib import auth
from pyanno import parameterTypes, returnType

class UserProfile(models.Model):
    '''
    Additional information about a user.
    '''
    
    ##
    # @ivar user: the user to whom this UserProfile belongs
    user                   = models.ForeignKey(auth.models.User, unique=True)
    
    ##
    # @ivar affiliation: The organization to which the user is affiliated
    affiliation            = models.CharField(max_length=200, default="")

    ##
    # @ivar is_aggregate_admin: Can this user add aggregates?
    is_aggregate_admin     = models.BooleanField("Can add aggregates",
                                             default=False)

    ##
    # @ivar is_researcher: Can this user create slices?
    is_researcher          = models.BooleanField("Can create slices",
                                                 default=False)
    
    ##
    # @ivar is_clearinghouse_admin: Can this user cross ownership boundaries?
    is_clearinghouse_admin = models.BooleanField("Can cross ownership" \
                                                 " boundaries",
                                                 default=False)

    def __unicode__(self):
        return "%s" % self.user
    
    @classmethod
    @parameterTypes(auth.models.User)
    @returnType('UserProfile')
    def get_or_create_profile(cls, user):
        '''
        Gets the user's profile if available or creates one if one doesn't exist
        @param user: the User whose UserProfile to get or create
        @return user_profile: user's profile 
        '''
        
        try:
            profile = user.get_profile()
        except UserProfile.DoesNotExist:
            if user.is_staff or user.is_superuser:
                profile = cls.objects.create(
                                user=user,
                                is_aggregate_admin=True,
                                is_researcher=True,
                                is_clearinghouse_admin=True,
                                )
            else:
                profile = cls.objects.create(
                                user=user,
                                )
        return profile

