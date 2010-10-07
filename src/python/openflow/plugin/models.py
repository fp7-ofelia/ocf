'''
Created on Apr 26, 2010

@author: jnaous
'''

import re
from django.db import models
from expedient.clearinghouse.resources import models as resource_models
from expedient.clearinghouse.slice import models as slice_models
from expedient.clearinghouse.aggregate import models as aggregate_models
from expedient.common.xmlrpc_serverproxy.models import PasswordXMLRPCServerProxy
from django.core.urlresolvers import reverse
from django.utils.datetime_safe import datetime
from autoslug.fields import AutoSlugField
from django.db.models import signals
from django.contrib.sites.models import Site
import logging
from expedient.common.utils import create_or_update, modelfields
from expedient.clearinghouse.slice.models import Slice
from django.db.models.aggregates import Count
from django.core.exceptions import ValidationError

logger = logging.getLogger("OpenflowModels")
parse_logger = logging.getLogger("OpenflowModelsParsing")

def as_is_slugify(value):
    return value

cntrlr_url_re = re.compile(r"^((tcp)|(ssl)):(\w+):(?P<port>\d+)$")
def validate_controller_url(value):
    def error():
        raise ValidationError(
            u"Invalid controller URL. The format is "
            "tcp:<hostname>:<port> or ssl:<hostname>:<port>. Port must "
            "be less than %s" % (2**16),
            code="invalid",
        )

    m = cntrlr_url_re.match(value)
    if m:
        port = m.group("port")
        if not port:
            error()
        else:
            port = int(port)
            if port > 2**16-1:
                error()
    else:
        error()
    
