'''
Created on May 28, 2010

@author: jnaous
'''
from django.db import models
from django.contrib.contenttypes.models import ContentType
from expedient.common.permissions.exceptions import PermissionDoesNotExist
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.auth.models import User

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

class ExpedientPermissionManager(models.Manager):
    """
    Implements methods for checking for missing permissions.
    """

    def get_missing_for_target(self, user, perm_names, target):
        """
        Same as L{get_missing} but accepts a single target instance instead of
        a queryset of targets.
        """
        if not isinstance(target, models.Model):
            # assume class
            target = ContentType.objects.get_for_model(target)
            
        return self.get_missing(user, perm_names,
                                target.__class__.objects.filter(pk=target.pk))
        
    def get_missing(self, user, perm_names, targets):
        """
        This is the method that should be used to check for permissions. All
        other methods that check permissions are wrappers around this method.
        
        Get the first missing permission that the user object does not have for
        all targets. If the ObjectPermission does not exist for the object, it
        will be created and saved before returning it.
        
        One exception is made: if the user is actually a
        C{django.contrib.auth.models.User} instance, then if the user is
        a superuser, get_missing always returns None.
        
        @param user: The permission user for the targets
        @type user: L{PermissionUser} or a model instance.
        @param perm_names: names of permissions to search for
        @type perm_names: iterable of C{str}
        @param targets: objects whose permissions we are searching for
        @type targets: C{QuerySet}
        
        @return: Missing permission and the target for which it is missing or
            None if nothing is missing.
        @rtype: tuple (L{ExpedientPermission}, target) or (None, None)
        """
        
        if not isinstance(user, PermissionUser):
            user, created = \
                PermissionUser.objects.get_or_create_from_instance(user)
        
        # check for superuser
        if isinstance(user.user, User) and user.user.is_superuser: return None
        
        ct = ContentType.objects.get_for_model(targets.model)
        ids = targets.values_list("pk", flat=True)
        
        obj_perms = ObjectPermission.objects.filter(
            object_type=ct,
            object_id__in=ids,
            permission__name__in=perm_names,
            users=user,
        )
        
        if obj_perms.count() < len(perm_names) * len(ids):
            # Check if all perm_names exist.
            qs = self.filter(name__in=perm_names)
            if qs.count() < len(set(perm_names)):
                for name in qs.values_list("name", flat=True):
                    if name not in perm_names:
                        raise PermissionDoesNotExist(name)
            # Find the missing permission
            for perm_name in perm_names:
                perm = qs.get(name=perm_name)
                for id in ids:
                    try:
                        ObjectPermission.objects.get(
                            object_type=ct,
                            object_id=id,
                            permission=perm,
                            users=user,
                        )
                    except ObjectPermission.DoesNotExist:
                        return (perm, targets.get(id=id))
        else:
            return None
        
class ExpedientPermission(models.Model):
    """
    This class holds all instances of L{ObjectPermission} that have a particular
    name. L{ObjectPermission} links users to a particular object.
    
    A permission may optionally have a URL where the browser should be
    redirected if the permission is missing (for example to request the
    permission). The URL is specified by its name in C{url_name}.
    
    One limitation of the system right now is that we can only link to objects
    that use a C{PositiveIntegerField} as the object ID.
    
    @cvar objects: a L{ExpedientPermissionManager} instance.
    
    @ivar name: The permission's name
    @type name: string
    @ivar url_name: The name of the URL whence to obtain permission
    @type url_name: string
    @ivar object_permissions: Per-object permissions with this permission name.
    @type object_permissions: m2m relationship to L{ObjectPermission}.
    """
    
    objects = ExpedientPermissionManager()
    
    name = models.CharField(max_length=100, unique=True)
    url_name = models.URLField("Name of URL whence to obtain permission.",
                               blank=True, null=True)
    
    def __unicode__(self):
        return "%s: %s" % (self.name, self.url)

