'''
Created on Aug 9, 2010

@author: jnaous
'''
from django.contrib.auth.models import User
from expedient.common.permissions.models import Permittee
from expedient.clearinghouse.roles.models import ProjectRole

def get_users_for_role(role, can_delegate=False):
    """Get all the users that have the role.
    
    This function does a lookup by the permissions the users have rather
    by whether or not they were given the role explicitly. It is much slower.
    
    @param role: role whose users we are looking for.
    @type role: instance of L{ProjectRole}
    @keyword can_delegate: Should we look only for users who can delegate
        the role? Default is C{False}.
    @type can_delegate: C{bool}
    @return: users that can own the role
    @rtype: C{QuerySet} of C{django.contrib.auth.models.User}
    """
    # get all the permissions in the role
    obj_perm_ids = role.obj_permissions.values_list("pk", flat=True)
    
    # Filter for all the ids
    qs = Permittee.objects.all()
    for id in obj_perm_ids:
        if can_delegate:
            qs = qs.filter(
                permissionownership__obj_permission__pk=id,
                permissionownership__can_delegate=True).distinct()
        else:
            qs = qs.filter(
                permissionownership__obj_permission__pk=id).distinct()
        
    user_ids = qs.values_list("object_id", flat=True)
    return User.objects.filter(pk__in=user_ids)
