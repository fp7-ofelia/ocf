'''
Created on Jul 4, 2010

@author: jnaous
'''
from django.db import models
from expedient.clearinghouse.resources.models import Resource, Sliver
from geni.models import GENIAggergate, GENIAggregateSliceInfo
from xml.etree import cElementTree as et
import calendar

class PlanetLabSliceInfo(GENIAggregateSliceInfo):
    """
    Subclasses L{GENIAggregateSliceInfo} to specify additional attributes
    for PlanetLab RSpecs
    """
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

def get_start_duration(start_time=None, end_time=None):
    """
    Get the start_time and duration in POSIX seconds from the epoch.
    
    @keyword start_time: Optional. A start time for the whole network.
        Default = None.
    @type start_time: C{datetime.datetime} instance
    @keyword end_time: Optional. An end time for the whole network.
        Default = None.
    @type end_time: C{datetime.datetime} instance
    @return: a tuple (start_time, duration)
    @rtype: (int or None, int or None)
    """
    
    if start_time:
        start_time_sec = calendar.timegm(start_time.timetuple())
        if end_time:
            duration = end_time - start_time
            duration = duration.total_seconds()
        else:
            duration = None
    else:
        start_time_sec = None
        duration = None
        
    return (start_time_sec, duration)

class PlanetLabNetwork(Resource):
    """
    PlanetLab NetSpec.
    """
    
    def get_as_elem(self, slice=None):
        """
        Get the PlanetLabNetwork as ElementTree element so it can be added
        to the RSpec and dumped as XML.
        
        @keyword slice: Optional. Slice for which we are producing this RSpec.
            Specifying the slice will set the <sliver /> tag for PlanetLab
            nodes that are part of the slice.
        @type slice: L{expedient.clearinghouse.slice.models.Slice}.
        @return: the NetSpec element
        @rtype: C{xml.etree.ElementTree.Element}
        """

        # see if this network has a sliver in the slice.
        netspec = et.Element("NetSpec", dict(
            name=self.name,
        ))
        
        if slice:
            try:
                sliver = slice.sliver_set.get(resource__pk=self.pk)
                net_sliver = sliver.as_leaf_class()
                stime, duration = get_start_duration(
                    net_sliver.start_time, net_sliver.end_time)
                netspec["start_time"] = "%s" % stime
                netspec["duration"] = "%s" % duration
            except Sliver.DoesNotExist:
                pass

        for rsc_type in ["node"]: #, "link"]:
            # Do all the DB ops in one go to be efficient. If we do this for
            # each node, then we can get really slow.
            if slice:
                # Get the IDs of all the planetlab nodes that are in the slice
                filter_key = "planetlab%s__network" % rsc_type
                rsc_ids = slice.resource_set.filter(
                    **{filter_key: self}).values_list("pk", flat=True)
                # get the wanted sliver info as tuples
                sliver_info_tuples = slice.sliver_set.filter(
                    resource__pk__in=rsc_ids,
                ).values_list("resource_id", "start_time", "end_time")
                # now make the resource ids dictionary keys
                sliver_info = {}
                for t in sliver_info_tuples:
                    sliver_info[t[0]] = t[1:]
            else:
                rsc_ids = []
                sliver_info = {}
            
            rsc_set_elem = et.SubElement(netspec, "%ss" % rsc_type)
            for rsc in getattr(self, "%ss" % rsc_type).all():
                rsc_elem = rsc.get_as_elem()
                if rsc.pk in rsc_ids:
                    # Add sliver tag
                    et.SubElement(rsc_elem, "sliver")
                    # add start/duration
                    stime, duration = get_start_duration(
                        *sliver_info_tuples[rsc.pk])
                    rsc_elem["start_time"] = "%s" % stime
                    rsc_elem["duration"] = "%s" % duration
                rsc_set_elem.append(rsc_elem)
        
        return netspec
    
