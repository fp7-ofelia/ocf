'''
Created on Jun 6, 2010

@author: jnaous
'''
from expedient.common.permissions.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from expedient.common.permissions.models import PermissionUser
from django.http import HttpResponseRedirect

class PermissionMiddleware(object):
    """
    Middleware to catch PermissionDenied exceptions thrown by the
    L{expedient.common.permissions} app and redirects to the permission URL
    if found.
    """
    
    def process_exception(self, request, exception):
        if type(exception) == PermissionDenied and exception.url_name:
            target_type = ContentType.objects.get_for_model(exception.target)
            target = exception.target
            
            if isinstance(exception.user, PermissionUser):
                user = exception.user.user
            else:
                user = exception.user
            user_type = ContentType.objects.get_for_model(user)

            url = reverse(
                self.url_name,
                kwargs={
                    "perm_name": exception.perm_name,
                    "target_ct_id": target_type.id,
                    "target_id": target.id,
                    "user_ct_id": user_type.id,
                    "user_id": user.id,
                },
            )
            
            return HttpResponseRedirect(url)
        
        return None
        
