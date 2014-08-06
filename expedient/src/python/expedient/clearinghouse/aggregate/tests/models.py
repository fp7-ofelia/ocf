'''
Created on Jun 11, 2010

@author: jnaous
'''
from django.db import models
from django.db.models.signals import pre_delete
from expedient.clearinghouse.resources.models import Resource
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.clearinghouse.slice.models import Slice

class DummyAggregate(Aggregate):
    def create_resources(self):
        for i in xrange(1,4):
            DummyResource.objects.create(
                name="DummyResource %s:%s" % (self.id, i),
                aggregate=self)
            
    def stop_slice(self, slice):
        super(DummyAggregate, self).stop_slice(slice)
        DummySliceEvent.objects.get_or_create(
            slice="%s" % slice,
            status="stopped",
            aggregate="%s" % self,
        )

class DummyResource(Resource):
    pass

class DummySliceEvent(models.Model):
    slice = models.TextField()
    status = models.TextField()
    aggregate = models.TextField()
    
def slice_deleted(sender, **kwargs):
    slice = kwargs["instance"]
    DummySliceEvent.objects.create(
        slice="%s" % slice,
        status="deleted",
    )
pre_delete.connect(slice_deleted, Slice)
