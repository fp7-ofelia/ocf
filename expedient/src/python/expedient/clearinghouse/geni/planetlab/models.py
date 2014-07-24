'''
Created on Jul 4, 2010

@author: jnaous
'''
from django.db import models
from expedient.clearinghouse.resources.models import Resource, Sliver
from expedient.clearinghouse.geni.models import GENIAggregate, GENISliceInfo
from expedient.common.utils import create_or_update
from xml.etree import cElementTree as et
import logging
from datetime import datetime

logger = logging.getLogger("PlanetLabModels")

class PlanetLabSliver(Sliver):
    pass

class PlanetLabNode(Resource):
    '''
    A PlanetLab node.
    '''
    
    node_id = models.CharField(max_length=256)
    
    class Meta:
        verbose_name = "PlanetLab Node"
    
    def __unicode__(self):
        return u"Planetlab node %s" % self.name

class PlanetLabAggregate(GENIAggregate):
    information = \
"""
A PlanetLab Aggregate exposed through the GENI API.
"""
   
    rspec = models.TextField("RSpec", editable=False,)
    
    class Meta:
        verbose_name = "PlanetLab GENI-API Aggregate"
    
    def __unicode__(self):
        return u"PlanetLab GENI-API Aggregate at %s" % self.url
    
    def _to_rspec(self, slice):
        """
        See L{GENIAggregate._to_rspec}.
        """
        # get all the reserved nodes
        reserved = PlanetLabNode.objects.filter(
            aggregate__pk=self.pk, slice_set=slice)
        
        # Get the ids of all reserved nodes
        node_ids = reserved.values_list("node_id", flat=True)
        
        rspec = "%s" % self.rspec
        
        # parse the rspec
        root = et.fromstring(rspec)
        
        # get a mapping from node id to node elem (since this version of
        # elementtree doesn't have XPath working well.
        node_elems = root.findall(".//node")
        node_dict = {}
        for node_elem in node_elems:
            id = node_elem.get("id", None)
            if id:
                node_dict[id] = node_elem
            
        # for each node_id in the reservation, find the corresponding
        # node_elem and add a sliver tag.
        for node_id in node_ids:
            node_elem = node_dict[node_id]
            et.SubElement(node_elem, "sliver")
        
        logger.debug("Sending PlanetLab Reservation RSpec:\n%s" 
                     % et.tostring(root))
        
        return et.tostring(root)
    
    def _from_rspec(self, rspec):
        """
        See L{GENIAggregate._from_rspec}.
        """
        root = et.fromstring(rspec)
        
        # get all planet lab nodes in the rspec.
        node_elems = root.findall(".//node")
        active_node_pks = []
        for elem in node_elems:
            node_id = elem.get("id", None)
            hostname = elem.findtext(".//hostname")
            # TODO: not interested if there's no node id and hostname
            if node_id and hostname:
                # Create/update a matching node. Put it in this aggregate.
                node, created = create_or_update(
                    PlanetLabNode,
                    filter_attrs=dict(name=hostname),
                    new_attrs=dict(node_id=node_id, aggregate=self)
                )
                active_node_pks.append(node.pk)
                logger.debug("Found node id %s name %s - created: %s" % (
                    node_id, hostname, created))
                
        # make disappeared nodes unavailable
        # we filter by aggregate so we don't make a node unavailable
        # if it has moved to another aggregate.
        PlanetLabNode.objects.filter(
            aggregate__pk=self.pk).exclude(pk__in=active_node_pks).update(
                available=False, status_change_timestamp=datetime.now())

        # save the RSpec
        self.rspec = rspec
        self.save()
        
