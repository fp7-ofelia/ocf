'''
Created on Jul 30, 2010

@author: jnaous
'''
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db.models import Q
from expedient.common.permissions.exceptions import \
    PermissionRegistrationConflict, PermissionDoesNotExist,\
    UnexpectedParameterType
from expedient.common.utils.managers import GenericObjectManager
import logging

logger = logging.getLogger("permissions.managers")

class ExpedientPermissionManager(models.Manager):
    """
    Implements methods for checking for missing permissions.
    """
    
    _enabled = True
    
    def enable_checks(self):
        """Enable permission checks."""
        self._enabled = True
        
    def disable_checks(self):
        """Disable permission checks."""
        self._enabled = False
    
    def are_checks_enabled(self):
        """Are permission checks enabled?
        
        @return: True if yes, False otherwise.
        """
        
        return self._enabled
    
    def _stringify_func(self, f):
        if callable(f):
            return "%s.%s" % (f.__module__, f.__name__)
        else:
            return f
    
    def create_permission(self, name, description="", view=None, force=False):
        """
        Create a new L{ExpedientPermission}. If permission is already
        registered with a different view, a L{PermissionRegistrationConflict}
        exception is thrown. This operation is idempotent. If the permission
        already exists, nothing happens.
        
        @param name: The name of the permission. Must be globally unique.
        @type name: L{str}
        @keyword view: View to redirect to if a permission is missing. Default
            None. The view function should have the signature::
                
                view(request, permission, permittee, target_obj_or_class, redirect_to=None)
            
            where C{permission} is an L{ExpedientPermission} instance,
            C{permittee} is the object exercising the permission (not
            necessarily a C{django.contrib.auth.models.User} instance), and
            C{target_obj_or_class} is the object instance or class
            that the permittee does not have the permission C{permission} for.
            C{redirect_to} is a field used to indicate the original URL that caused
            the L{PermissionDenied} exception. The view should redirect there
            when done.
            
        @type view: Full import path of the view as C{str} or the view function
            object itself. Note that the view must be importable by its a path
            (i.e. cannot use nested functions).
        @keyword force: Force changing the view even if the view was registered
            with a different function before.
        @return: the new L{ExpedientPermission}.
        """
        view = self._stringify_func(view)
        # check if the permission is registered with a different view
        # somewhere else
        perm, created = self.get_or_create(
            name=name, defaults=dict(view=view, description=description))
        
        if not created and perm.description != description:
            perm.description = description
            perm.save()
            
        if not created and perm.view != view:
            if force:
                perm.view = view
                logger.warning(
                    "Permission %s was forceably re-registered with view "
                    "%s instead of %s" % (name, view, perm.view))
                perm.save()
            else:
                raise PermissionRegistrationConflict(name, view, perm.view)
        return perm

    def get_missing_for_target(self, permittee, perm_names, target):
        """
        Same as L{get_missing} but accepts a single target instance instead of
        a queryset of targets, and only returns the missing
        L{ExpedientPermission}. If C{permittee} is a
        C{django.contrib.auth.models.User} instance and is a superuser, always
        return None. Also if the target is the same as the permittee, always
        return None.
        
        @param permittee: The object exercising the permission on the target
        @type permittee: L{Permittee} or a model instance.
        @param perm_names: names of permissions to search for
        @type perm_names: iterable of C{str}
        @param target: object whose permissions we are searching for
        @type target: C{Model}
        
        @return: Missing permission.
        @rtype: L{ExpedientPermission} or None
        """
        if not isinstance(target, models.Model):
            # assume class
            target = ContentType.objects.get_for_model(target)
        
        return self.get_missing(
            permittee, perm_names,
            target.__class__.objects.filter(pk=target.pk)
        )[0]
        
    def get_missing(self, permittee, perm_names, targets):
        """
        This is the method that should be used to check for permissions. All
        other methods that check permissions are wrappers around this method.
        
        Get the first missing permission that the permittee object does not
        have for all targets. If the ObjectPermission does not exist
        for the object, it will be created and saved before returning it.
        
        Two exceptions are made: if the permittee is actually a
        C{django.contrib.auth.models.User} instance, then if the user is
        a superuser, C{get_missing} always returns (None, None).  And if the
        C{target} is the same as the C{permittee}, always return (None, None).
        
        @param permittee: The object exercising the permission on the targets
        @type permittee: L{Permittee} or other model instance.
        @param perm_names: names of permissions to search for
        @type perm_names: iterable of C{str}
        @param targets: objects whose permissions we are searching for
        @type targets: C{QuerySet}
        
        @return: Missing permission and the target for which it is missing or
            None if nothing is missing.
        @rtype: tuple (L{ExpedientPermission}, target) or (None, None)
        """
        if not self.are_checks_enabled():
            return (None, None)
        
        from expedient.common.permissions.models import Permittee, \
            ObjectPermission
        
        permittee = Permittee.objects.get_as_permittee(permittee)
        
        # check for superuser
        if isinstance(permittee.object, User) and permittee.object.is_superuser:
            return (None, None)
        
        ct = ContentType.objects.get_for_model(targets.model)
        ids = targets.values_list("pk", flat=True)
        
        obj_perms = ObjectPermission.objects.filter(
            object_type=ct,
            object_id__in=ids,
            permission__name__in=perm_names,
            permittees=permittee,
        )
        
        if obj_perms.count() < len(perm_names) * len(ids):
            # Check if all perm_names exist.
            qs = self.filter(name__in=perm_names)
            if qs.count() < len(set(perm_names)):
                found = list(qs.values_list("name", flat=True))
                for name in perm_names:
                    if name not in found:
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
                            permittees=permittee,
                        )
                    except ObjectPermission.DoesNotExist:
                        # allow permittee == target
                        if ct == permittee.object_type and \
                        id == permittee.object_id:
                            continue
                        return (perm, targets.get(id=id))
            
            # If we reach here then the missing permission must have been
            # the case where permittee == target
            return (None, None)
            
        else:
            return (None, None)
        
    def get_as_permission(self, permission):
        """
        Returns C{permission} as an L{ExpedientPermission} instance.
        
        @param permission: name of the permission or a L{ExpedientPermission}
            instance already.
        @type permission: L{str} or L{ExpedientPermission}
        @return: the same permission.
        @rtype: L{ExpedientPermission}
        """
        from expedient.common.permissions.models import ExpedientPermission
        
        if isinstance(permission, str):
            try:
                return ExpedientPermission.objects.get(name=permission)
            except ExpedientPermission.DoesNotExist:
                raise PermissionDoesNotExist(permission)
            
        elif isinstance(permission, ExpedientPermission):
            return permission
        
        else:
            raise UnexpectedParameterType(
                type(permission), [str, ExpedientPermission], "permission")


