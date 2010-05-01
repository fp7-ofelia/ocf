'''
Created on Apr 26, 2010

@author: jnaous
'''

from django.db import models
from django.db.models.query import Q
from clearinghouse.resources import models as resource_models
from clearinghouse.aggregate import models as aggregate_models
from clearinghouse.xmlrpc_serverproxy.models import PasswordXMLRPCServerProxy
from django.core.urlresolvers import reverse
from django.utils.datetime_safe import datetime
from autoslug.fields import AutoSlugField
import traceback

class OpenFlowAdminInfo(aggregate_models.AggregateAdminInfo):
    class Extend:
        replacements = {
            "aggregate_class": "OpenFlowAggregate",
        }

class OpenFlowUserInfo(aggregate_models.AggregateUserInfo):
    class Extend:
        replacements = {
            "aggregate_class": "OpenFlowAggregate",
        }

class OpenFlowSliceInfo(aggregate_models.AggregateSliceInfo):
    controller_url = models.CharField("URL of the slice's OpenFlow controller",
                                      max_length=100)
    class Extend:
        replacements = {
            "aggregate_class": "OpenFlowAggregate",
        }

class OpenFlowProjectInfo(aggregate_models.AggregateProjectInfo):
    class Extend:
        replacements = {
            "aggregate_class": "OpenFlowAggregate",
        }

class OpenFlowAggregate(aggregate_models.Aggregate):
    client = models.OneToOneField(PasswordXMLRPCServerProxy)
    
    class Extend:
        replacements= {
            'admin_info_class': OpenFlowAdminInfo,
            'user_info_class': OpenFlowUserInfo,
            'slice_info_class': OpenFlowSliceInfo,
            'project_info_class': OpenFlowProjectInfo,
        }
        
    class Meta:
        verbose_name = "OpenFlow Aggregate"
        
    def setup_new_aggregate(self, hostname):
        self.client.change_password()
        self.client.register_topology_callback(
            "https://%s/openflow/xmlrpc/" % hostname,
            "%s" % self.pk,
        )
        
    def get_raw_topology(self):
        '''
        Get the topology for this aggregate as a set of links.
        '''
        # Create a filter that selects any connection that connects a switch
        # in this aggregate
        filter = Q(src_iface__switch__aggregate=self) | \
            Q(dst_iface__switch__aggregate=self)
            
        # optimize so we don't hit the DB multiple times
        qs = OpenFlowConnection.objects.filter(filter)
        qs.select_related("src_iface","src_iface__switch",
                          "dst_iface","dst_iface__switch")
        
        # Dump the links into tuples
        links = set()
        for cnxn in qs:
                links.add((cnxn.src_iface.switch.datapath_id,
                           cnxn.src_iface.port_num,
                           cnxn.dst_iface.switch.datapath_id,
                           cnxn.dst_iface.port_num))
        return links
    
    def update_topology(self):
        '''
        Read the topology from the OM and FV, parse it, and store it.
        '''
        from clearinghouse.utils import create_or_update
        def unslugify(slug):
            return tuple(map(int, slug.split("_")))
        
        # Get the active topology information from the AM
        links_raw = self.client.get_links()
#        switches_raw = self.client.get_switches()
        
        # optimize the parsing by storing information in vars
        current_links = self.get_raw_topology()
        current_switches = self.openflowswitch_set.all()
        current_dpids = set(current_switches.values_list('datapath_id', flat=True))
