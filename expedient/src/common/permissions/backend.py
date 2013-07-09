'''
Created on May 31, 2010

@author: jnaous
'''
from expedient.common.permissions.models import ExpedientPermission

class ExpedientPermissionsBackend(object):
    """Django backend for object permissions. Needs Django 1.2.

    Use it together with the default ModelBackend like so::

        AUTHENTICATION_BACKENDS = (
            'django.contrib.auth.backends.ModelBackend',
            'expedient.common.permissions.backend.ExpedientPermissionsBackend',
        )
    """
    supports_object_permissions = True
    supports_anonymous_user = False

    def has_perm(self, user_obj, perm, obj=None):
        """
        Checks whether the passed user has passed permission for passed
        object (obj).
        """
        if obj == None:
            return False
    
        missing, _ = ExpedientPermission.objects.get_missing_for_target(
            user_obj, [perm], obj)
        
        return missing == None
    