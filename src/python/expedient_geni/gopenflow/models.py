'''Contains models for OpenFlow aggregates available through the GENI API.
Created on Sep 13, 2010

@author: jnaous
'''
import logging
from expedient_geni.models import GENIAggregate
from openflow.plugin.models import \
    create_or_update_switches, create_or_update_links, get_raw_topology
from openflow.plugin.gapi.rspec import create_resv_rspec, parse_external_rspec
from expedient.common.middleware import threadlocals

logger = logging.getLogger("gopenflow.models")

class GCFOpenFlowAggregate(GENIAggregate):
    """An OpenFlow Aggregate exposed through the GENI API."""
    information = \
"""
An OpenFlow Aggregate exposed through the GENI API.
"""

    class Meta:
        verbose_name = "OpenFlow GENI-API Aggregate"
    
    def __unicode__(self):
        return u"OpenFlow GENI-API Aggregate at %s" % self.url
    
    def _to_rspec(self, slice):
        """
        See L{GENIAggregate._to_rspec}.
        """
        user = threadlocals.get_thread_locals()["user"]
        return create_resv_rspec(user, slice, aggregate=self)
    
    def _from_rspec(self, rspec):
        """
        See L{GENIAggregate._from_rspec}.
        """
        switches, links = parse_external_rspec(rspec)
        
        create_or_update_switches(self, switches)
        create_or_update_links(self, links)
        
    def get_raw_topology(self):
        return get_raw_topology(self)