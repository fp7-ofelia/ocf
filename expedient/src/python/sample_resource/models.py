from django.db import models
from django.core.exceptions import MultipleObjectsReturned
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.common.permissions.shortcuts import must_have_permission
#from sample_resource.models.SampleResource import SampleResource

from expedient.clearinghouse.resources.models import Resource

class SampleResource(Resource):
    '''
    SampleResource class.
    '''

    class Meta:
        app_label = 'sample_resource'

    interfaces = models.ManyToManyField('iFace', blank = True, null = True)
    project_id = models.CharField(max_length = 1024, default="")
    project_name = models.CharField(max_length = 1024, default="")
    slice_id = models.CharField(max_length = 1024, default="")
    slice_name = models.CharField(max_length = 1024, default="")
    system_type = models.CharField(max_length = 512, default="")
    system_version = models.CharField(max_length = 512, default="")
    technology = models.CharField(max_length = 10, default="")
    temperature = models.FloatField(blank = True, null=True)
    uuid = models.CharField(max_length = 1024, default="")

    def complete_delete(self):
        self.action_set.clear()
        for interface in self.interfaces.all():
            self.interfaces.remove(interface)
            interface.delete()
        super(SampleResource, self).delete()

    def get_project_id(self):
        return self.project_id

    def get_project_name(self):
        return self.project_name

    def get_slice_id(self):
        return self.slice_id

    def get_slice_name(self):
        return self.slice_name

    def get_system_type(self):
        return self.system_type

    def get_system_version(self):
        return self.system_version

    def get_technology(self):
        return self.technology

    def get_temperature(self):
        return self.temperature

    def get_uuid(self):
        return self.uuid

    def set_project_id(self, project_id):
        self.project_id = project_id

    def set_project_name(self, project_name):
        self.project_name = project_name

    def set_slice_id(self, slice_id):
        self.slice_id = slice_id

    def set_slice_name(self, slice_name):
        self.slice_name = slice_name

    def set_system_type(self, system_type):
        self.system_type = system_type

    def set_system_version(self, system_version):
        self.system_version = system_version

    def set_technology(self, technology):
        self.technology = technology

    def set_temperature(self, temperature):
        self.temperature = temperature

    def set_uuid(self, uuid):
        self.uuid = uuid


# SampleResource plugin class
class SampleResourcePlugin(Aggregate):
    '''
    SampleResource plugin that communicates the SampleResource Aggregate Manager with Expedient.
    '''
    # SampleResource Aggregate information field
    information = "An aggregate of sample resources"

    class Meta:
        app_label = 'sample_resource'
        verbose_name = "SampleResource Aggregate"

    client = models.OneToOneField('xmlrpcServerProxy', editable = False, blank = True, null = True)

    def stop_slice(self, slice):
        super(SampleResource, self).stop_slice(slice)
        try:
            pass
#            from vt_plugin.controller.dispatchers.GUIdispatcher import startStopSlice
#            startStopSlice("stop",slice.uuid)
        except:
            raise

    """
    aggregate.remove_from_project on a SampleResource AM will get here first to check
    that no slice inside the project contains sample resources for the given aggregate
    """
    def remove_from_project(self, project, next):
        # Check permission because it won't always call parent method (where permission checks)
        must_have_permission("user", self.as_leaf_class(), "can_use_aggregate")

        vms = self.resource_set.filter_for_class(SampleResource).filter(sample_resource__project_id = project.uuid)
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
            raise MultipleObjectsReturned("Please delete all sample resources inside aggregate '%s' before removing it from slices %s" % (self.name, str(offending_slices)))
        # Aggregate has no VMs in slices (OK) -> delete completely from project (parent method)
        else:
            return super(SampleResource, self).remove_from_project(project, next)

    """
    aggregate.remove_from_slice on a VT AM will get here first to check
    that the slice does not contain VMs for the given aggregate
    """
    def remove_from_slice(self, slice, next):
        # If any VM (created inside this slice) is found inside any server of the VT AM, warn
        if self.resource_set.filter_for_class(VM).filter(vm__sliceId=slice.uuid):
            raise MultipleObjectsReturned("Please delete all sample resources inside aggregate '%s' before removing it" % str(self.name))
        return super(SampleResources, self).remove_from_slice(slice, next)

