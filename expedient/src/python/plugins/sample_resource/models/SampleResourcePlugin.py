from django.db import models
from django.core.exceptions import MultipleObjectsReturned
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.common.permissions.shortcuts import must_have_permission
from sample_resource.models.SampleResource import SampleResource

# Sample Resource Plugin class
class SampleResourcePlugin(Aggregate):
    '''
    Sample Resource Plugin that communicates the Virtualization Aggregate Manager with Expedient
    '''
    # Sample Resource Aggregate information field
    information = "An aggregate of sample resources"
    
    class Meta:
        app_label = 'sample_resource'
        verbose_name = "Sample Resource Aggregate"
    
#    client = models.OneToOneField('xmlrpcServerProxy', editable = False, blank = True, null = True)


    #def start_slice(self, slice):
    #    super(SampleResourcePlugin, self).start_slice(slice)
    #    try:
    #        from sample_resource.controller.dispatchers.GUIdispatcher import startStopSlice
    #        startStopSlice("start",slice.uuid)
    #    except:
    #        raise

    def stop_slice(self, slice):
        super(SampleResourcePlugin, self).stop_slice(slice)
        try:
            from sample_resource.controller.dispatchers.GUIdispatcher import startStopSlice
            startStopSlice("stop",slice.uuid)
        except:
            raise

    """
    aggregate.remove_from_project on a VT AM will get here first to check
    that no slice inside the project contains VMs for the given aggregate
    """
    def remove_from_project(self, project, next):
        # Check permission because it won't always call parent method (where permission checks)
        must_have_permission("user", self.as_leaf_class(), "can_use_aggregate")

        sample_resources = self.resource_set.filter_for_class(SampleResource).filter(sampleresource__projectId=project.uuid)
        offending_slices = []
        for resource in sample_resources:
            offending_slices.append(str(resource.SampleResource.get_slice_name()))
        # Aggregate has VMs in slices -> stop slices and remove aggregate from there where possible
        if offending_slices:
            for slice in project.slice_set.all():
                try:
                    self.stop_slice(slice)
                    self.remove_from_slice(slice, next)
                except:
                    pass
            raise MultipleObjectsReturned("Please delete all Sample Resources inside aggregate '%s' before removing it from slices %s" % (self.name, str(offending_slices)))
        # Aggregate has no VMs in slices (OK) -> delete completely from project (parent method)
        else:
            return super(SampleResourcePlugin, self).remove_from_project(project, next)

    """
    aggregate.remove_from_slice on a VT AM will get here first to check
    that the slice does not contain VMs for the given aggregate
    """
    def remove_from_slice(self, slice, next):
        # If any VM (created inside this slice) is found inside any server of the VT AM, warn
        if self.resource_set.filter_for_class(SampleResource).filter(sampleresource__sliceId=slice.uuid):
            raise MultipleObjectsReturned("Please delete all Sample Resources inside aggregate '%s' before removing it" % str(self.name))
        return super(SampleResourcePlugin, self).remove_from_slice(slice, next)

