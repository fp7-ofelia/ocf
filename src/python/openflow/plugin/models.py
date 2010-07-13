'''
Created on Apr 26, 2010

@author: jnaous
'''

from django.db import models
from expedient.clearinghouse.resources import models as resource_models
from expedient.clearinghouse.slice import models as slice_models
from expedient.clearinghouse.aggregate import models as aggregate_models
from expedient.common.xmlrpc_serverproxy.models import PasswordXMLRPCServerProxy
from django.core.urlresolvers import reverse
from django.utils.datetime_safe import datetime
from autoslug.fields import AutoSlugField
from django.db.models import signals

import logging
from expedient.common.utils import create_or_update
logger = logging.getLogger("OpenflowModels")

def as_is_slugify(value):
    return value

class OpenFlowSliceInfo(models.Model):
    slice = models.OneToOneField(slice_models.Slice)
    controller_url = models.CharField(
        "OpenFlow controller URL", max_length=100,
        help_text="e.g. tcp:beirut.stanford.edu:6633")
    # TODO: It is not a good idea to store the password in the clear.
    password = models.CharField(
        max_length=64, help_text="This is the password to use when accessing\
 the slice directly at the flowvisors.")

class OpenFlowAggregate(aggregate_models.Aggregate):
    information = \
"""
OpenFlow is an open standard that allows network switches to be controlled by
a remote controller. It enables researchers to run experimental protocols in
production networks, and is currently deployed in several universities.
"""

    client = models.OneToOneField(PasswordXMLRPCServerProxy)
    usage_agreement = models.TextField()
    
    class Meta:
        verbose_name = "OpenFlow Aggregate"
        
    def setup_new_aggregate(self, base_uri):
        self.client.install_trusted_ca()
        # TODO: re-enable this for security. Currently disabled for testing.
