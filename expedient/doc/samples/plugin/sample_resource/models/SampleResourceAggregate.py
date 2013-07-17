from django.db import models
from django.core.exceptions import MultipleObjectsReturned
from modules.aggregate.models import Aggregate
from common.permissions.shortcuts import must_have_permission
from sample_resource.models.SampleResource import SampleResource

# SampleResource Aggregate class
class SampleResourceAggregate(Aggregate):
    '''
    SampleResource Aggregate Plugin that communicates the SampleResource Aggregate Manager with Expedient
    '''
    # Sample Resource Aggregate information field
    information = "An aggregate of sample resources"
    
    class Meta:
        app_label = 'sample_resource'
        verbose_name = "Sample Resource Aggregate"
    
    client = models.OneToOneField('xmlrpcServerProxy', editable = False, blank = True, null = True)

    def stop_slice(self, slice):
        pass

    def get_resources(self, slice_id):
        try:
            return SampleResource.objects.filter(slice_id = slice_id, aggregate = self.pk)
        except Exception as e:
            return []

    """
    aggregate.remove_from_project on a SampleResource AM will get here first to check
    that no slice inside the project contains SampleResource's for the given aggregate
    """
    def remove_from_project(self, project, next):
        # Check permission because it won't always call parent method (where permission checks)
        must_have_permission("user", self.as_leaf_class(), "can_use_aggregate")

        sample_resources = self.resource_set.filter_for_class(SampleResource).filter(sampleresource__projectId=project.uuid)
        offending_slices = []
        for resource in sample_resources:
            offending_slices.append(str(resource.SampleResource.get_slice_name()))
        # Aggregate has SampleResource's in slices -> stop slices and remove aggregate from there where possible
        if offending_slices:
            for slice in project.slice_set.all():
                try:
                    self.stop_slice(slice)
                    self.remove_from_slice(slice, next)
                except:
                    pass
            raise MultipleObjectsReturned("Please delete all Sample Resources inside aggregate '%s' before removing it from slices %s" % (self.name, str(offending_slices)))
        # Aggregate has no SampleResource's in slices (OK) -> delete completely from project (parent method)
        else:
            return super(SampleResourcePlugin, self).remove_from_project(project, next)

    """
    aggregate.remove_from_slice on a SampleResource AM will get here first to check
    that the slice does not contain SampleResource's for the given aggregate
    """
    def remove_from_slice(self, slice, next):
        # If any SampleResource (created inside this slice) is found inside the SampleResource AM, warn
        if self.resource_set.filter_for_class(SampleResource).filter(sampleresource__sliceId=slice.uuid):
            raise MultipleObjectsReturned("Please delete all Sample Resources inside aggregate '%s' before removing it" % str(self.name))
        return super(SampleResourcePlugin, self).remove_from_slice(slice, next)