#class PlanetLabLink(Resource):
#    """
#    A PlanetLab Rspec LinkSpec.
#    """
#    type = models.CharField(max_length=60)
#    init_params = models.TextField(default="")
#    bw = models.IntegerField("Bandwidth")
#    min_alloc = models.IntegerField("Minimum allocation")
#    max_alloc = models.IntegerField("Maximum allocation")
#    network = models.ForeignKey(PlanetLabNetwork, related_name="links")
#    
#    def get_as_elem(self):
#        """
#        Return the link as an ElementTree element.
#        
#        @return: the LinkSpec element
#        @rtype: C{xml.etree.ElementTree.Element}
#        """
#        return et.Element("LinkSpec", dict(
#            name = self.name,
#            type = self.type,
#            init_params = self.init_params,
#            bw = self.bw,
#            min_alloc = self.min_alloc,
#            max_alloc = self.max_alloc,
#        ))

class PlanetLabNode(Resource):
    '''
    A PlanetLab node.
    '''
    type = models.CharField(max_length=60)
    init_params = models.TextField(default="")
    cpu_min = models.IntegerField()
    cpu_share = models.IntegerField()
    cpu_pct = models.IntegerField()
    disk_max = models.IntegerField()
    network = models.ForeignKey(PlanetLabNetwork, related_name="nodes")
    
    def get_as_elem(self):
        """
        Return the node as an ElementTree element.
        
        @return: the NodeSpec element
        @rtype: C{xml.etree.ElementTree.Element}
        """
        node_elem = et.Element("NodeSpec", dict(
            name = self.name,
            type = self.type,
            init_params = self.init_params,
            cpu_min = self.cpu_min,
            cpu_share = self.cpu_share,
            cpu_pct = self.cpu_pct,
            disk_max = self.disk_max,
        ))
        
        net_if = et.SubElement(node_elem, "net_if")
        for iface in self.planetlabinterface_set.all():
            net_if.append(iface.get_as_elem())
            
        return node_elem

class PlanetLabInterface(models.Model):
    '''
    A PlanetLab Interface (IfSpec)
    '''
    name = models.CharField(max_length=200)
    addr = models.CharField("Address", max_length=200)
    type = models.CharField(max_length=60)
    init_params = models.TextField(default="")
    min_rate = models.IntegerField("Minimum Throughput")
    max_rate = models.IntegerField("Maximum Throughput")
    max_kbyte = models.IntegerField()
    ip_spoof = models.BooleanField("Spoof IP Address?")
    
#    link = models.ForeignKey(PlanetLabLink, related_name="endpoints")
    node = models.ForeignKey(PlanetLabNode)

    def get_as_elem(self):
        """
        Return the interface as an ElementTree element.
        
        @return: the IfSpec element
        @rtype: C{xml.etree.ElementTree.Element}
        """
        return et.Element("IfSpec", dict(
            name = self.name,
            addr = self.addr,
            type = self.type,
            init_params = self.init_params,
            min_rate = self.min_rate,
            max_rate = self.max_rate,
            max_kbyte = self.max_kbyte,
            ip_spoof = self.ip_spoof,
        ))
        
#class PlanetLabLinkSliver(Sliver):
#    start_time = models.DateTimeField()
#    end_time = models.DateTimeField()
    
class PlanetLabNodeSliver(Sliver):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

class PlanetLabNetworkSliver(Sliver):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

class PlanetLabAggregate(GENIAggergate):
    information = \
"""
A PlanetLab Aggregate exposed through the GENI API.
"""
    
    def _to_rspec(self, slice):
        info = slice.planetlabsliceinfo
        stime, duration = get_start_duration(info.start_time, info.end_time)
        rspec = et.Element("RSpec", dict(
            start_time="%s" % stime,
            duration = "%s" % duration,
        ))
        
        for net in PlanetLabNetwork.objects.filter(aggregate__pk=self):
            rspec.append(net.get_as_elem(slice))
        
        return rspec
    