#        current_ifaces = self.openflowinterface_set.all().values_list('switch','port_num')
#        current_ifaces = map(
#            lambda(a,b): (current_switches.get(pk=a).datapath_id, b),
#            current_ifaces,
#        )
        current_ifaces = map(
            unslugify,
            self.openflowinterface_set.all().values_list("slug", flat=True))
        
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
            OpenFlowSwitch.objects.create(
                name=dpid,
                datapath_id=dpid,
                aggregate=self,
                available=True,
                status_change_timestamp=datetime.now(),
            )
        
        # make old datapaths unavailable
        self.openflowswitch_set.filter(
            datapath_id__in=dead_dpids).update(
                available=False, status_change_timestamp=datetime.now())
            
        # create new ifaces
        for iface in new_ifaces:
            OpenFlowInterface.objects.create(
                name="",
                port_num=iface[1],
                switch=OpenFlowSwitch.objects.get(datapath_id=iface[0]),
            )
        
        # make old ifaces unavailable
        dead_iface_slugs = ["%s_%s" % t for t in dead_ifaces]
        OpenFlowInterface.objects.filter(
            slug__in=dead_iface_slugs).update(
                available=False, status_change_timestamp=datetime.now())
        
        # create new links
        for link in new_links:
            OpenFlowConnection.objects.create(
                src_iface=OpenFlowInterface.objects.get(slug="%s_%s" % link[0:1]),
                dst_iface=OpenFlowInterface.objects.get(slug="%s_%s" % link[2:3]),
            )
            
        # delete old links
        for link in dead_links:
            try:
                c = OpenFlowConnection.objects.get(slug="%s_%s_%s_%s" % link)
            except OpenFlowConnection.DoesNotExist:
                print "WARNING: Connection that was thought to be dead not found in DB."
                traceback.print_exc()
            else:
                c.delete()

    def update_slice(self, slice):
        slice.reserve_slice(slice)
        
    def create_slice(self, user, slice, slice_password):
        # get all the slivers that are in this aggregate
        sw_slivers_qs = \
            slice.openflowswitchsliver_set.filter(switch__aggregate=self)
        sw_slivers_qs.select_related('resource', 'flowspacerule_set')
        
        sw_slivers = []
        for s in sw_slivers_qs:
            d = {}
            d['datapath_id'] = s.resource.datapath_id
            d['flowspace'] = []
            for fs in s.flowspacerule_set:
                fsd = {}
                for f in fs._meta.fields:
                    fsd[f.name] = getattr(fs, f.name)
                d['flowspace'].append(fsd)
            sw_slivers.append(d)
        
        return self.client.reserve_slice(
            slice.id, slice.project.name, slice.project.description,
            slice.name, slice.description, 
            slice.openflowsliceinfo.controller_url,
            user.email, slice_password, sw_slivers)
        
    def delete_slice(self, slice, server=None):
        return self.client.delete_slice(slice.id)
    
    def check_status(self):
        return self.available # TODO: and self.client.is_available()

class OpenFlowSwitch(resource_models.Resource):
    datapath_id = models.IntegerField(unique=True)
    
    class Extend:
        replacements={
            "sliver_class": "OpenFlowSwitchSliver",
        }

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
        )
    )

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
            instance.switch.datapath_id, instance.port_num))

    class Extend:
        replacements={
            "sliver_class": "OpenFlowInterfaceSliver",
        }

class OpenFlowSwitchSliver(resource_models.Sliver):
    class Extend:
        replacements={
            "resource_class": OpenFlowSwitch,
        }

class OpenFlowInterfaceSliver(resource_models.Sliver):
    class Extend:
        replacements={
            "resource_class": OpenFlowInterface,
        }

class FlowSpaceRule(models.Model):
    TYPE_ALLOW = 1
    TYPE_DENY  = -1
    TYPE_RD_ONLY = 0
    
    POLICY_TYPE_CHOICES={TYPE_ALLOW: 'Allow',
                         TYPE_DENY: 'Deny',
                         TYPE_RD_ONLY: 'Read Only',
                         }
    
    DIR_IN = 'ingress'
    DIR_OUT = 'egress'
    DIR_BI = 'bidirectional'
    DIRECTION_CHOICES={DIR_IN: 'Ingress',
                       DIR_OUT: 'Egress',
                       DIR_BI: 'Bidirectional',
                       }

    switch_sliver = models.ForeignKey(OpenFlowSwitchSliver)

    direction = models.CharField(max_length=20,
                                 choices=DIRECTION_CHOICES.items(),
                                 default=DIR_BI)
    policy = models.SmallIntegerField(choices=POLICY_TYPE_CHOICES.items(),
                                      default=TYPE_ALLOW)
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
    port_num_start = models.CharField('Switch port number range start',
                                      max_length=4, default="*")
    
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
    port_num_end = models.CharField('Switch port number range end',
                                      max_length=4, default="*")
    
    def __unicode__(self):
        return("Policy: "+FlowSpaceRule.POLICY_TYPE_CHOICES[self.policy]
               +", port: " +self.interface.port_num+", dl_src: "+self.dl_src
               +", dl_dst: "+self.dl_dst+", dl_type: "+self.dl_type
               +", vlan_id: "+self.vlan_id+", nw_src: "+self.nw_src
               +", nw_dst: "+self.nw_dst+", nw_proto: "+self.nw_proto
               +", tp_src: "+self.tp_src+", tp_dst: "+self.tp_dst)
