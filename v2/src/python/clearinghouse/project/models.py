from django.db import models
from django.contrib import auth
from clearinghouse.aggregate.models import Aggregate

class Project(models.Model):
    '''
    A project is a collection of users working on the same set of slices.
    
    @param name: The name of the project
    @type name: L{str}
    @param description: Short description of the project
    @type description: L{str}
    @ivar members: The member L{auth.models.User}s of the project.
    @type members: L{models.ManyToManyField}
    '''
    
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    members = models.ManyToManyField(auth.models.User)
    aggregates = models.ManyToManyField(Aggregate)
    
    def __unicode__(self):
        s = u"Project %s members: " % self.name
        s = s + ", ".join(self.members)
        return s
