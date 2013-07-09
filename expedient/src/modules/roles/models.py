'''
Created on Aug 3, 2010

@author: jnaous
'''
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import F, Count
from expedient.clearinghouse.project.models import Project
from expedient.common.permissions.models import ObjectPermission, Permittee,\
    PermissionOwnership
from expedient.common.messaging.models import DatedMessage

class ProjectRoleManager(models.Manager):
    """Manager for L{ProjectRole} instances."""
    
    def get_users_with_role(self, role_name, project):
        """Get a C{User} query set for users that have role C{role_name} in
        project C{project}
        
        @param role_name: Name of the project role.
        @type role_name: C{str}.
        @param project: project instance.
        @type project: L{Project}.
        @return: all users with that role in the project
        @rtype: C{QuerySet} of C{User} objects.
        """
        user_ids = set(Permittee.objects.filter(
            projectrole__name=role_name,
            projectrole__project=project).values_list(
#                "pk", flat=True))
                "object_id", flat=True))
        return User.objects.filter(pk__in=user_ids)
    
    def filter_for_can_delegate(self, permittee, project):
        """filter for all roles the permittee can fully delegate in a project
        
        @param permittee: object to check for delegatable roles.
        @type permittee: L{Permittee} or C{django.db.models.Model}
        @param project: the project to filter roles for
        @type project: L{Project}
        @return: all project roles the permittee can delegate.
        @rtype: C{QuerySet} of C{ProjectRole}s.
        """
        permittee = Permittee.objects.get_as_permittee(permittee)
        
        # get all the permissions the permittee cannot delegate
        obj_perms_ids = list(ObjectPermission.objects.exclude(
            permissionownership__can_delegate=True,
            permissionownership__permittee=permittee,
        ).filter(projectrole__project=project).values_list("pk", flat=True))
        
        # take out any roles that have a permission the
        # permittee cannot delegate
        return self.exclude(
            obj_permissions__pk__in=obj_perms_ids).filter(
                project=project)
        
    def filter_for_permission(self, perm_name, target):
        """Filter roles that have the permission C{perm_name} for C{target}.
        
        @param perm_name: The name of the permission to filter the roles for.
        @type perm_name: C{str}.
        @param target: The object that is the target of the permission.
        @type target: instance of C{Model}. Note this cannot be a C{class}.
        @return: Only project roles that have the permission for the target.
        @rtype: C{QuerySet} for C{ProjectRole}.
        
        """
        
        return self.filter(
            obj_permissions__permission__name=perm_name,
            obj_permissions__object_type=\
                ContentType.objects.get_for_model(target.__class__),
            obj_permissions__object_id=target.pk,
        ).distinct()

