from django.db import models
from django.contrib.auth.models import User

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
    members = models.ManyToManyField(User)
    
    def __unicode__(self):
        s = u"Project %s members: %s" % (self.name, self.members.all())
        return s
