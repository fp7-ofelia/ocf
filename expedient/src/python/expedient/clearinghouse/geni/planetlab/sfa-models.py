'''
Created on Jul 4, 2010

@author: jnaous
'''
from django.db import models
from expedient.clearinghouse.resources.models import Resource, Sliver
from expedient.clearinghouse.geni.models import GENIAggregate, GENISliceInfo
from xml.etree import cElementTree as et
import calendar
from exceptions import RSpecParsingException, NameConflictException
import logging

logger = logging.getLogger("PlanetLabModels")

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

class PlanetLabSliceInfo(GENISliceInfo):
    """
    Subclasses L{GENIAggregateSliceInfo} to specify additional attributes
    for PlanetLab RSpecs
    """
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)

class PlanetLabNetwork(Resource):
    """
    PlanetLab NetSpec.
    """
    
    def __unicode__(self):
        return u"PlanetLabNetwork %s" % self.name
    
    @classmethod
    def get_from_elem(cls, pl_aggregate, network_elem):
        """
        Create or update the NetSpec in the DB from the Element C{network_elem}
        that is found in an RSpec. If the same name is in another aggregate,
        a L{NameConflictException} is raised.
        
        @param pl_aggregate: The PlanetLabAggregate to which this network
            belongs.
        @type pl_aggregate: L{PlanetLabAggregate}
        @param network_elem: a NetSpec element from an RSpec.
        @type network_elem: C{xml.etree.ElementTree.Element}
        """
        name = network_elem.get("name")
        
        if not name:
            raise RSpecParsingException("Could not find NetSpec name.")
        
        try:
            net = cls.objects.get(name=name)
        except cls.DoesNotExist:
            net = cls.objects.create(
                name=name, aggregate=pl_aggregate)
            
        if net.aggregate.pk != pl_aggregate.pk:
            raise NameConflictException(
                "Network %s is in a different aggregate." % name)
        
        if net.available == False:
            net.available = True
            net.update_timestamp()
        
        net.save()
        
        # Update the nodes in the network
        current_node_pks = set(
            net.nodes.filter(available=True).values_list("pk", flat=True))
        new_node_pks = set()
        node_elems = network_elem.findall(".//NodeSpec")
        for node_elem in node_elems:
            node = PlanetLabNode.get_from_elem(net, node_elem)
            new_node_pks.add(node.pk)
            logger.debug("Added %s." % node)
            
        # set available to False for old nodes
        old_node_pks = current_node_pks - new_node_pks
        for pk in old_node_pks:
            node = PlanetLabNode.objects.get(pk=pk)
            node.available = False
            node.update_timestamp()
            node.save()
            logger.debug("Set %s to unavailable." % node)
            
        return net
    
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
    
    def __unicode__(self):
        return u"PlanetLabNode %s" % self.name
    
    @classmethod
    def get_from_elem(cls, network, node_elem):
        """
        Create or update the planetlab node in the DB from the Element
        C{node_elem} that is found in an RSpec. If the same name is in another
        aggregate, a L{NameConflictException} is raised.
        
        @param network: The PlanetLabNetwork to which this node belongs.
        @type network: L{PlanetLabNetwork}
        @param node_elem: a NodeSpec element from an RSpec.
        @type node_elem: C{xml.etree.ElementTree.Element}
        """
        name = node_elem.get("name")
        
        if not name:
            raise RSpecParsingException("Could not find NodeSpec name.")
        
        try:
            node = cls.objects.get(name=name)
            if node.aggregate.pk != network.aggregate.pk:
                raise NameConflictException(
                    "Node %s is in a different aggregate." % name)
            if not node.available:
                node.available = True
                node.update_timestamp()
        except cls.DoesNotExist:
            node = cls(name=name, aggregate=network.aggregate, available=True)
            
        for attr in ["type", "init_params"]:
            setattr(node, attr, node_elem.get(attr, ""))
            
        for attr in ["cpu_min", "cpu_share", "cpu_pct", "disk_max"]:
            setattr(node, attr, node_elem.get(attr, 0))
        
        node.network = network
        
        node.save()
        
        # Update the ifaces on the node
        current_iface_pks = set(
            node.interfaces.filter(available=True).values_list("pk", flat=True))
        new_iface_pks = set()
        iface_elems = node_elem.findall(".//IfaceSpec")
        for iface_elem in iface_elems:
            iface = PlanetLabInterface.get_from_elem(node, iface_elem)
            new_iface_pks.add(iface.pk)
            logger.debug("Added %s" % iface)
        
        # set available to False for old interfaces
        old_iface_pks = current_iface_pks - new_iface_pks
        for pk in old_iface_pks:
            iface = PlanetLabInterface.objects.get(pk=pk)
            iface.available = False
            iface.save()
            logger.debug("Set %s to unavailable" % iface)

        return node
    
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
    
    available = models.BooleanField(default=True)
    
