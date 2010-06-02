'''
@author: jnaous
'''
from django.db import models
from expedient.clearinghouse.project.models import Project
from expedient.common.permissions.models import PermissionUserModel

class Slice(PermissionUserModel):
    '''
    Holds information about reservations across aggregates
    @ivar name: The name of the Slice
    @type name: L{str}
    @ivar description: Short description of the slice
    @type description: L{str}
    @ivar project: Project in which this slice belongs
    @type project: L{models.ForeignKey} to L{Project}
    '''

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    project = models.ForeignKey(Project)
