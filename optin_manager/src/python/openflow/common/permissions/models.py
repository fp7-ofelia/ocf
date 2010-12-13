'''
Created on May 28, 2010

@author: jnaous
'''
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.auth.models import User
from expedient.common.utils.managers import GenericObjectManager
from exceptions import PermissionDoesNotExist

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
        if isinstance(user.user, User) and user.user.is_superuser:
            return (None, None)
        
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
            return (None, None)
        
class ExpedientPermission(models.Model):
    """
    This class holds all instances of L{ObjectPermission} that have a particular
    name. L{ObjectPermission} links users to a particular object.
    
    A permission may optionally have a view where the browser should be
    redirected if the permission is missing (for example to request the
    permission). The view is specified by its full path in C{view}.
    
    One limitation of the system right now is that we can only link to objects
    that use a C{PositiveIntegerField} as the object ID.
    
    @cvar objects: a L{ExpedientPermissionManager} instance.
    
    @ivar name: The permission's name
    @type name: C{str}
    @ivar view: The full path to the view for the permission
    @type view: C{str}
    @ivar object_permissions: Per-object permissions with this permission name.
    @type object_permissions: m2m relationship to L{ObjectPermission}.
    """
    
    objects = ExpedientPermissionManager()
    
    name = models.CharField(max_length=100, unique=True)
    view = models.CharField("Permission View", max_length=300,
                            blank=True, null=True)
    
    def __unicode__(self):
        return "%s: %s" % (self.name, self.view)

        
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
    
    def get_permitted_objects(self, klass, perm_names, perm_user):
        """
        Get a queryset of C{klass} instances that the permission user
        C{perm_user} has permissions named by perm_names for.
        """
        if not isinstance(perm_user, PermissionUser):
            perm_user, created = \
                PermissionUser.objects.get_or_create_from_instance(perm_user)
            if created:
                return klass.objects.get_empty_query_set()

        get = lambda(perm_name): \
            set(ObjectPermission.objects.get_objects_queryset(
                klass, dict(permission__name=perm_names[0], users=perm_user),
                {}))
        
        objs = get(perm_names[0])
        for name in perm_names[1:]:
            objs.intersection_update(get(name))
            
        return klass.objects.filter(pk__in=objs)

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
    
    def __unicode__(self):
        return u"%s object permission for %s" % (self.permission.name,
                                                 self.target)
    
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
    
    def __unicode__(self):
        return u"%s" % self.user
    
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
    
    def __unicode__(self):
        return u"%s - %s: Delegatable is %s" % (self.obj_permission,
                                                self.user,
                                                self.can_delegate)
    
    class Meta:
        unique_together=(("obj_permission", "user"),)

class PermissionRequest(models.Model):
    """
    A request from a C{auth.models.User} on behalf of a C{PermissionUser} to
    obtain some permission for a particular target.
    """
    requesting_user = models.ForeignKey(User, related_name="sent_permission_requests")
    permission_owner = models.ForeignKey(User, related_name="received_permission_requests")
    requested_permission = models.ForeignKey(ObjectPermission)
    message = models.TextField(default="", blank=True, null=True)
    
    def allow(self):
        from utils import give_permission_to
        give_permission_to(self.requesting_user,
                           self.requested_permission.permission,
                           self.requested_permission.target,
                           self.permission_owner)
        self.delete()
        
    def deny(self):
        self.delete()
