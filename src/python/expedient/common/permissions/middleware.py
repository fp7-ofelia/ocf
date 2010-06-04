'''
Created on Jun 6, 2010

@author: jnaous
'''
from expedient.common.permissions.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from expedient.common.permissions.models import PermissionUser,\
    ExpedientPermission
from django.http import HttpResponseRedirect

import logging
logger = logging.getLogger("PermissionMiddleware")

class PermissionMiddleware(object):
    """
    Middleware to catch PermissionDenied exceptions thrown by the
    L{expedient.common.permissions} app and redirects to the permission URL
    if found.
    """
    
    def process_exception(self, request, exception):
        
        if type(exception) == PermissionDenied and exception.allow_redirect:
            target_type = ContentType.objects.get_for_model(exception.target)
            target = exception.target
            
            logger.debug("Handling permission denied %s" % exception)
            
            # Make sure there's a view for the permission before redirecting
            view = ExpedientPermission.objects.filter(
                name=exception.perm_name).values_list("view", flat=True)
            if not view[0]: return False
            
            if isinstance(exception.user, PermissionUser):
                user = exception.user.user
            else:
                user = exception.user
            user_type = ContentType.objects.get_for_model(user)
            
            url = reverse("permissions_url",
                kwargs={
                    "perm_name": exception.perm_name,
                    "target_ct_id": target_type.id,
                    "target_id": target.id,
                    "user_ct_id": user_type.id,
                    "user_id": user.id,
                },
            )
            
            # add a "next" field for redirection after permission is obtained.
            url += "?next=%s" % request.path
            
            return HttpResponseRedirect(url)
        
        return None
        
