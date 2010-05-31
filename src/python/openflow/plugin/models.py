'''
Created on Apr 26, 2010

@author: jnaous
'''

from django.db import models
from expedient.clearinghouse.resources import models as resource_models
from expedient.clearinghouse.aggregate import models as aggregate_models
from expedient.common.xmlrpc_serverproxy.models import PasswordXMLRPCServerProxy
from django.core.urlresolvers import reverse
from django.utils.datetime_safe import datetime
from autoslug.fields import AutoSlugField
from django.contrib.contenttypes.models import ContentType

def as_is_slugify(value):
    return value

class OpenFlowUserInfo(aggregate_models.AggregateUserInfo):
    signed_license = models.BooleanField("Signed usage agreement?",
                                         default=False)
    
class OpenFlowSliceInfo(aggregate_models.AggregateSliceInfo):
    controller_url = models.CharField("URL of the slice's OpenFlow controller",
                                      max_length=100)

class OpenFlowAggregate(aggregate_models.Aggregate):
    client = models.OneToOneField(PasswordXMLRPCServerProxy)
    usage_agreement = models.TextField()
    
    class Meta:
        verbose_name = "OpenFlow Aggregate"
        
    def setup_new_aggregate(self, hostname):
        self.client.install_trusted_ca()
        err = self.client.change_password()
        if err: return err
        
        err = self.client.register_topology_callback(
            "https://%s%s" % (hostname, reverse("openflow_open_xmlrpc")),
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

#        print "******** Update topology"

#        print "Link raw:"
#        pprint(links_raw, indent=4)
        
        # optimize the parsing by storing information in vars
        current_links = self.get_raw_topology()
#        print "Current links:"
#        pprint (current_links, indent=4)
        
        current_switches = OpenFlowSwitch.objects.filter(aggregate=self)
#        print "Current switches:"
#        pprint (current_switches, indent=4)

        current_dpids = set(current_switches.values_list('datapath_id', flat=True))
#        print "Current dpids:"
#        pprint (current_dpids, indent=4)
        
        current_ifaces = set(
            OpenFlowInterface.objects.filter(
                aggregate=self).select_related(
                    "switch").values_list("switch__datapath_id", "port_num"))
#        print "Current ifaces:"
#        pprint (current_ifaces, indent=4)
        
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

#        print "active links:"
#        pprint (active_links, indent=4)
#        print "active ifaces:"
#        pprint (active_ifaces, indent=4)
#        print "active dpids:"
#        pprint (active_dpids, indent=4)
        
        new_links = active_links - current_links
        dead_links = current_links - active_links
        new_dpids = active_dpids - current_dpids
        dead_dpids = current_dpids - active_dpids
        new_ifaces = active_ifaces - current_ifaces
        dead_ifaces = current_ifaces - active_ifaces
        
#        print "New_links:"
#        pprint (new_links, indent=4)
#        print "New_dpids:"
#        pprint (new_dpids, indent=4)
#        print "New_ifaces:"
#        pprint (new_ifaces, indent=4)
        
#        print "dead_links:"
#        pprint (dead_links, indent=4)
#        print "dead_dpids:"
#        pprint (dead_dpids, indent=4)
#        print "dead_ifaces:"
#        pprint (dead_ifaces, indent=4)
        
        # create the new datapaths
        for dpid in new_dpids:
#            print "Adding dpid %s" % dpid
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
        
#        print "After adding: %s" % OpenFlowSwitch.objects.filter(
#            aggregate=self, available=True)
        
        # make old datapaths unavailable
        if dead_dpids:
            current_switches.filter(
                datapath_id__in=dead_dpids).update(
                    available=False, status_change_timestamp=datetime.now())

#        print "After deleting: %s" % OpenFlowSwitch.objects.filter(
#            aggregate=self, available=True)
            
        # create new ifaces
        for iface in new_ifaces:
#            print "Adding iface %s_%s" % iface
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

#        print "After adding: %s" % OpenFlowInterface.objects.filter(aggregate=self)
        
        # make old ifaces unavailable
        # TODO: Is there a better way to w/o slugs?
        if dead_ifaces:
            dead_iface_slugs = ["%s_%s" % t for t in dead_ifaces]
            OpenFlowInterface.objects.filter(
                aggregate=self, slug__in=dead_iface_slugs).update(
                    available=False, status_change_timestamp=datetime.now())

#        print "After deleting: %s" % OpenFlowInterface.objects.filter(aggregate=self)
        
        # create new links
        for link in new_links:
            OpenFlowConnection.objects.create(
                src_iface=OpenFlowInterface.objects.get(
                    switch__datapath_id=link[0],
                    port_num=link[1],
                ),
                dst_iface=OpenFlowInterface.objects.get(
                    switch__datapath_id=link[2],
                    port_num=link[3],
                ),
            )
            
        # delete old links
        # TODO: Is there a better way to filter these?
        link_slugs = ["%s_%s_%s_%s" % link for link in dead_links]
        dead_cnxns = OpenFlowConnection.objects.filter(slug__in=link_slugs)
        if dead_cnxns.count < len(set(link_slugs)):
            print "WARNING: Some connections that were thought to be dead" +\
                " not found in DB."
        dead_cnxns.delete()

    def update_slice(self, slice):
        slice.create_slice(slice)
        
    def create_slice(self, user, slice, slice_password):
        # get all the slivers that are in this aggregate
        sw_slivers_qs = slice.sliver_set.filter(
            resource__aggregate=self,
            resource__content_type=ContentType.objects.get_for_model(
                OpenFlowSwitch)
        ).select_related(
            'resource__openflowswitch',
            'flowspacerule_set',
        )
        
        sw_slivers = []
        for s in sw_slivers_qs:
            d = {}
            d['datapath_id'] = s.resource.openflowswitch.datapath_id
            d['flowspace'] = []
            for fs in s.flowspacerule_set.all():
                fsd = {}
                for f in fs._meta.fields:
                    fsd[f.name] = getattr(fs, f.name)
                d['flowspace'].append(fsd)
            sw_slivers.append(d)
        
        return self.client.create_slice(
            slice.id, slice.project.name, slice.project.description,
            slice.name, slice.description, 
            slice.aggregatesliceinfo.controller_url,
            user.email, slice_password, sw_slivers)
        
    def delete_slice(self, slice, server=None):
        return self.client.delete_slice(slice.id)
    
    def check_status(self):
        return self.available and self.client.is_available()

class OpenFlowSwitch(resource_models.Resource):
    datapath_id = models.CharField(max_length=100, unique=True)
    
    def __unicode__(self):
        return "OF Switch %s (%016x)" % (self.datapath_id, self.datapath_id)
#    class Extend:
#        replacements={
#            "sliver_class": "OpenFlowSwitchSliver",
#        }

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
    )
    
    def __unicode__(self):
        return "OF Connection: %s" % self.slug

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
    )

    def __unicode__(self):
        return "OF Interface: %s" % self.slug

#    class Extend:
#        replacements={
#            "sliver_class": "OpenFlowInterfaceSliver",
#        }

#class OpenFlowSwitchSliver(resource_models.Sliver):
#    class Extend:
#        replacements={
#            "resource_class": OpenFlowSwitch,
#        }
#
#class OpenFlowInterfaceSliver(resource_models.Sliver):
#    class Extend:
#        replacements={
#            "resource_class": OpenFlowInterface,
#        }

class FlowSpaceRule(models.Model):
    switch_sliver = models.ForeignKey(resource_models.Sliver)

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

class GAPISlice(models.Model):
    slice_urn = models.CharField(max_length=500, primary_key=True)
    switches = models.ManyToManyField(OpenFlowSwitch)
    
