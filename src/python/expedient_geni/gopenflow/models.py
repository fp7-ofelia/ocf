'''Contains models for OpenFlow aggregates available through the GENI API.
Created on Sep 13, 2010

@author: jnaous
'''
import logging
from datetime import datetime
from expedient_geni.models import GENIAggregate
from openflow.plugin.models import OpenFlowInterface, OpenFlowSwitch,\
    create_or_update_switches
from openflow.plugin.gapi.rspec import create_resv_rspec, parse_external_rspec
from expedient.common.middleware import threadlocals
from expedient.common.utils import create_or_update

logger = logging.getLogger("gopenflow.models")

class GCFOpenFlowAggregate(GENIAggregate):
    """A PlanetLab Aggregate exposed through the GENI API."""
    information = \
"""
A PlanetLab Aggregate exposed through the GENI API.
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
    
    def update_resources(self):
        """
        See L{GENIAggregate.update_resources}.
        """
        
        rspec = self.proxy.ListResources(
            [self.get_am_cred()],
            {"geni_compressed": False, "geni_available": True})
        
        logger.debug("Got rspec:\n%s" % rspec)
        
        switches = parse_external_rspec(rspec)
        
        create_or_update_switches(switches)
        