#    link = models.ForeignKey(PlanetLabLink, related_name="endpoints")
    node = models.ForeignKey(PlanetLabNode, related_name="interfaces")

    def __unicode__(self):
        return u"PlanetLabInterface %s" % self.name
    
    @classmethod
    def get_from_elem(cls, node, iface_elem):
        """
        Create or update the planetlab interface in the DB from the Element
        C{iface_elem} that is found in an RSpec.
        
        @param node: The PlanetLabNode to which this interface belongs.
        @type network: L{PlanetLabNode}
        @param iface_elem: a IfaceSpec element from an RSpec.
        @type iface_elem: C{xml.etree.ElementTree.Element}
        """
        name = iface_elem.get("name")
        
        if not name:
            raise RSpecParsingException("Could not find IfaceSpec name.")
        
        try:
            iface = cls.objects.get(name=name, node=node)
        except cls.DoesNotExist:
            iface = cls(name=name, node=node)
            
        for attr in ["addr", "type", "init_params"]:
            setattr(iface, attr, iface_elem.get(attr, ""))
            
        for attr in ["min_rate", "max_rate", "max_kbyte"]:
            setattr(iface, attr, iface_elem.get(attr, 0))
        
        for attr in ["ip_spoof"]:
            setattr(iface, attr, iface_elem.get(attr, False))
        
        iface.available = True
        iface.save()
        
        return iface

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

class PlanetLabAggregate(GENIAggregate):
    information = \
"""
A PlanetLab Aggregate exposed through the GENI API.
"""
    
    class Meta:
        verbose_name = "PlanetLab GENI-API Aggregate"
    
    def __unicode__(self):
        return u"PlanetLab GENI-API Aggregate at %s" % self.url
    
    def _to_rspec(self, slice):
        """
        See L{GENIAggregate._to_rspec}.
        """
        info = slice.planetlabsliceinfo
        stime, duration = get_start_duration(info.start_time, info.end_time)
        rspec = et.Element("RSpec", dict(
            start_time="%s" % stime,
            duration = "%s" % duration,
        ))
        
        for net in PlanetLabNetwork.objects.filter(aggregate__pk=self):
            rspec.append(net.get_as_elem(slice))
        
        return rspec
    
    def _list_resources(self):
        """
        See L{GENIAggregate._list_resources}.
        """
        rspec = self.proxy.ListResources(
            [self.get_am_cred()], 
            {"geni_compressed": False, "geni_available": True})
        
        logger.debug("Got rspec:\n%s" % rspec)
        
        root = et.fromstring(rspec)
        
        current_net_pks = set(
            PlanetLabNetwork.objects.filter(
                available=True, aggregate__pk=self.pk).values_list(
                    "pk", flat=True))
        
        logger.debug("Current_net_pks: %s" % current_net_pks)
        
        new_net_pks = set()
        network_elems = root.findall(".//NetSpec")
        for network_elem in network_elems:
            network = PlanetLabNetwork.get_from_elem(self, network_elem)
            new_net_pks.add(network.pk)
            logger.debug("Added %s" % network)
            
        # set available to False for old networks
        old_net_pks = current_net_pks - new_net_pks
        for pk in old_net_pks:
            net = PlanetLabNetwork.objects.get(pk=pk)
            net.available = False
            net.save()
            logger.debug("Set %s to unavailable." % network)

    def add_to_slice(self, slice, next):
        """
        Create a PlanetLabSliceInfo instance for this slice if none exists.
        """
        info, created = PlanetLabSliceInfo.objects.get_or_create(slice=slice)
        slice.aggregate.add(self)
        return next
    