class ObjectPermissionManager(GenericObjectManager):
    """
    Adds some useful methods to the default manager type.
    """
    
    def __init__(self):
        super(ObjectPermissionManager, self).__init__("object_type",
                                                      "object_id")
    
    def get_perm_and_obj(self, permission, obj_or_class):
        """
        Turn C{permission} into a L{ExpedientPermission} instance if
        it is not (and it is a permission name).
        Also turn C{obj_or_class} into a model instance if it is a class.
        
        @param permission: the permission's name or the L{ExpedientPermission}
            instance
        @type permission: L{ExpedientPermission} or string
        @param obj_or_class: If this is a class, it will be returned as a
            C{ContentType} instance
        @type obj_or_class: a model instance or class.
        @return: Tuple (permission as L{ExpedientPermission}, obj_or_class as
            a C{Model} instance).
        @rtype: (L{ExpedientPermission}, C{Model})
        """
        from expedient.common.permissions.models import ExpedientPermission

        if not isinstance(obj_or_class, models.Model):
            # assume it's a model class, so get the contenttype for it.
            obj_or_class = ContentType.objects.get_for_model(obj_or_class)

        permission = ExpedientPermission.objects.get_as_permission(permission)

        return (permission, obj_or_class)
    
    def get_or_create_for_object_or_class(self, permission, obj_or_class):
        """
        Get the object permission C{permission} for object C{obj}.
        
        @param permission: the permission's name or the L{ExpedientPermission}
            instance
        @type permission: L{ExpedientPermission} or string
        @param obj_or_class: object for which to get the permission
        @type obj_or_class: a model instance or class.
        @return: tuple (object permission we are looking for, created)
        @rtype: (L{ObjectPermission}, C{bool})
        """
        permission, obj_or_class = self.get_perm_and_obj(
            permission, obj_or_class)
        
        return self.get_or_create_from_instance(
            obj_or_class,
            permission=permission,
        )
        
    def get_for_object_or_class(self, permission, obj_or_class):
        """
        Get the object permission with name C{perm_name} for object C{obj}.
        
        @param permission: the permission's name or the L{ExpedientPermission}
            instance
        @type permission: L{ExpedientPermission} or string
        @param obj_or_class: object for which to get the permission
        @type obj_or_class: a model instance or class.
        @return: the object permission we're looking for
        @rtype: L{ObjectPermission}
        """
        permission, obj_or_class = self.get_perm_and_obj(
            permission, obj_or_class)
        
        return self.filter_from_instance(
            instance=obj_or_class).get(permission=permission)
        
    
    def get_permitted_objects(self, klass, perm_names, permittee):
        """
        Get a queryset of C{klass} instances that the object
        C{permittee} has permissions named by perm_names for.
        
        @param klass: the class of the objects we want.
        @type klass: C{class}
        @param perm_names: list of permission names.
        @type perm_names: [C{str}]
        @param permittee: permission exerciser for whom we're looking
            object permissions.
        @type permittee: C{Model} instance not necessarily a L{Permittee}
        """
        from expedient.common.permissions.models import Permittee
        
        permittee = Permittee.objects.get_as_permittee(permittee)

        def get(perm_name):
            return set(self.get_objects_queryset(
                klass, dict(
                    permission__name=perm_name, permittees=permittee),
                {}).values_list("pk", flat=True))
        
        obj_ids = get(perm_names[0])
        for name in perm_names[1:]:
            obj_ids.intersection_update(get(name))
            
        return klass.objects.filter(pk__in=obj_ids)


