'''
@author: jnaous
'''
from django.db import models
from expedient.clearinghouse.project.models import Project
from expedient.clearinghouse.aggregate.models import Aggregate
from django.contrib.auth.models import User
from expedient.common.messaging.models import DatedMessage
from expedient.common.permissions.models import ObjectPermission, Permittee
from expedient.clearinghouse.aggregate.utils import get_aggregate_classes

class Slice(models.Model):
    '''
    Holds information about reservations across aggregates
    @ivar name: The name of the Slice
    @type name: L{str}
    @ivar description: Short description of the slice
    @type description: L{str}
    @ivar project: Project in which this slice belongs
    @type project: L{models.ForeignKey} to L{Project}
    @ivar owner: Original creator of the slice
    @type owner: C{User}
    @ivar started: Has this slice been reserved with the aggregates yet? 
    @type started: C{bool}
    @ivar modified: Has this slice been modified since it was last reserved?
    @type modified: C{bool}
    @ivar aggregates: Read-only property returning all aggregates that can
        be used by the project (i.e. for which the project has the
        "can_use_aggregate" permission).
    @type aggregates: C{QuerySet} of L{Aggregate}s
    '''

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    project = models.ForeignKey(Project)
    owner = models.ForeignKey(User, related_name="owned_slices")
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
            
    def _get_aggregates(self):
        """Get all aggregates that can be used by the slice
        (i.e. for which the slice has the "can_use_aggregate" permission).
        """
        agg_ids = []
        agg_classes = get_aggregate_classes()
        permittee = Permittee.objects.get_as_permittee(self)
        for agg_class in agg_classes:
            agg_ids.extend(
                ObjectPermission.objects.filter_for_class(
                    agg_class,
                    permission__name="can_use_aggregate",
                    permittees=permittee,
                ).values_list("object_id", flat=True)
            )
        return Aggregate.objects.filter(pk__in=agg_ids)
    aggregates=property(_get_aggregates)
    