'''
Created on May 28, 2010

@author: jnaous
'''
from django.db import models
from django.contrib.contenttypes.models import ContentType
from expedient.common.permissions.exceptions import PermissionDoesNotExist
from django.db.models import Manager

## At the model level:
# require permissions for object methods
# redirect to pages to request permissions
# have some sensible default permissions
## At the project level:
# create roles that contain bunches of permissions
# have permissions that are delegatable and not delegatable
## Permission checks:
# either explicitly given permissions or permissions by rules
# Rule permissions:
#   - teammates may send messages to each other:

class ExpedientPermissionManager(Manager):
    """
    Adds some useful methods to the default manager type.
    """
    
    def get_perms(self, perm_names, target=None):
        """
        Returns a queryset of permissions with names in C{perm_names}. If
        C{target} is specified then filter by target as well as names.
        permission is missing, raises a L{PermissionDoesNotExist} exception.
        
        @param perm_names: list of permission names
        @type perm_names: L{list} of L{str}
        @keyword target: target for these permissions. Default None.
        @type target: L{ControlledModel}
        
        @return: QuerySet of permissions
        @rtype: QuerySet of L{ExpedientPermission}s
        """
        perms_req = ExpedientPermission.objects.filter(
            name__in=list(set(perm_names)))
        
        if target:
            perms_req = perms_req.filter(targets=target)

        # check if some permission name does not exist
        if perms_req.count() < len(perm_names):
            perms_req_names = set(perms_req.values_list("name", flat=True))
            perm_names = set(perm_names)
            missing = perm_names - perms_req_names
            raise PermissionDoesNotExist(missing.pop(), target=target)
        
        return perms_req

class ExpedientPermission(models.Model):
    """
    Users can own sets of permissions that are related to particular objects.
    """
    
    objects = ExpedientPermissionManager()
    
    name = models.CharField(max_length=200, unique=True)
    url_name = models.URLField("Name of URL whence to obtain permission.",
                               blank=True, null=True)
    
    def __unicode__(self):
        return "%s: %s" % (self.name, self.url)
    
class PermissionInfo(models.Model):
    """
    Information on what the user model can do with the permission.
    """
    permission = models.ForeignKey(ExpedientPermission)
    perm_user = models.ForeignKey("PermissionUserModel")
    can_delegate = models.BooleanField()
    
class ControlledModel(models.Model):
    """
    Models that want to require permissions on their methods must inherit
    from ControlledModel.
    """
    permissions = models.ManyToManyField(
        ExpedientPermission, related_name="targets")
    
class PermissionUserModel(models.Model):
    """
    Models that will need to have permissions must inherit from UserModel.
    """
    permissions = models.ManyToManyField(
        ExpedientPermission, related_name="users", through=PermissionInfo)
    
    def check_permissions(self, perms_req):
        """
        Check that the the L{PermissionUserModel} has the permissions given in
        C{perms_req}. Returns the first missing permission or None if all were
        found.

        @param perms_req: C{QuerySet} of required permissions
        @type perms_req: C{QuerySet} of L{ExpedientPermission}s

        @return: first missing permission or None if all are found
        @rtype: L{ExpedientPermission} or None
        """
        
        # find the permissions
        perms_found = self.permissions.filter(pk__in=perms_req)
        
        # find the first missing permission and raise an exception
        if perms_found.count() < perms_req.count():
            for req in perms_req:
                if req not in perms_found:
                    return req
        
        else:
            return None
    
    def check_permission_names(self, target, perm_names):
        """
        Check that the the L{PermissionUserModel} has the permissions whose
        target is target and whose names are given in C{perm_names}. Returns the
        first missing permission or None if all were found.
        
        @param target: permissions' target
        @type target: L{ControlledModel}
        @param perm_names: permission names
        @type perm_names: L{list}
        
        @return: first missing permission or None if all are found
        @rtype: L{ExpedientPermission} or None
        """
        
        perms_req = ExpedientPermission.objects.get_perms(perm_names,
                                                          target=target)
        return self.check_permissions(perms_req)

class ControlledContentType(ControlledModel):
    """
    Links permissions to ContentTypes to create class-level permissions.
    """
    content_type = models.OneToOneField(ContentType)