#        err = self.client.change_password()
#        if err: return err
        if base_uri.endswith("/"): base_uri = base_uri[:-1]
        try:
            logger.debug("Registering topology callback at %s%s" % (
                base_uri, reverse("openflow_open_xmlrpc")))
            err = self.client.proxy.register_topology_callback(
                "%s%s" % (base_uri, reverse("openflow_open_xmlrpc")),
                "%s" % self.pk,
            )
            if err: return err
        except Exception as ret_exception:
            import traceback
            logger.info("XML RPC call failed to aggregate %s" % self.name)
            traceback.print_exc()
            return str(ret_exception)

        err = self.update_topology()
        if err: return err
        
    def get_raw_topology(self):
        '''
        Get the topology for this aggregate as a set of links.
        '''
        links = set()
        for iface in OpenFlowInterface.objects.filter(
        aggregate=self).select_related("switch", "ingress_neighbors__switch"):
            for in_ngbr in iface.ingress_neighbors.all():
                links.add((iface.switch.datapath_id, iface.port_num,
                           in_ngbr.switch.datapath_id, in_ngbr.port_num))

        return links
    
    def parse_switches(self):
        '''
        Update the set of available switches.
        '''
        # switches already in the DB.
        current_switches = OpenFlowSwitch.objects.filter(aggregate=self)

        # switch info received from FlowVisor
        active_switches_raw = self.client.proxy.get_switches()
        
        active_switch_ids = []
        active_iface_ids = []
        for switch_info in active_switches_raw:
            dpid, info = switch_info
            
            # The ports is a comma-separated set of values (see flowvisor API).
            portstrs = info["portList"].split(",")
            # turn into port numbers
            ports = [int(p) for p in portstrs if p != ""]
            
            # find the switch with the dpid if it exists and create/update it
            switch, created = create_or_update(
                OpenFlowSwitch,
                filter_attrs=dict(
                    datapath_id=dpid,
                ),
                new_attrs=dict(
                    aggregate=self,
                    name=dpid,
                    available=True,
                    status_change_timestamp=datetime.now(), 
                )
            )
            active_switch_ids.append(switch.id)
            
            for port in ports:
                # update the interfaces for this switch
                iface, created = create_or_update(
                    OpenFlowInterface,
                    filter_attrs=dict(
                        switch__datapath_id=dpid,
                        port_num=port,
                    ),
                    new_attrs=dict(
                        aggregate=self,
                        name="Port %s" % port,
                        switch=switch,
                        available=True,
                        status_change_timestamp=datetime.now(), 
                    ),
                )
                logger.debug("Added interface %s:%s" % (dpid, port))
                active_iface_ids.append(iface.id)
                
        # make all inactive switches and interfaces unavailable.
        OpenFlowInterface.objects.filter(
            aggregate=self).exclude(id__in=active_iface_ids).update(
                available=False, status_change_timestamp=datetime.now())
            
        OpenFlowSwitch.objects.filter(
            aggregate=self).exclude(id__in=active_switch_ids).update(
                available=False, status_change_timestamp=datetime.now())
        
    def parse_links(self):
        '''
        Get the available links and update the network connections.
        '''
        active_links_raw = self.client.proxy.get_links()
    
        active_cnxn_ids = []
        # Create any missing connections.
        for src_dpid, src_port, dst_dpid, dst_port, attrs in active_links_raw:
            logger.debug("parsing link %s:%s - %s:%s" % (
                src_dpid, src_port, dst_dpid, dst_port))
            cnxn, created = OpenFlowConnection.objects.get_or_create(
                src_iface=OpenFlowInterface.objects.get(
                    switch__datapath_id=src_dpid,
                    port_num=src_port,
                ),
                dst_iface=OpenFlowInterface.objects.get(
                    switch__datapath_id=dst_dpid,
                    port_num=dst_port,
                ),
            )
            active_cnxn_ids.append(cnxn.id)
            
        # Delete old connections.
        OpenFlowConnection.objects.filter(
            # Make sure all the connections we delete have both end points in
            # the aggregate.
            src_iface__switch__aggregate=self,
            dst_iface__switch__aggregate=self).exclude(
                # don't delete active connections
                id__in=active_cnxn_ids).delete()
        
    def update_topology(self):
        '''
        Read the topology from the OM and FV, parse it, and store it.
        '''
        try:
            self.parse_switches()
            self.parse_links()
        except:
            import traceback
            traceback.print_exc()
            raise
        
    def _get_slivers(self, slice):
        """
        Get the set of slivers in the slice for this aggregate in a format
        that the OM understands.
        
        @param slice: The slice to get slivers from
        @type slice: L{expedient.clearinghouse.slice.models.Slice}
        @return: C{dict} containing a mapping from datapath ids in the aggregate
            to flowspaces on that switch.
        @rtype: C{dict}
        """
        # get all interfaces in this slice
        ifaces = OpenFlowInterface.objects.filter(
            slice_set=slice, aggregate__id=self.id).select_related(
                'flowspacerule_set', 'switch')
        
        # get the list of dpids in the slice
        dpids = set(ifaces.values_list('switch__datapath_id', flat=True))
        
        sw_slivers = []
        # For each dpid, get the flowspace by looking at the interface slivers
        for dpid in dpids:
            d = {}
            d['datapath_id'] = dpid
            d['flowspace'] = []
            for iface in ifaces.filter(switch__datapath_id=dpid):
                sliver = iface.sliver_set.get(slice=slice).as_leaf_class()
                for fs in sliver.flowspacerule_set.all():
                    fsd = {"port_num_start": iface.port_num,
                           "port_num_end": iface.port_num}
                    for f in fs._meta.fields:
                        if f.name != "sliver":
                            fsd[f.name] = getattr(fs, f.name)
                    d['flowspace'].append(fsd)
            sw_slivers.append(d)
            
        return sw_slivers

    ###################################################################
    # Following are overrides from aggregate_models.Aggregate
    
    def check_status(self):
        return self.available and self.client.is_available()

    def get_edit_url(self):
        return reverse("openflow_aggregate_edit",
                       kwargs={'agg_id': self.id})
    
    def add_to_slice(self, slice, next):
        return reverse("openflow_aggregate_slice_add",
                       kwargs={'agg_id': self.id,
                               'slice_id': slice.id})+"?next="+next

    @classmethod
    def get_aggregates_url(cls):
        return reverse("openflow_aggregate_home")

    @classmethod
    def get_create_url(cls):
        return reverse("openflow_aggregate_create")
    
    def start_slice(self, slice):
        sw_slivers = self._get_slivers(slice)
        try:
            return self.client.proxy.create_slice(
                slice.id, slice.project.name,
                slice.project.description,
                slice.name, slice.description,
                slice.openflowsliceinfo.controller_url,
                slice.owner.email,
                slice.openflowsliceinfo.password, sw_slivers)
        except Exception as ret_exception:
            import traceback
            logger.info("XML RPC call failed to aggregate %s" % self.name)
            traceback.print_exc()
            return {'error_msg':str(ret_exception),'switches':[]}

    def stop_slice(self, slice):
        try:
            self.client.proxy.delete_slice(slice.id)
        except Exception as e:
            import traceback
            logger.info("XML RPC call failed to aggregate %s" % self.name)
            traceback.print_exc()
            return "%s" % e
    
