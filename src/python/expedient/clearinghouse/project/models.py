'''
@author jnaous
'''
from django.db import models
from django.contrib.auth.models import User
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.common.permissions.models import Permittee, ObjectPermission
from expedient.common.permissions.utils import permissions_save_override,\
    permissions_delete_override

class ProjectManager(models.Manager):
    """Manager for L{Project} instances.
    
    Add methods to retrieve project querysets.
    """
    
    def get_for_member(self, member):
        """Return projects in which C{member} is a member.
        
        This is a wrapper around the C{get_permitted_object} method of
        the L{ObjectPermission} manager.
        
        @param member: The user whose projects we are looking for.
        @type member: C{User}.
        """
        return ObjectPermission.objects.get_permitted_objects(
            klass=Project, perm_names=["can_view_project"], permittee=member)

class Project(models.Model):
    '''
    A project is a collection of users working on the same set of slices.
    
    @cvar objects: A L{ProjectManager} instance.
    
    @ivar name: The name of the project
    @type name: L{str}
    @ivar description: Short description of the project
    @type description: L{str}
    @ivar aggregates: Read-only property returning all aggregates that can
        be used by the project (i.e. for which the project has the
        "can_use_aggregate" permission).
    @type aggregates: C{QuerySet} of L{Aggregate}s
    @ivar members: Read-only property returning all users allowed to view the
        project (i.e. have the "can_view_project" permission for the project).
    @type members: C{QuerySet} of C{User}s.
    @ivar managers: Read-only property returning all users allowed manage
        the project (i.e. have the "can_manage_project" permission
        for the project).
    @type managers: C{QuerySet} of C{User}s.
    '''
    objects = ProjectManager()
    
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    
    save = permissions_save_override(
        permittee_kw="user",
        model_func=lambda: Project,
        create_perm="can_create_project",
        edit_perm="can_edit_project",
        delete_perm="can_delete_project",
    )
    delete = permissions_delete_override(
        permittee_kw="user",
        model_func=lambda: Project,
        delete_perm="can_delete_project",
    )
    
    def get_aggregates(self):
        """Get all aggregates that can be used by the project
        (i.e. for which the project has the "can_use_aggregate" permission).
        """
        return ObjectPermission.objects.get_permitted_objects(
            klass=Aggregate,
            perm_names=["can_use_aggregate"],
            permittee=self,
        )
    aggregates=property(get_aggregates)
    
    def get_members(self):
        """Get all users who have the "can_view_project" permission for
        the project"""
        
        return Permittee.objects.filter_for_class_and_permission_name(
            klass=User,
            permission="can_view_project",
            target_obj_or_class=self,
        )
    members=property(get_members)
    
    def get_managers(self):
        """Return all users who can manage the project"""
        return Permittee.objects.filter_for_class_and_permission_name(
            klass=User,
            permission="can_manage_project",
            target_obj_or_class=self,
        )
    managers=property(get_managers)
    
    def __unicode__(self):
        s = u"Project %s members: %s" % (self.name, self.members.all())
        return s