class PermitteeManager(GenericObjectManager):
    """
    Extends L{GenericObjectManager} to add useful functions for getting
    L{Permittee}s.
    """
    
    def filter_for_class_and_permission_name(
        self, klass, permission, target_obj_or_class, can_delegate=False):
        """
        Return a queryset filtered for only those who own a permission for
        a particular object. Further, the returned queryset is of class
        given by C{klass}.
        
        @param klass: The class of the objects in the returned queryset.
        @type klass: C{class} or C{ContentType}.
        @param permission: name of the permission or the L{ExpedientPermission}
            object itself that we want the permittee to have
        @type permission: C{str} or L{ExpedientPermission}.
        @param target_obj_or_class: The object or class which we are looking
            for permissions for.
        @type target_obj_or_class: a model instance or class.
        @keyword can_delegate: If true then only look for permittees who can
            give the permission to others.
        @type can_delegate: C{bool} default False.
        """
        
        if isinstance(klass, ContentType):
            ct = klass
        else:
            ct = ContentType.objects.get_for_model(klass)
        
        ids = self.filter_for_permission_name(
                permission, target_obj_or_class, can_delegate=can_delegate,
            ).filter(
                object_type=ct,
            ).values_list("object_id", flat=True)
        return ct.model_class().objects.filter(id__in=ids)
    
    def filter_for_permission_name(self, permission, target_obj_or_class, can_delegate=False):
        """
        Return a queryset filtered for only those who own a permission for
        a particular object.
        
        @param permission: name of the permission or the L{ExpedientPermission}
            object itself that we want the permittee to have
        @type permission: C{str} or L{ExpedientPermission}.
        @param target_obj_or_class: The object or class which we are looking
            for permissions for.
        @type target_obj_or_class: a model instance or class.
        @keyword can_delegate: If true then only look for permittees who can
            give the permission to others.
        @type can_delegate: C{bool} default False.
        """
        from expedient.common.permissions.models import ObjectPermission

        try:
            obj_permission = ObjectPermission.objects.get_for_object_or_class(
                permission, target_obj_or_class)
        except ObjectPermission.DoesNotExist:
            return self.filter(pk=-1)
        
        return self.filter_for_obj_permission(
            obj_permission, can_delegate=can_delegate)
    
    def filter_for_obj_permission(self, obj_permission, can_delegate=False):
        """
        Return a queryset filtered for only those who own a permission for
        a particular object.
        
        @param obj_permission: permission we want the permittees to have
        @type obj_permission: L{ObjectPermission}
        @keyword can_delegate: If true then only look for permittees who can
            give the permission to others.
        @type can_delegate: C{bool} default False.
        """
        
        # filter for superusers
        su_set = User.objects.filter(
            is_superuser=True)

        # Make sure that the superusers all have Permittee counterparts
        su_ids = []
        for su in su_set:
            su_ids.append(self.get_as_permittee(su).id)
        
        su_q = Q(id__in=su_ids)
        
        # check the permission ownership
        pi_q_d = dict(
            permissionownership__obj_permission=obj_permission,
        )
        if can_delegate:
            pi_q_d.update(permissionownership__can_delegate=True)
        pi_q = Q(**pi_q_d)
        
        return self.filter(su_q | pi_q)
    
    def get_as_permittee(self, obj):
        """
        Get the object as a L{Permittee} instance if it is not already.
        If the L{Permittee} for the object does not exist, then create it.
        
        @param obj: the object to return as a L{Permittee} instance.
        @type obj: a C{Model} instance or a L{Permittee} instance.
        @return: the L{Permittee} instance pointing to the object.
        @rtype: L{Permittee}
        """
        from expedient.common.permissions.models import Permittee
        
        if isinstance(obj, Permittee):
            return obj
        elif isinstance(obj, models.Model):
            return self.get_or_create_from_instance(obj)[0]
        else:
            raise UnexpectedParameterType(
                type(obj), [Permittee, models.Model], "obj")
    

