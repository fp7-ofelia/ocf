'''
@author: jnaous
'''
from django.db import models
from expedient.clearinghouse.project.models import Project
from expedient.clearinghouse.aggregate.models import Aggregate
from django.contrib.auth.models import User
from expedient.common.messaging.models import DatedMessage

class Slice(models.Model):
    '''
    Holds information about reservations across aggregates
    @ivar name: The name of the Slice
    @type name: L{str}
    @ivar description: Short description of the slice
    @type description: L{str}
    @ivar project: Project in which this slice belongs
    @type project: L{models.ForeignKey} to L{Project}
    @ivar aggregates: Aggregates the slice can use.
    @type aggregates: many to many relationship to L{Aggregate}
    @ivar owner: Original creator of the slice
    @type owner: C{User}
    @ivar managers: users who can edit the slice
    @type managers: many to many relationship with C{User}
    @ivar started: Has this slice been reserved with the aggregates yet? 
    @type started: C{bool}
    @ivar modified: Has this slice been modified since it was last reserved?
    @type modified: C{bool}
    '''

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    project = models.ForeignKey(Project)
    aggregates = models.ManyToManyField(Aggregate)
    owner = models.ForeignKey(User, related_name="owned_slices")
    managers = models.ManyToManyField(User, related_name="managed_slices", blank=True)
    started = models.BooleanField(default=False, editable=False)
    modified = models.BooleanField(default=False, editable=False)
    
    def start(self, user):
        """
        Should be an idempotent operation on the aggregates.
        """
        for agg in self.aggregates.all():
            agg.as_leaf_class().start_slice(self)
        self.started = True
        self.modified = False
        self.save()

    def stop(self, user):
        """
        Should be an idempotent operation on the aggregates.
        """
        for agg in self.aggregates.all():
            agg.as_leaf_class().stop_slice(self)
        self.started = False
        self.save()
            
    