class OpenFlowSwitch(resource_models.Resource):
    datapath_id = models.CharField(max_length=100, unique=True)
    
    def __unicode__(self):
        return "OpenFlow Switch %s" % self.datapath_id

class OpenFlowConnection(models.Model):
    '''Connection between two interfaces'''
    src_iface = models.ForeignKey("OpenFlowInterface",
                                  related_name="ingress_connections")
    dst_iface = models.ForeignKey("OpenFlowInterface",
                                  related_name="egress_connections")
    slug = AutoSlugField(
        populate_from=lambda instance: "%s_%s_%s_%s" % (
            instance.src_iface.switch.datapath_id,
            instance.src_iface.port_num,
            instance.dst_iface.switch.datapath_id,
            instance.dst_iface.port_num,
        ),
        slugify=as_is_slugify,
        editable=False,
    )
    
    class Meta:
        unique_together=(("src_iface", "dst_iface"),)
    
    def __unicode__(self):
        return "%s to %s" % (self.src_iface, self.dst_iface)

class OpenFlowInterface(resource_models.Resource):
    port_num = models.IntegerField()
    switch = models.ForeignKey(OpenFlowSwitch)
    ingress_neighbors = models.ManyToManyField(
        'self', symmetrical=False,
        related_name="egress_neighbors",
        through=OpenFlowConnection,
    )
    slug = AutoSlugField(
        populate_from=lambda instance: "%s_%s" % (
            instance.switch.datapath_id, instance.port_num),
        slugify=as_is_slugify,
        editable=False,
    )

    class Meta:
        unique_together=(("switch", "port_num"),)
        verbose_name = "OpenFlow Interface"

    def __unicode__(self):
        return "Port %s on %s" % (self.port_num, self.switch)

class OpenFlowInterfaceSliver(resource_models.Sliver):
    class TooManySliversPerSlicePerInterface(Exception): pass
    
    @classmethod
    def check_save(cls, sender, **kwargs):
        """
        Make sure there is only one OpenFlowInterfaceSliver per
        slice per interface.
        """
        instance = kwargs["instance"]
        if kwargs["created"]:
            if OpenFlowInterfaceSliver.objects.filter(
                slice=instance.slice, resource=instance.resource).count() > 1:
                raise cls.TooManySliversPerSlicePerInterface()
signals.post_save.connect(OpenFlowInterfaceSliver.check_save,
                          OpenFlowInterfaceSliver)

class FlowSpaceRule(models.Model):
    sliver = models.ForeignKey(OpenFlowInterfaceSliver)

    dl_src_start = models.CharField('Link layer source address range start',
                                    max_length=17, default="*")
    dl_dst_start = models.CharField('Link layer destination address range start',
                                    max_length=17, default="*")
    dl_type_start = models.CharField('Link layer type range start',
                                     max_length=5, default="*")
    vlan_id_start = models.CharField('VLAN ID range start',
                                     max_length=4, default="*")
    nw_src_start = models.CharField('Network source address range start',
                                    max_length=18, default="*")
    nw_dst_start = models.CharField('Network destination address range start',
                                    max_length=18, default="*")
    nw_proto_start = models.CharField('Network protocol range start',
                                      max_length=3, default="*")
    tp_src_start = models.CharField('Transport source port range start',
                                    max_length=5, default="*")
    tp_dst_start = models.CharField('Transport destination port range start',
                                    max_length=5, default="*")
    
    dl_src_end = models.CharField('Link Layer Source Address Range End',
                                  max_length=17, default="*")
    dl_src_end = models.CharField('Link layer source address range end',
                                    max_length=17, default="*")
    dl_dst_end = models.CharField('Link layer destination address range end',
                                    max_length=17, default="*")
    dl_type_end = models.CharField('Link layer type range end',
                                     max_length=5, default="*")
    vlan_id_end = models.CharField('VLAN ID range end',
                                     max_length=4, default="*")
    nw_src_end = models.CharField('Network source address range end',
                                    max_length=18, default="*")
    nw_dst_end = models.CharField('Network destination address range end',
                                    max_length=18, default="*")
    nw_proto_end = models.CharField('Network protocol range end',
                                      max_length=3, default="*")
    tp_src_end = models.CharField('Transport source port range end',
                                    max_length=5, default="*")
    tp_dst_end = models.CharField('Transport destination port range end',
                                    max_length=5, default="*")

class GAPISlice(models.Model):
    slice_urn = models.CharField(max_length=500, primary_key=True)
    switches = models.ManyToManyField(OpenFlowSwitch)
    
