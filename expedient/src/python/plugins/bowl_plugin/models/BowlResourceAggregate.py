#
# BOWL expedient plugin for the Berlin Open Wireless Lab
# based on the sample plugin
#
# Authors: Theresa Enghardt (tenghardt@inet.tu-berlin.de)
#          Robin Kuck (rkuck@net.t-labs.tu-berlin.de)
#          Julius Schulz-Zander (julius@net.t-labs.tu-berlin.de)
#          Tobias Steinicke (tsteinicke@net.t-labs.tu-berlin.de)
#
# Copyright (C) 2013 TU Berlin (FG INET)
# All rights reserved.
#
"""
Class for BOWL AM

@date: Jul 08, 2013
@author: Theresa Enghardt
"""

from django.db import models
from django.core.exceptions import MultipleObjectsReturned
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.common.permissions.shortcuts import must_have_permission
from bowl_plugin.models.BowlResource import BowlResource
import jsonrpclib
import logging

# BOWL Aggregate class
class BowlResourceAggregate(Aggregate):
    information = "An aggregate of wireless nodes"
    
    class Meta:
        app_label = 'bowl_plugin'
        verbose_name = "BOWL Aggregate"
    
    client = models.OneToOneField('xmlrpcServerProxy', editable = False, blank = True, null = True)

    def stop_slice(self, slice):
        super(BowlResourceAggregate, self).stop_slice(slice)
        pass

#    def get_resources(self, slice_id):
    def get_resources(self):
        logger = logging.getLogger(__name__)
        logger.info("Getresources for aggregate: %s from %s" % (str(self), str(self.client.url)))
        nodes = []

        try:
            s = jsonrpclib.Server(self.client.url)
            res = s.ListResources(available=False)
            #if not res:
            #    nodes = []
            #res = s.ListResources(available=True)
            #if not res:
            #    nodes.append(res)
            #print("Resources: %s" % str(res))
            #print("Nodes: %s" % str(nodes))
            return res
#            return BowlResource.objects.filter(slice_id = slice_id, aggregate = self.pk)
#            return BowlResource.objects.filter(aggregate = self.pk)
        except Exception as e:
            logger.error("Could not connect: %s" % e)
            return []

    def remove_from_project(self, project, next):
        """
        aggregate.remove_from_project on a BOWL AM will get here first to check
        that no slice inside the project contains BOWL Nodes for the given aggregate
        """
        # Check permission because it won't always call parent method (where permission checks)
        must_have_permission("user", self.as_leaf_class(), "can_use_aggregate")

        bowl_nodes = self.resource_set.filter_for_class(BowlResource).filter(bowlresource__project_id=project.uuid)
        offending_slices = []
        for resource in bowl_nodes:
            offending_slices.append(str(resource.BowlResource.get_slice_name()))
        # Aggregate has Bowl Nodes in slices -> stop slices and remove AM from it if possible
        if offending_slices:
            for slice in project.slice_set.all():
                try:
                    self.stop_slice(slice)
                    self.remove_from_slice(slice, next)
                except:
                    pass
            raise MultipleObjectsReturned("Please delete all Bowl Nodes inside aggregate '%s' before removing it from slices %s" % (self.name, str(offending_slices)))
        # Aggregate has no BOWL Nodes in slices (OK) -> delete completely from project (parent method)
        else:
            return super(BowlResourceAggregate, self).remove_from_project(project, next)

    def remove_from_slice(self, slice, next):
        """
        aggregate.remove_from_slice on a BOWL AM will get here first to check
        that the slice does not contain BOWL Nodes for the given aggregate
        """
        # Warn if any Bowl Node (created in this slice) is found inside the BOWL AM
        if self.resource_set.filter_for_class(BowlResource).filter(bowlresource__slice_id=slice.uuid):
            raise MultipleObjectsReturned("Please delete all Bowl Nodes inside aggregate '%s' before removing it" % str(self.name))
        return super(BowlResourceAggregate, self).remove_from_slice(slice, next)

