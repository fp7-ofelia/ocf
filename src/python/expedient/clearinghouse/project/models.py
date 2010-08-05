'''
@author jnaous
'''
from django.db import models
from expedient.common.permissions.models import Permittee, ObjectPermission
from expedient.common.permissions.utils import permissions_save_override,\
    permissions_delete_override
from expedient.clearinghouse.aggregate.models import Aggregate

class ProjectManager(models.Manager):
    """Manager for L{Project} instances.
    
    Add methods to retrieve project querysets.
    """
    
    def get_for_user(self, user):
        """Return projects for which C{user} has some permission.
        
        @param user: The user whose projects we are looking for.
        @type user: C{User}.
        """
        if user.is_superuser:
            return self.all()
        
        permittee = Permittee.objects.get_as_permittee(user)
        
        proj_ids = ObjectPermission.objects.filter_for_class(
            klass=Project, permittee=permittee).values_list(
                "object_id", flat=True)
        return self.filter(id__in=list(proj_ids))

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
    @ivar researchers: Read-only property returning all users that have the
        'researcher' role for the project.
    @type researchers: C{QuerySet} of C{User}s.
    @ivar owners: Read-only property returning all users that have the 'owner'
        role for the project.
    @type owners: C{QuerySet} of C{User}s.
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
    
    def _get_aggregates(self):
        """Get all aggregates that can be used by the project
        (i.e. for which the project has the "can_use_aggregate" permission).
        """
        return ObjectPermission.objects.get_permitted_objects(
            klass=Aggregate,
            perm_names=["can_use_aggregate"],
            permittee=self,
        )
    aggregates=property(_get_aggregates)
    
    def _get_researchers(self):
        """Get all users who have the 'researcher' role for the project"""
        from expedient.clearinghouse.roles.models import ProjectRole
        return ProjectRole.objects.get_users_with_role('researcher', self)
    researchers=property(_get_researchers)
    
    def _get_owners(self):
        """Get all users who have the 'owner' role for the project"""
        from expedient.clearinghouse.roles.models import ProjectRole
        return ProjectRole.objects.get_users_with_role('owner', self)
    owners=property(_get_owners)
    
    def __unicode__(self):
        s = u"Project %s members: %s" % (self.name, self.members.all())
        return s