class ProjectRole(models.Model):
    """Groups object permissions together for easier fine-grained management.
    This role is local to a project.
    
    @cvar objects: a L{ProjectRoleManager}.
    
    @ivar name: The name of the role. Doesn't needs to be unique within a
        project.
    @type name: str, max length=100
    @ivar description: Information about the role.
    @type description: TextField
    @ivar project: The project for this role.
    @type project: L{Project}
    @ivar obj_permissions: object permissions that this roles groups.
    @type obj_permissions: C{ManyToManyField} to L{ObjectPermission}.
    @ivar permittees: Set of permittees that have this role.
    @type permittees: C{ManyToManyField} to L{Permittee}.
    """
    
    objects = ProjectRoleManager()
    
    name = models.CharField(
        max_length=100,
        help_text="Enter the name of the role. This should be unique within "
        "the project.")
    description = models.TextField(blank=True, default="",
        help_text="The role's description should help users know what the "
        "role is meant for and what capabilities the role gives.")
    project = models.ForeignKey(Project)
    obj_permissions = models.ManyToManyField(
        ObjectPermission, verbose_name="Role's permissions",
        help_text="Select the permissions that users who have role "
        "should have."
    )
    permittees = models.ManyToManyField(Permittee)
    
    class Meta:
        unique_together = (
            ("name", "project"),
        )
    
    def __unicode__(self):
        return self.name
    
    def give_to_permittee(self, permittee, giver=None, can_delegate=False):
        """Give the role to a permittee. This combines the permittee's
        permissions.
        
        @param permittee: object to give the role to.
        @type permittee: object or L{Permittee} instance.
        @keyword giver: The giver of all the permissions in the roles. If
            not C{None}, the giver will be checked for authorization to
            delegate the permission.
        @type giver: Model instance or L{Permittee}
        @keyword can_delegate: Should the permittee be able to give the
            permissions in the role to others? Default False.
        @type can_delegate: C{bool}.
        """
        
        permittee = Permittee.objects.get_as_permittee(permittee)
        self.permittees.add(permittee)
        for obj_perm in self.obj_permissions.all():
            obj_perm.give_to(
                permittee, giver=giver, can_delegate=can_delegate)

    def delete(self):
        for permittee in self.permittees.all():
            self.remove_from_permittee(permittee)
        return super(ProjectRole, self).delete()

    def remove_from_permittee(self, permittee):
        """Remove all the permissions in this role from the permittee except
        for ones given by another role."""
        
        permittee = Permittee.objects.get_as_permittee(permittee)
        self.permittees.remove(permittee)
        
        # Get the IDs of the other permissions.
        other_roles = ProjectRole.objects.filter(permittees=permittee)
        other_perms_ids = []
        for r in other_roles:
            other_perms_ids.extend(
                r.obj_permissions.all().values_list("id", flat=True))
                
        # get the list of permissions to remove and remove all.
        to_remove = list(self.obj_permissions.exclude(id__in=other_perms_ids))
        PermissionOwnership.objects.filter(
            permittee=permittee, obj_permission__in=to_remove).delete()
    
    def add_permission(self, obj_permission, giver=None, can_delegate=False):
        """Add the object permission to the role and to all permittees who
        have this role.
        
        @param obj_permission: The object permission to add.
        @type obj_permission: L{ObjectPermission}.
        @keyword giver: The giver of the permission in the roles. If
            not C{None}, the giver will be checked for authorization to
            delegate the permission.
        @type giver: Model instance or L{Permittee}
        @keyword can_delegate: Should the permittees with this role be able
            to give the permission to others?
        @type can_delegate: C{bool}.
        """
        
        for p in self.permittees.all():
            obj_permission.give_to(p, giver=giver, can_delegate=can_delegate)
        self.obj_permissions.add(obj_permission)
        
    def remove_permission(self, obj_permission):
        """Opposite of L{add_permission} but does not remove the permission
        from permittees with other roles that have the permission.
        """

        self.obj_permissions.remove(obj_permission)

        permittees = self.permittees.exclude(
            projectrole__obj_permissions=obj_permission,
        )
        
        PermissionOwnership.objects.filter(
            permittee__id__in=list(
                permittees.values_list("pk", flat=True)),
            obj_permission=obj_permission,
        ).delete()
        
class ProjectRoleRequest(models.Model):
    """A request for a project role"""
    
    requester = models.ForeignKey(
        User, help_text="User requesting the role.",
        related_name="role_requests_made")
    requested_role = models.ForeignKey(
        ProjectRole, help_text="Choose a role to request.")
    giver = models.ForeignKey(
        User, help_text="Choose a user to make a request to.",
        related_name="role_requests_received")
    message = models.TextField(
        blank=True, default="",
        help_text="Add a personalized message to the request.")
    
    def approve(self, delegate):
        self.requested_role.give_to_permittee(
            self.requester, giver=self.giver, can_delegate=delegate)
        DatedMessage.objects.post_message_to_users(
            "'%s' '%s' role '%s' to '%s'" % (
                self.giver.username,
                "delegated" if delegate else "gave",
                self.requested_role.name, self.requester.username),
            msg_type=DatedMessage.TYPE_SUCCESS,
            username__in=[self.requester.username, self.giver.username])
        self.delete()
        
    def deny(self):
        DatedMessage.objects.post_message_to_users(
            "%s denied giving role %s to %s" % (
                self.giver.username,
                self.requested_role.name, self.requester.username),
            msg_type=DatedMessage.TYPE_WARNING,
            username__in=[self.requester.username, self.giver.username])
        self.delete()

