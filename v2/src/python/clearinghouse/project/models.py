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
    members = models.ManyToManyField(auth.models.User)
    
    # @ivar aggregates: The aggregates over which slices can be created
    aggregates = models.ManyToManyField(Aggregate)
    
    def __unicode__(self):
        s = u"Project %s members: " % self.name
        s = s + ", ".join(self.members)
        return s
