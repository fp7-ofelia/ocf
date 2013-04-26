'''
Created on May 28, 2010

@author: jnaous
'''
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.auth.models import User
from expedient.common.permissions.exceptions import PermissionCannotBeDelegated
from expedient.common.permissions.managers import ExpedientPermissionManager,\
    ObjectPermissionManager, PermitteeManager, PermissionOwnershipManager

import logging
logger = logging.getLogger("permissions.models")

class ExpedientPermission(models.Model):
    """
    This class holds all instances of L{ObjectPermission} that have a
    particular name. L{ObjectPermission} links permittees to a particular
    object.
    
    A permission may optionally have a view where the browser should be
    redirected if the permission is missing (for example to request the
    permission). The view is specified by its full path in C{view}.
    
    The signature for the view function should be the following::
    
        missing_perm_view(
                request, permission, permittee, target_obj_or_class,
                redirect_to=None)
    
        - C{permission} is the missing L{ExpedientPermission}.
        - C{permittee} is the object that needs to exercise the permission.
        - C{target_obj_or_class} is the object or class whose permission is
            missing.
        - C{redirect_to} is the URL from which the request was made.
    
    One limitation of the system right now is that we can only link to objects
    that use a C{PositiveIntegerField} as the object ID.
    
    @cvar objects: a L{ExpedientPermissionManager} instance.
    @type objects: L{ExpedientPermissionManager}
    
    @ivar name: The permission's name
    @type name: C{str}
    @ivar description: Information about the permission.
    @type description: C{str}
    @ivar view: The full path to the view for the permission
    @type view: C{str}
    @ivar object_permissions: Per-object permissions with this permission name.
    @type object_permissions: m2m relationship to L{ObjectPermission}.
    """
    
    objects = ExpedientPermissionManager()
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")
    view = models.CharField("Permission View", max_length=300,
                            blank=True, null=True)
    
    def __unicode__(self):
        return "perm name: %s, desc: %s, view: %s" % (
            self.name, self.description, self.view)

        

class ObjectPermission(models.Model):
    """
    Links a permission to its object using the C{contenttypes} framework and
    to the set of permittees holding the permission.
    
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
    @ivar permittees: many-to-many relationship to permittees who own
        the object permission
    @type permittees: C{ManyToManyField} to L{Permittee} through
        L{PermissionOwnership}
    """

    objects = ObjectPermissionManager()
    
    permission = models.ForeignKey(ExpedientPermission)
    
    object_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey("object_type", "object_id")
    
    permittees = models.ManyToManyField(
        "Permittee", through="PermissionOwnership")
    
    def __unicode__(self):
        return u"%s object permission for %s" % (self.permission.name,
                                                 self.target)
    
    class Meta:
        unique_together = (
            ("permission", "object_type", "object_id"),
        )
    
    def give_to(self, receiver, giver=None, can_delegate=False):
        """
        Give permission ownership to an object. This method also checks that
        the action is allowed (the C{giver} can actually give the permission
        to C{receiver}).
        
        @param receiver: The permittee receiving the permission. If not a
            L{Permittee} instance, one will be created (if not found).
        @type receiver: L{Permittee} or C{Model} instance.
        @keyword giver: The permission owner giving the permission. If not a
            L{Permittee} instance, one will be created (if not found).
            Defaults to C{None}.
        @type giver: L{Permittee} or C{Model} instance.
        @keyword can_delegate: Can the receiver in turn give the permission
            out? Default is False.
        @type can_delegate: L{bool}
        @return: The new C{PermissionOwnership} instance.
        """
        # Is someone delegating the permission?
        if giver:
            giver = Permittee.objects.get_as_permittee(giver)

            # check that the giver can give ownership
            can_give = Permittee.objects.filter_for_obj_permission(
#                self, can_delegate=True).filter(
                # No need to find for some one that CAN actually delegate...
                # Permissions already take care of this.
                self, can_delegate=False).filter(
                    id=giver.id).count() > 0
                
            if not can_give:
                raise PermissionCannotBeDelegated(
                    giver, self.permission.name)
        
        receiver = Permittee.objects.get_as_permittee(receiver)
        
        # All is good get or create the permission.
        po, created = PermissionOwnership.objects.get_or_create(
            obj_permission=self,
            permittee=receiver,
            defaults=dict(can_delegate=can_delegate),
        )
        
        # Don't change the can_delegate option if the permission was already
        # created unless if it's to enable it. We don't want people
        # taking each other's delegation capabilities (e.g. from owner)
        if po.can_delegate != can_delegate and (created or \
        (not created and can_delegate)):
            po.can_delegate = can_delegate
            po.save()
            
        return po
    
    
class Permittee(models.Model):
    """
    Links permissions to their owners using the C{contenttypes} framework,
    where permittees are not necessarily C{django.contrib.auth.models.User}
    instances.
    
    @cvar objects: L{PermitteeManager} for the class
    
    @ivar object_type: The C{ContentType} indicating the class of the permittee.
    @type object_type: ForeignKey to C{ContentType}
    @ivar object_id: The id of the permittee.
    @type object_id: positive C{int}
    @ivar object: the object for this permittee.
    @type object: varies
    """
    
    objects = PermitteeManager("object_type", "object_id")
    
    object_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey("object_type", "object_id")
    
    def __unicode__(self):
        return u"%s" % self.object
    
    class Meta:
        unique_together=(("object_type", "object_id"),)
        
class PermissionOwnership(models.Model):
    """
    Information on what the permittee can do with the permission.
    
    @cvar objects: L{PermissionOwnershipManager} for the class
    
    @ivar obj_permission: the object permission for this info.
    @type obj_permission: ForeignKey to L{ObjectPermission}
    @ivar permittee: the permittee for this info.
    @type permittee: ForeignKey to L{Permittee}
    @ivar can_delegate: Can the permittee give this permission to someone else?
    @type can_delegate: C{bool}
    """
    
    objects = PermissionOwnershipManager()
    
    obj_permission = models.ForeignKey(ObjectPermission)
    permittee = models.ForeignKey(Permittee)
    can_delegate = models.BooleanField()
    
    def __unicode__(self):
        return u"%s - %s: Delegatable is %s" % (self.obj_permission,
                                                self.permittee,
                                                self.can_delegate)
    
    class Meta:
        unique_together=(("obj_permission", "permittee"),)

class PermissionRequest(models.Model):
    """
    A request from a C{auth.models.User} on behalf of a C{Permittee} to
    obtain some permission for a particular target.
    
    @ivar requesting_user: the user requesting the permission be given to
        C{permittee}.
    @type requesting_user: C{django.contrib.auth.models.User}
    @ivar permittee: The object that will receive the permission if granted.
    @type permittee: L{Permittee}
    @ivar permission_owner: The owner who should grant the permission.
    @type permission_owner: C{django.contrib.auth.models.User}
    @ivar requested_permission: The permission requested.
    @type requested_permission: L{ObjectPermission}
    @ivar message: a message to the permission owner.
    @type message: C{str}
    """
    requesting_user = models.ForeignKey(
        User, related_name="sent_permission_requests")
    permittee = models.ForeignKey(Permittee)
    permission_owner = models.ForeignKey(
        User, related_name="received_permission_requests")
    requested_permission = models.ForeignKey(ObjectPermission)
    message = models.TextField(default="", blank=True)
    
    def allow(self, can_delegate=False):
        self.requested_permission.give_to(
            self.permittee,
            giver=self.permission_owner,
            can_delegate=can_delegate)
        self.delete()
        
    def deny(self):
        self.delete()