class GenericObjectManager(models.Manager):
    """
    Adds methods to retrieve generic objects when the model uses the
    contenttypes framework.
    
    @keyword ct_field: name of the ForeignKey field pointing to C{ContentType}.
        Default is "content_type".
    @keyword fk_field: name of the ID field for objects. Default is
        C{object_id}.
    """
    def __init__(self, ct_field="content_type", fk_field="object_id"):
        self.ct_field = ct_field
        self.fk_field = fk_field
        
    def get_or_create_from_instance(self, instance, **kwargs):
        """
        Similar to the C{get_or_create} method, but accepts an instance
        object to be used for the generic foreign key relation.
        """
        kwargs.update({
            self.ct_field: ContentType.objects.get_for_model(instance),
            self.fk_field: instance.id,
        })
        return self.get_or_create(**kwargs)
    
    def filter_from_instance(self, instance):
        """
        Get the generic objects pointing to the instance.
        
        @param instance: instance to retrieve the object for.

        @return: C{QuerySet} containing all generic object.
        """
        return self.filter(**{
            self.ct_field: ContentType.objects.get_for_model(instance),
            self.fk_field: instance.id,
        })
        
    def filter_from_queryset(self, queryset):
        """
        Get a filtered queryset that contains all the objects for all instances
        in queryset. This will only return a query set of the objects found.
        Some may not exist.
        
        @param queryset: QuerySet of objects whose generic counterparts we wish
            to find.
            
        @return: C{QuerySet} that contains the generic objects.
        """
        return self.filter(**{
            self.ct_field: ContentType.objects.get_for_model(queryset.model),
            self.fk_field + "__in": queryset.values_list("pk", flat=True),
        })

class ObjectPermissionManager(GenericObjectManager):
    """
    Adds some useful methods to the default manager type.
    """
    
    def __init__(self):
        super(ObjectPermissionManager, self).__init__("object_type",
                                                      "object_id")
    
    def get_for_object(self, perm_name, obj):
        """
        Get the object permission for this object with this name.
        
        @param perm_name: name of the permission
        @type perm_name: C{str}
        @param obj: object for which to get the permission
        @type obj: a model.
        """
        return self.filter_for_object(obj).get(permission__name=perm_name)

class ObjectPermission(models.Model):
    """
    Links a permission to its object using the C{contenttypes} framework and
    to the set of users holding the permission.
    
    @cvar objects: L{ObjectPermissionManager} for the class.
    
    @ivar permission: The L{ExpedientPermission} of which this
        L{ObjectPermission} is a sort of instance.
    @type permission: L{ExpedientPermission}
    @ivar object_type: The C{ContentType} indicating the class of the target.
    @type object_type: ForeignKey to C{ContentType}
    @ivar object_id: The id of the target.
    @type object_id: positive C{int}
    @ivar target: the object for this target.
    @type target: varies
    @ivar users: many-to-many relationship to users who hold the object
        permission
    @type users: C{ManyToManyField} to L{PermissionUser} through
        L{PermissionInfo}
    """

    objects = ObjectPermissionManager()
    
    permission = models.ForeignKey(ExpedientPermission)
    
    object_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey("object_type", "object_id")
    
    users = models.ManyToManyField("PermissionUser", through="PermissionInfo")
    
    class Meta:
        unique_together = (
            ("permission", "object_type", "object_id"),
        )
    
class PermissionUser(models.Model):
    """
    Links permissions to their users using the C{contenttypes} framework, where
    users are not necessarily C{django.contrib.auth.models.User} instances.
    
    @cvar objects: L{GenericObjectManager} for the class
    
    @ivar user_type: The C{ContentType} indicating the class of the user.
    @type user_type: ForeignKey to C{ContentType}
    @ivar user_id: The id of the user.
    @type user_id: positive C{int}
    @ivar user: the object for this user.
    @type user: varies
    """
    
    objects = GenericObjectManager("user_type", "user_id")
    
    user_type = models.ForeignKey(ContentType)
    user_id = models.PositiveIntegerField()
    user = GenericForeignKey("user_type", "user_id")
    
    class Meta:
        unique_together=(("user_type", "user_id"),)

class PermissionInfo(models.Model):
    """
    Information on what the user model can do with the permission.
    
    @ivar obj_permission: the object permission for this info.
    @type obj_permission: ForeignKey to L{ObjectPermission}
    @ivar user: the user for this info.
    @type user: ForeignKey to L{PermissionUser}
    @ivar can_delegate: Can the user give this permission to someone else?
    @type can_delegate: C{bool}
    """
    obj_permission = models.ForeignKey(ObjectPermission)
    user = models.ForeignKey(PermissionUser)
    can_delegate = models.BooleanField()
