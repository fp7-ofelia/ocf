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
from django.contrib.auth.models import User
from django.http import Http404
from django.conf import settings
from django.db.models import signals
from expedient.common.messaging.models import DatedMessage

def as_is_slugify(value):
    return value

class OpenFlowSliceInfo(models.Model):
    slice = models.OneToOneField(slice_models.Slice)
    controller_url = models.CharField("URL of the slice's OpenFlow controller",
                                      max_length=100)
    # TODO: It is not a good idea to store the password in the clear.
    password = models.CharField(max_length=64)

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
        err = self.client.register_topology_callback(
            "%s%s" % (base_uri, reverse("openflow_open_xmlrpc")),
            "%s" % self.pk,
        )
        if err: return err

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
    
    def update_topology(self):
        '''
        Read the topology from the OM and FV, parse it, and store it.
        '''
        from expedient.common.utils import create_or_update
        
        # Get the active topology information from the AM
        links_raw = self.client.get_links()

        # optimize the parsing by storing information in vars
        current_links = self.get_raw_topology()
        
        current_switches = OpenFlowSwitch.objects.filter(aggregate=self)

        current_dpids = set(current_switches.values_list('datapath_id', flat=True))
        
        current_ifaces = set(
            OpenFlowInterface.objects.filter(
                aggregate=self).select_related(
                    "switch").values_list("switch__datapath_id", "port_num"))
        
        attrs_set = []
        ordered_active_links = []
        active_links = set()
        active_dpids = set()
        active_ifaces = set()
        for src_dpid, src_port, dst_dpid, dst_port, attrs in links_raw:
            link = (src_dpid, src_port, dst_dpid, dst_port)
            active_links.add(link)
            active_ifaces.add((src_dpid, src_port))
            active_ifaces.add((dst_dpid, dst_port))
            active_dpids.add(src_dpid)
            active_dpids.add(dst_dpid)
            attrs_set.append(attrs)
            ordered_active_links.append(link)

        new_links = active_links - current_links
        dead_links = current_links - active_links
        new_dpids = active_dpids - current_dpids
        dead_dpids = current_dpids - active_dpids
        new_ifaces = active_ifaces - current_ifaces
        dead_ifaces = current_ifaces - active_ifaces
        
        # create the new datapaths
        for dpid in new_dpids:
            create_or_update(
                OpenFlowSwitch,
                filter_attrs={
                    "datapath_id": dpid,
                    "aggregate":self,
                },
                new_attrs={
                    "name":dpid,
                    "available": True,
                    "status_change_timestamp": datetime.now(),
                }
            )
        
        # make old datapaths unavailable
        if dead_dpids:
            current_switches.filter(
                datapath_id__in=dead_dpids).update(
                    available=False, status_change_timestamp=datetime.now())

        # create new ifaces
        for iface in new_ifaces:
            create_or_update(
                OpenFlowInterface,
                filter_attrs=dict(
                    switch__datapath_id=iface[0],
                    port_num=iface[1],
                    aggregate=self,
                ),
                new_attrs=dict(
                    name="",
                    switch=OpenFlowSwitch.objects.get(datapath_id=iface[0]),
                    available=True,
                    status_change_timestamp=datetime.now(),
                ),
            )

        # make old ifaces unavailable
        # TODO: Is there a better way to w/o slugs?
        if dead_ifaces:
            dead_iface_slugs = ["%s_%s" % t for t in dead_ifaces]
            OpenFlowInterface.objects.filter(
                aggregate=self, slug__in=dead_iface_slugs).update(
                    available=False, status_change_timestamp=datetime.now())
        
        # create new links
        for link in new_links:
            create_or_update(
                OpenFlowConnection,
                filter_attrs=dict(
                    src_iface=OpenFlowInterface.objects.get(
                        switch__datapath_id=link[0],
                        port_num=link[1],
                    ),
                    dst_iface=OpenFlowInterface.objects.get(
                        switch__datapath_id=link[2],
                        port_num=link[3],
                    ),
                ),
            )
            
        # delete old links
        # TODO: Is there a better way to filter these?
        link_slugs = ["%s_%s_%s_%s" % link for link in dead_links]
        dead_cnxns = OpenFlowConnection.objects.filter(slug__in=link_slugs)
        dead_cnxns.delete()
        
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

    def remove_from_slice(self, slice, next):
        """
        Stop the slice at the aggregate, then remove aggregate from the slice.
        """
        # check if there's info already (aggregate in slice already)
        try:
            info = OpenFlowSliceInfo.objects.get(slice=slice)
        except OpenFlowSliceInfo.DoesNotExist:
            raise Http404("OpenFlowSlice information for slice does not exist.")
    
        try:
            self.stop_slice(slice)
        except:
            pass
        
        slice.aggregates.remove(self)
        
        return next
        
    @classmethod
    def get_aggregates_url(cls):
        return reverse("openflow_aggregate_home")

    @classmethod
    def get_create_url(cls):
        return reverse("openflow_aggregate_create")
    
    def start_slice(self, slice):
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

        return self.client.create_slice(
            slice.id, slice.project.name,
            slice.project.description,
            slice.name, slice.description,
            slice.openflowsliceinfo.controller_url,
            slice.owner.email,
            slice.openflowsliceinfo.password, sw_slivers)

    def stop_slice(self, slice):
        self.client.delete_slice(slice.id)
    
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
    