class OpenFlowSliceInfo(models.Model):
    slice = models.OneToOneField(slice_models.Slice)
    controller_url = models.CharField(
        "OpenFlow controller URL", max_length=100,
        validators=[validate_controller_url],
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

    def parse_switches(self, active_switches_raw):
        '''
        Update the set of available switches.
        '''
        # switches already in the DB.
        current_switches = OpenFlowSwitch.objects.filter(aggregate=self)
        
        switches = {}
        for switch_info in active_switches_raw:
            dpid, info = switch_info
            
            # The ports is a comma-separated set of values (see flowvisor API).
            portstrs = info["portList"].split(",")
            # turn into port numbers
            ports = [int(p) for p in portstrs if p != ""]
            
            switches[dpid] = ports
            
        create_or_update_switches(self, switches)            

    def parse_links(self, active_links_raw):
        '''
        Get the available links and update the network connections.
        '''
        active_cnxn_ids = []
        # Create any missing connections.
        for src_dpid, src_port, dst_dpid, dst_port, attrs in active_links_raw:
            parse_logger.debug("parsing link %s:%s - %s:%s" % (
                src_dpid, src_port, dst_dpid, dst_port))
            try:
                src_iface = OpenFlowInterface.objects.get(
                    switch__datapath_id=src_dpid,
                    port_num=src_port,
                )
            except OpenFlowInterface.DoesNotExist:
                logger.warn("Tried to add connection for non-existing source\
 interface %s:%s" % (src_dpid, src_port))
                continue

            try:
                dst_iface = OpenFlowInterface.objects.get(
                    switch__datapath_id=dst_dpid,
                    port_num=dst_port,
                )
            except OpenFlowInterface.DoesNotExist:
                logger.warn("Tried to add connection for non-existing dest\
 interface %s:%s" % (dst_dpid, dst_port))
                continue

            cnxn, created = OpenFlowConnection.objects.get_or_create(
                src_iface=src_iface,
                dst_iface=dst_iface,
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
            switches = self.client.proxy.get_switches()
            links = self.client.proxy.get_links()
        except:
            import traceback
            traceback.print_exc()
            raise
        self.parse_switches(switches)
        self.parse_links(links)
        
    def _get_slice_id(self, slice):
        """
        Get a slice id to use when creating slices at the OM.
        """
        return "%s_%s" % (Site.objects.get_current().domain, slice.id)
        
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
                        if f.name != "slivers":
                            v = getattr(fs, f.name)
                            fsd[f.name] = v if v is not None else "*"
                    d['flowspace'].append(fsd)
            sw_slivers.append(d)
            
        return sw_slivers

    ###################################################################
    # Following are overrides from aggregate_models.Aggregate         #
    ###################################################################
    
    @classmethod
    def get_url_name_prefix(cls):
        return "openflow"
    
    def check_status(self):
        return self.available and self.client.is_available()

    def start_slice(self, slice):
        super(OpenFlowAggregate, self).start_slice(slice)
        sw_slivers = self._get_slivers(slice)
        try:
            return self.client.proxy.create_slice(
                self._get_slice_id(slice), slice.project.name,
                slice.project.description,
                slice.name, slice.description,
                slice.openflowsliceinfo.controller_url,
                slice.owner.email,
                slice.openflowsliceinfo.password, sw_slivers)
        except Exception as ret_exception:
            import traceback
            logger.info("XML RPC call to aggregate %s failed." % self.name)
            logger.error(traceback.format_exc())
            raise

    def stop_slice(self, slice):
        super(OpenFlowAggregate, self).stop_slice(slice)
        try:
            self.client.proxy.delete_slice(self._get_slice_id(slice))
        except Exception as e:
            import traceback
            logger.info("XML RPC call failed to aggregate %s" % self.name)
            traceback.print_exc()
            raise
    
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

class NonOpenFlowConnection(models.Model):
    """Connection to/from an OpenFlow Interface to a non-OpenFlow Resource"""
    
    of_iface = models.ForeignKey(
        "OpenFlowInterface",
        verbose_name="OpenFlow Interface",
        related_name="nonopenflow_connections")
    
    resource = models.ForeignKey(
        resource_models.Resource,
        verbose_name="Non-OpenFlow Resource",
        related_name="openflow_connections")
    
    class Meta:
        unique_together=(("of_iface", "resource"),)
    
    def __unicode__(self):
        return "to/from %s from/to %s" % (
            self.of_iface, self.resource.as_leaf_class())

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
        return "Aggregate %s: Port %s on %s" % (
            self.aggregate.name, self.port_num, self.switch)

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
    slivers = models.ManyToManyField(
        OpenFlowInterfaceSliver,
        help_text="Select the interfaces to apply the flowspace rule to.",
    )

    dl_src_start = modelfields.MACAddressField(
        'Link layer source address range start', null=True, blank=True)
    dl_dst_start = modelfields.MACAddressField(
        'Link layer destination address range start', null=True, blank=True)
    dl_type_start = modelfields.LimitedIntegerField(
        'Link layer type range start',
        max_value=2**16-1, min_value=0, blank=True, null=True)
    vlan_id_start = modelfields.LimitedIntegerField(
        'VLAN ID range start',
        max_value=2**12-1, min_value=0, blank=True, null=True)
    nw_src_start = models.IPAddressField(
        'Network source address range start', blank=True, null=True)
    nw_dst_start = models.IPAddressField(
        'Network destination address range start', blank=True, null=True)
    nw_proto_start = modelfields.LimitedIntegerField(
        'Network protocol range start',
        max_value=2**8-1, min_value=0, blank=True, null=True)
    tp_src_start = modelfields.LimitedIntegerField(
        'Transport source port range start',
        max_value=2**16-1, min_value=0, blank=True, null=True)
    tp_dst_start = modelfields.LimitedIntegerField(
        'Transport destination port range start',
        max_value=2**16-1, min_value=0, blank=True, null=True)
    
    dl_src_end = modelfields.MACAddressField(
        'Link layer source address range end', null=True, blank=True)
    dl_dst_end = modelfields.MACAddressField(
        'Link layer destination address range end', null=True, blank=True)
    dl_type_end = modelfields.LimitedIntegerField(
        'Link layer type range end',
        max_value=2**16-1, min_value=0, blank=True, null=True)
    vlan_id_end = modelfields.LimitedIntegerField(
        'VLAN ID range end',
        max_value=2**12-1, min_value=0, blank=True, null=True)
    nw_src_end = models.IPAddressField(
        'Network source address range end', blank=True, null=True)
    nw_dst_end = models.IPAddressField(
        'Network destination address range end', blank=True, null=True)
    nw_proto_end = modelfields.LimitedIntegerField(
        'Network protocol range end',
        max_value=2**8-1, min_value=0, blank=True, null=True)
    tp_src_end = modelfields.LimitedIntegerField(
        'Transport source port range end',
        max_value=2**16-1, min_value=0, blank=True, null=True)
    tp_dst_end = modelfields.LimitedIntegerField(
        'Transport destination port range end',
        max_value=2**16-1, min_value=0, blank=True, null=True)

def create_or_update_switches(aggregate, switches):
    """Create or update the switch in aggregate C{aggregate} with switches in C{switches}.
    
    C{switches} is a dict mapping datapath ids to list of ports.
    
    """

    active_switch_ids = []
    active_iface_ids = []
    for dpid, ports in switches.items():
        switch, _ = create_or_update(
            OpenFlowSwitch,
            filter_attrs=dict(
                datapath_id=dpid,
            ),
            new_attrs=dict(
                aggregate=aggregate,
                name=dpid,
                available=True,
                status_change_timestamp=datetime.now(), 
            )
        )
        active_switch_ids.append(switch.id)
        
        for port in ports:
            # update the interfaces for this switch
            iface, _ = create_or_update(
                OpenFlowInterface,
                filter_attrs=dict(
                    switch__datapath_id=dpid,
                    port_num=port,
                ),
                new_attrs=dict(
                    aggregate=aggregate,
                    name="Port %s" % port,
                    switch=switch,
                    available=True,
                    status_change_timestamp=datetime.now(), 
                ),
            )
            active_iface_ids.append(iface.id)
            
    # make all inactive switches and interfaces unavailable.
    OpenFlowInterface.objects.filter(
        aggregate=aggregate).exclude(id__in=active_iface_ids).update(
            available=False, status_change_timestamp=datetime.now())
        
    OpenFlowSwitch.objects.filter(
        aggregate=aggregate).exclude(id__in=active_switch_ids).update(
            available=False, status_change_timestamp=datetime.now())
        
# when a slice is deleted, make sure all its flowspace is deleted too
def delete_empty_flowspace(sender, **kwargs):
    empty_fs = FlowSpaceRule.objects.annotate(
        num_slivers=Count("slivers")).filter(
            num_slivers=0)
    logger.debug("Deleting %s flowspaces" % empty_fs.count())
    empty_fs.delete()

def check_fs_change(sender, **kwargs):
    if kwargs["action"] == "post_remove":
        logger.debug("m2m changed with %s" % kwargs["action"])
        delete_empty_flowspace(sender, **kwargs)

signals.post_delete.connect(delete_empty_flowspace, Slice)        
signals.post_delete.connect(delete_empty_flowspace, OpenFlowInterfaceSliver)        
signals.m2m_changed.connect(
    check_fs_change, FlowSpaceRule.slivers.through)        

