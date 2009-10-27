from django.forms.formsets import BaseFormSet
from django.db import models
from django.db.models import permalink
from django.forms import ModelForm, Form
import django.forms as forms
from django.contrib.auth.models import User
from django.forms.fields import IntegerField
import egeni_api
import plc_api

class AggregateManager(models.Model):
    '''An Aggregate Manager'''
    
    TYPE_OF = 'OF'
    TYPE_PL = 'PL'
    
    AM_TYPE_CHOICES={TYPE_OF: 'E-GENI Aggregate Manager',
                     TYPE_PL: 'PlanetLab Aggregate Manager',
                     }

    # @ivar name: The name of the aggregate manager. Must be unique 
    name = models.CharField(max_length=200, unique=True)
    
    # @ivar url: Location where the aggregate manager can be reached
    url = models.URLField('Aggregate Manager URL', unique=True, verify_exists=False)
    
    # @ivar type: Aggregate Type: OF or PL
    type = models.CharField(max_length=20, choices=AM_TYPE_CHOICES.items())
    
    # @ivar remote_node_set: nodes that this AM connects to that are not under its control
    remote_node_set = models.ManyToManyField("Node", related_name='remote_am_set',
                                             blank=True, null=True)

    # @ivar local_node_set: nodes that this AM connects to that are under its control
    
    # @ivar connected_node_set: nodes that this AM connects to that are or are not under its control
    connected_node_set = models.ManyToManyField("Node",
                                                related_name='connected_am_set',
                                                blank=True, null=True)

    def get_absolute_url(self):
        return ('am_detail', [str(self.id)])
    get_absolute_url = permalink(get_absolute_url)

    def __unicode__(self):
        return AggregateManager.AM_TYPE_CHOICES[self.type] + ' ' + self.name + ' at ' + self.url
    
    def get_local_nodes(self):
        return self.local_node_set.all()
    
    def updateRSpec(self):
        print "Update RSpec Type %s" % self.type
        if self.type == AggregateManager.TYPE_OF:
            return egeni_api.update_rspec(self)
        else:
            return plc_api.update_rspec(self)
        
    def makeReservation(self):
        '''Request a reservation and return a message on success or failure'''
        
        if self.type == AggregateManager.TYPE_OF:
            error = egeni_api.reserve_slice(self)
        else:
            error = plc_api.reserve_slice(self)
            
        if error:
            # parse the error xml
            pass

class Node(models.Model):
    '''
    Anything that has interfaces. Can be a switch or a host or a stub.
    '''
    
    TYPE_OF = 'OF';
    TYPE_PL = 'PL';

    nodeId = models.CharField(max_length=200, primary_key=True)
    type = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    
    is_remote = models.BooleanField()
    
    # @ivar remoteURL: indicates URL of controller
    remoteURL = models.URLField("Controller URL", verify_exists=False)
    
    # @ivar aggMgr: The AM that created the node or controls it
    aggMgr = models.ForeignKey(AggregateManager,
                               related_name='local_node_set',
                               blank=True,
                               null=True,
                               )
    
    # @ivar img_url: URL of the image used for when the node is drawn
    img_url = models.CharField(max_length=200)
    
    def __unicode__(self):
        return "Node %s" % self.nodeId
    
    def get_absolute_url(self):
        return('node_detail', [str(self.aggMgr.id), str(self.nodeId)])
    get_absolute_url = permalink(get_absolute_url)

class Interface(models.Model):
    '''Describes a port and its connection'''
    portNum = models.PositiveSmallIntegerField(blank=True, null=True)
    ownerNode = models.ForeignKey(Node)
    remoteIfaces = models.ManyToManyField('self', symmetrical=False, through="Link")
    
    # PlanetLab additional things
    max_kbyte = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    address = models.IPAddressField(blank=True, null=True)
    type = models.CharField(max_length=200, blank=True, null=True)
    init_params = models.TextField(blank=True, null=True)
    ip_spoof = models.BooleanField(blank=True, null=True)
    max_rate = models.IntegerField(blank=True, null=True)
    min_rate = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return "Interface "+self.portNum+" of node "+self.ownerNode.nodeId
        
class Link(models.Model):
    '''
    Stores information about the unidirectional connection between
    two nodes.
    '''
    
    src = models.ForeignKey(Interface, related_name='src_link_set')
    dst = models.ForeignKey(Interface, related_name='dst_link_set')
    
    # PlanetLab additional fields
    bandwidth = models.IntegerField(blank=True, null=True)
    max_allocation = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=200, blank=True, null=True)

    def __unicode__(self):
        return "Link from " + self.src.__unicode__() \
                + " to " + self.dst.__unicode__()

