from django.db import models
from django.contrib import auth
from clearinghouse.aggregate.models import Aggregate

class Project(models.Model):
    '''Slices belong to projects.'''
    
    # @ivar name: The name of the project
    name = models.CharField(max_length=200, unique=True)
    
    # @ivar description: Short description of the project
    description = models.TextField()
    
    # @ivar members: The member users of the project. Each member has a role.
    members = models.ManyToManyField(auth.models.User, through="ProjectRole")
    
    # @ivar aggregates: The aggregates over which slices can be created
    aggregates = models.ManyToManyField(Aggregate)
    
    def __unicode__(self):
        s = u"Project %s members: " % self.name
        for r in self.projectrole_set():
            s = s + u"%s (%s), " % (r.member, r.role)
        return s
    
class ProjectRole(models.Model):
    '''Role of a member in a project'''
    
    PI = 'Principal Investigator'
    RESEARCHER = 'Researcher'
    EXPERIMENTER = 'Experimenter'
    USER = 'User'
    
    ROLES = {PI: 'Owner of the project. Can create slices and add ' + 
             'researchers, experimenters, and users. Responsible for ' +
             'actions of project members.',
             RESEARCHER: 'Can create slices and add other researchers, ' +
             'experimenters, and users.',
             EXPERIMENTER: 'Can create slices and add users',
             USER: 'Can access/use precreated slices',
             }
    # @ivar rols: The member's role in the project.
    role = models.CharField(max_length=200, choices=ROLES.items())
    
    # @ivar member: The User instance
    member = models.ForeignKey(auth.models.User)
    
    # @ivar project: The Project instance
    project = models.ForeignKey(Project)

    def __unicode__(self):
        return u"%s: %s" % (self.role, self.get_role_display())
    
