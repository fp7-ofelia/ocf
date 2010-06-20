'''
@author jnaous
'''
from django.db import models
from django.contrib.auth.models import User
from expedient.clearinghouse.aggregate.models import Aggregate

class Project(models.Model):
    '''
    A project is a collection of users working on the same set of slices.
    
    @ivar name: The name of the project
    @type name: L{str}
    @ivar description: Short description of the project
    @type description: L{str}
    @ivar members: The member L{auth.models.User}s of the project.
    @type members: L{models.ManyToManyField}
    @ivar owner: The person who created and is reponsible for the project.
    @type owner: L{auth.models.User}
    @ivar aggregates: The aggregates this project can use.
    @type aggregates: ManyToMany to L{Aggregate}
    '''
    
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    members = models.ManyToManyField(User)
    owner = models.ForeignKey(User, related_name="owned_projects")
    aggregates = models.ManyToManyField(Aggregate)
    
    def __unicode__(self):
        s = u"Project %s members: %s" % (self.name, self.members.all())
        return s

