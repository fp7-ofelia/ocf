from django.db import models
from django.core.exceptions import MultipleObjectsReturned
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.common.permissions.shortcuts import must_have_permission
from vt_plugin.models.VM import VM

# Virtualization Plugin class
class VtPlugin(Aggregate):
    '''
    Virtualization Plugin that communicates the Virtualization Aggregate Manager with Expedient
    '''
    # VT Aggregate information field
    information = "An aggregate of VT servers "
    
    class Meta:
        app_label = 'vt_plugin'
        verbose_name = "Virtualization Aggregate"
    
    client = models.OneToOneField('xmlrpcServerProxy', editable = False, blank = True, null = True)


    #def start_slice(self, slice):
    #    super(VtPlugin, self).start_slice(slice)
    #    try:
    #        from vt_plugin.controller.dispatchers.GUIdispatcher import startStopSlice
    #        startStopSlice("start",slice.uuid)
    #    except:
    #        raise

    def stop_slice(self, slice):
        super(VtPlugin, self).stop_slice(slice)
        try:
            from vt_plugin.controller.dispatchers.GUIdispatcher import startStopSlice
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

        vms = self.resource_set.filter_for_class(VM).filter(vm__projectId=project.uuid)
        offending_slices = []
        for vm in vms:
            offending_slices.append(str(vm.vm.getSliceName()))
        # Aggregate has VMs in slices -> stop slices and remove aggregate from there where possible
        if offending_slices:
            for slice in project.slice_set.all():
                try:
                    self.stop_slice(slice)
                    self.remove_from_slice(slice, next)
                except:
                    pass
            raise MultipleObjectsReturned("Please delete all VMs inside aggregate '%s' before removing it from slices %s" % (self.name, str(offending_slices)))
        # Aggregate has no VMs in slices (OK) -> delete completely from project (parent method)
        else:
            return super(VtPlugin, self).remove_from_project(project, next)

    """
    aggregate.remove_from_slice on a VT AM will get here first to check
    that the slice does not contain VMs for the given aggregate
    """
    def remove_from_slice(self, slice, next):
        # If any VM (created inside this slice) is found inside any server of the VT AM, warn
        if self.resource_set.filter_for_class(VM).filter(vm__sliceId=slice.uuid):
            raise MultipleObjectsReturned("Please delete all VMs inside aggregate '%s' before removing it" % str(self.name))
        return super(VtPlugin, self).remove_from_slice(slice, next)