class PermissionOwnershipManager(models.Manager):
    """Manager for PermissionOwnership model.
    
    Adds the delete_ownership and get_ownership methods 
    to the default manager.
    """
    
    def get_ownership(self, permission, obj_or_class, owner):
        """Get a PermissionOwnership instance.
        
        @param permission: The name of the permission or its
            L{ExpedientPermission} instance.
        @type permission: C{str} or L{ExpedientPermission}.
        @param obj_or_class: The target object or class for the permission.
        @type obj_or_class: C{Model} instance or C{class}.
        @param owner: The permittee currently owning the permission.
        @type owner: L{Permittee} or C{Model} instance.
        """
        from expedient.common.permissions.models import Permittee
        from expedient.common.permissions.models import ObjectPermission
        from expedient.common.permissions.models import PermissionOwnership
        
        try:
            obj_permission =\
                ObjectPermission.objects.get_for_object_or_class(
                    permission, obj_or_class)
        except ObjectPermission.DoesNotExist:
            raise PermissionOwnership.DoesNotExist()
        
        permittee = Permittee.objects.get_as_permittee(owner)
        
        return self.get(
            obj_permission=obj_permission,
            permittee=permittee,
        )
    
    def delete_ownership(self, permission, obj_or_class, owner):
        """Take permission away from an owner.
        
        Remove the permission C{permission} to use object or class
        C{obj_or_class} from the owner C{owner}. If the owner doesn't
        have the permission to begin with, nothing happens.
        
        @param permission: The name of the permission to remove or its
            L{ExpedientPermission} instance.
        @type permission: C{str} or L{ExpedientPermission}.
        @param obj_or_class: The object or class for which the permission
            is being removed
        @type obj_or_class: C{Model} instance or C{class}.
        @param owner: The permittee currently owning the permission.
        @type owner: L{Permittee} or C{Model} instance.
        """
        from expedient.common.permissions.models import PermissionOwnership
        
        try:
            po = self.get_ownership(permission, obj_or_class, owner)
        except PermissionOwnership.DoesNotExist:
            return
        else:
            po.delete()
        
    def delete_all_for_target(self, obj_or_class, owner):
        """Delete all the permissions owned by C{owner} for target C{obj_or_class}
        
        @param obj_or_class: The object or class for which the permissions
            are being removed
        @type obj_or_class: C{Model} instance or C{class}.
        @param owner: The permittee currently owning the permissions.
        @type owner: L{Permittee} or C{Model} instance.
        """
        from expedient.common.permissions.models import Permittee

        permittee = Permittee.objects.get_as_permittee(owner)
        
        if not isinstance(obj_or_class, models.Model):
            obj_or_class = ContentType.objects.get_for_model()

        obj_type = ContentType.objects.get_for_model(obj_or_class)
        
        self.filter(
            permittee=permittee,
            obj_permission__object_type=obj_type,
            obj_permission__object_id=obj_or_class.id,
        ).delete()
        