class Slice(models.Model):
    '''This is created by a user (the owner) and contains
    multiple reservations from across different aggregate managers'''
    
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=200, unique=True)
    controller_url = models.URLField('Slice Controller URL', verify_exists=False)
    nodes = models.ManyToManyField(Node, through="NodeSliceStatus")
    links = models.ManyToManyField(Link, through="LinkSliceStatus")
    committed = models.BooleanField()

    # nodes that this slice has seen. We use this to store a user's
    # x,y settings and other per-slice per-node settings
    gui_nodes = models.ManyToManyField(Node, through="NodeSliceGUI", related_name='gui_slice_set')
    
    # PlanetLab additional fields
    start_date = models.DateField("Start date", blank=True, null=True)
    start_time = models.TimeField("Start time", blank=True, null=True)
    end_date = models.DateField("End date", blank=True, null=True)
    end_time = models.TimeField("End time", blank=True, null=True)
    
    def get_utc_start_time(self):
        # TODO
        return "xxxx"
    
    def get_utc_duration(self):
        # TODO
        return "yyyy"

    def get_absolute_url(self):
        return('slice_flash_detail', [str(self.id)])
    get_absolute_url = permalink(get_absolute_url)
    
    def has_interface(self, iface):
        '''
        return true if the interface is a src or dst in any link in
        this slice
        '''
        return (self.links.filter(src=iface).count()
                + self.links.filter(src=iface).count()) > 0
    
class NodeSliceStatus(models.Model):
    '''
    Tracks information about the node in the slice.
    '''
    
    slice = models.ForeignKey(Slice)
    node = models.ForeignKey(Node)

    reserved = models.BooleanField()
    removed = models.BooleanField()
    has_error = models.BooleanField()
    
    # PlanetLab additional fields
    init_params = models.TextField(blank=True, null=True)
    cpu_min = models.IntegerField(blank=True, null=True)
    cpu_share = models.IntegerField(blank=True, null=True)
    cpu_pct = models.IntegerField(blank=True, null=True)
    disk_max =  models.IntegerField(blank=True, null=True)
    start_date = models.DateField("Start date", blank=True, null=True)
    start_time = models.TimeField("Start time", blank=True, null=True)
    end_date = models.DateField("End date", blank=True, null=True)
    end_time = models.TimeField("End time", blank=True, null=True)

    def get_utc_start_time(self):
        # TODO
        return "xxxx"
    
    def get_utc_duration(self):
        # TODO
        return "yyyy"

class NodeSliceGUI(models.Model):
    '''
    Tracks information about the nodes in the GUI when
    shown for this slice.
    '''
    
    slice = models.ForeignKey(Slice)
    node = models.ForeignKey(Node)
    
    x = models.FloatField()
    y = models.FloatField()

class LinkSliceStatus(models.Model):
    '''
    Tracks information about the link in the slice.
    '''
    
    slice = models.ForeignKey(Slice)
    link = models.ForeignKey(Link)
    
    reserved = models.BooleanField()
    removed = models.BooleanField()
    has_error = models.BooleanField()
    
    # PlanetLab additional fields
    start_date = models.DateField("Start date", blank=True, null=True)
    start_time = models.TimeField("Start time", blank=True, null=True)
    end_date = models.DateField("End date", blank=True, null=True)
    end_time = models.TimeField("End time", blank=True, null=True)
    init_params = models.TextField(blank=True, null=True)    

    def get_utc_start_time(self):
        # TODO
        return "xxxx"
    
    def get_utc_duration(self):
        # TODO
        return "yyyy"
    
class SliceForm(ModelForm):
    class Meta:
        model = Slice
        fields = ('name', 'controller_url')

class FlowSpace(models.Model):
    policy = models.CharField(max_length=2)
    dl_src = models.CharField(max_length=17)
    dl_dst = models.CharField(max_length=17)
    dl_type = models.CharField(max_length=5)
    vlan_id = models.CharField(max_length=4)
    nw_src = models.CharField(max_length=18)
    nw_dst = models.CharField(max_length=18)
    nw_proto = models.CharField(max_length=3)
    tp_src = models.CharField(max_length=5)
    tp_dst = models.CharField(max_length=5)
    slice = models.ForeignKey(Slice, null=True, blank=True)
    
    def __unicode__(self):
        return("Port: "+self.interface.portNum+", dl_src: "+self.dl_src
               +", dl_dst: "+self.dl_dst+", dl_type: "+self.dl_type
               +", vlan_id: "+self.vlan_id+", nw_src: "+self.nw_src
               +", nw_dst: "+self.nw_dst+", nw_proto: "+self.nw_proto
               +", tp_src: "+self.tp_src+", tp_dst: "+self.tp_dst)

class FlowSpaceForm(ModelForm):
    # TODO: add validation using policy manager
    class Meta:
        model=FlowSpace
        exclude = ('slice')
