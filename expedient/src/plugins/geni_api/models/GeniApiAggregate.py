"""
Communicates the GeniApi Aggregate Manager with Expedient.

@date: Jun 12, 2013
@author: CarolinaFernandez
"""

from django.db import models
from django.core.exceptions import MultipleObjectsReturned
from modules.aggregate.models import Aggregate
from common.permissions.shortcuts import must_have_permission
from geni_api.models.GeniApi import GeniApi

# GeniApi Aggregate class
class GeniApiAggregate(Aggregate):
    # Sample Resource Aggregate information field
    information = "An aggregate of sample resources"
    
    class Meta:
        app_label = 'geni_api'
        verbose_name = "Sample Resource Aggregate"
    
    api_version = models.IntegerField()
    rspec_version = models.CharField(max_length=30)
    uuid = models.CharField(max_length=36)
    urn = models.CharField(max_length=256)
    gid = models.TextField("GID")

    client = models.OneToOneField('xmlrpcServerProxy', editable = False, blank = True, null = True)
    def stop_slice(self, slice):
        super(GeniApiAggregate, self).stop_slice(slice)
        pass

#    def get_resources(self, slice_id):
    def get_resources(self):
        try:
#            return GeniApi.objects.filter(slice_id = slice_id, aggregate = self.pk)
            return GeniApi.objects.filter(aggregate = self.pk)
        except Exception as e:
            return []

    def remove_from_project(self, project, next):
        """
        aggregate.remove_from_project on a GeniApi AM will get here first to check
        that no slice inside the project contains GeniApi's for the given aggregate
        """
        # Check permission because it won't always call parent method (where permission checks)
        must_have_permission("user", self.as_leaf_class(), "can_use_aggregate")

        geni_apis = self.resource_set.filter_for_class(GeniApi).filter(sampleresource__project_id=project.uuid)
        offending_slices = []
        for resource in geni_apis:
            offending_slices.append(str(resource.GeniApi.get_slice_name()))
        # Aggregate has GeniApi's in slices -> stop slices and remove AM from it if possible
        if offending_slices:
            for slice in project.slice_set.all():
                try:
                    self.stop_slice(slice)
                    self.remove_from_slice(slice, next)
                except:
                    pass
            raise MultipleObjectsReturned("Please delete all Sample Resources inside aggregate '%s' before removing it from slices %s" % (self.name, str(offending_slices)))
        # Aggregate has no GeniApi's in slices (OK) -> delete completely from project (parent method)
        else:
            return super(GeniApiAggregate, self).remove_from_project(project, next)

    def remove_from_slice(self, slice, next):
        """
        aggregate.remove_from_slice on a GeniApi AM will get here first to check
        that the slice does not contain GeniApi's for the given aggregate
        """
        # Warn if any GeniApi (created in this slice) is found inside the GeniApi AM
        if self.resource_set.filter_for_class(GeniApi).filter(sampleresource__slice_id=slice.uuid):
            raise MultipleObjectsReturned("Please delete all Sample Resources inside aggregate '%s' before removing it" % str(self.name))
        return super(GeniApiAggregate, self).remove_from_slice(slice, next)

