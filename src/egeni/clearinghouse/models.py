from django.db import models
from geniLight.geniLight_client import GeniLightClient
from xml.dom import minidom
from xml import xpath
from django.db.models import permalink
from django.forms import ModelForm
from django.contrib.auth.models import User

test_xml = """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<tns:RSpec xmlns:tns="http://yuba.stanford.edu/geniLight/rspec" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://yuba.stanford.edu/geniLight/rspec http://yuba.stanford.edu/geniLight/rspec.xsd">

  <tns:version>1.0</tns:version>

  <tns:remoteEntry>
    <tns:remoteURL>pl.princeton.edu:2134</tns:remoteURL>
    <tns:remoteType>PLNode</tns:remoteType>
    <tns:node>
      <tns:nodeId>9dsafj</tns:nodeId>
      <tns:interfaceEntry>
        <tns:port>0</tns:port>
        <tns:remoteNodeId>2580021f7cae400</tns:remoteNodeId>
        <tns:remotePort>1</tns:remotePort>
      </tns:interfaceEntry>
    </tns:node>
  </tns:remoteEntry>

  <tns:switchEntry>
    <tns:node>
      <tns:nodeId>640021f7cae400</tns:nodeId>
      <tns:interfaceEntry>
        <tns:port>26</tns:port>
        <tns:remoteNodeId>2580021f7cae400</tns:remoteNodeId>
        <tns:remotePort>46</tns:remotePort>
        <tns:remoteNodeId>1f40021f7cae400</tns:remoteNodeId>
        <tns:remotePort>43</tns:remotePort>
      </tns:interfaceEntry>
      <tns:interfaceEntry>
        <tns:port>28</tns:port>
          <tns:flowSpaceEntry>
              <tns:policy>0</tns:policy>
              <tns:dl_type>2</tns:dl_type>
              <tns:tp_dst>423</tns:tp_dst>
          </tns:flowSpaceEntry>
          <tns:flowSpaceEntry>
              <tns:policy>0</tns:policy>
              <tns:dl_type>2</tns:dl_type>
              <tns:tp_dst>423</tns:tp_dst>
          </tns:flowSpaceEntry>
      </tns:interfaceEntry>
    </tns:node>
  </tns:switchEntry>

  <tns:switchEntry>
    <tns:node>
      <tns:nodeId>2580021f7cae400</tns:nodeId>
      <tns:interfaceEntry>
        <tns:port>46</tns:port>
        <tns:remoteNodeId>640021f7cae400</tns:remoteNodeId>
        <tns:remotePort>26</tns:remotePort>
        <tns:remoteNodeId>1f40021f7cae400</tns:remoteNodeId>
        <tns:remotePort>43</tns:remotePort>
      </tns:interfaceEntry>
      <tns:interfaceEntry>
        <tns:port>48</tns:port>
      </tns:interfaceEntry>
      <tns:interfaceEntry>
        <tns:port>1</tns:port>
        <tns:remoteNodeId>9dsafj</tns:remoteNodeId>
        <tns:remotePort>0</tns:remotePort>
      </tns:interfaceEntry>
    </tns:node>
  </tns:switchEntry>

  <tns:switchEntry>
    <tns:node>
      <tns:nodeId>1f40021f7cae400</tns:nodeId>
      <tns:interfaceEntry>
        <tns:port>41</tns:port>
      </tns:interfaceEntry>
      <tns:interfaceEntry>
        <tns:port>43</tns:port>
        <tns:remoteNodeId>640021f7cae400</tns:remoteNodeId>
        <tns:remotePort>26</tns:remotePort>
        <tns:remoteNodeId>2580021f7cae400</tns:remoteNodeId>
        <tns:remotePort>46</tns:remotePort>
      </tns:interfaceEntry>
      <tns:interfaceEntry>
        <tns:port>44</tns:port>
      </tns:interfaceEntry>
    </tns:node>
  </tns:switchEntry>

  <tns:switchEntry>
    <tns:node>
      <tns:nodeId>12c0021f7cae400</tns:nodeId>
      <tns:interfaceEntry>
        <tns:port>33</tns:port>
      </tns:interfaceEntry>
      <tns:interfaceEntry>
        <tns:port>35</tns:port>
      </tns:interfaceEntry>
      <tns:interfaceEntry>
        <tns:port>36</tns:port>
      </tns:interfaceEntry>
    </tns:node>
  </tns:switchEntry>

  <tns:switchEntry>
    <tns:node>
      <tns:nodeId>c80021f7cae400</tns:nodeId>
    </tns:node>
  </tns:switchEntry>

  <tns:switchEntry>
    <tns:node>
      <tns:nodeId>123456789ab</tns:nodeId>
      <tns:interfaceEntry>
        <tns:port>0</tns:port>
      </tns:interfaceEntry>
    </tns:node>
  </tns:switchEntry>

</tns:RSpec>
"""

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
    
    def get_absolute_url(self):
        return ('am_detail', [str(self.id)])
    get_absolute_url = permalink(get_absolute_url)

    def __unicode__(self):
        return AggregateManager.AM_TYPE_CHOICES[self.type] + ' ' + self.name + ' at ' + self.url
    
    def get_local_nodes(self):
        return self.node_set.filter(is_remote=False)
    
    def updateRSpec(self):
        print "Update RSpec Type %s" % self.type
        if self.type == AggregateManager.TYPE_OF:
            return self.updateOFRSpec()
        else:
            return self.updatePLRSpec()
        
    def updateOFRSpec(self):
        '''
        Read and parse the RSpec specifying all 
        nodes from the aggregate manager using the E-GENI
        RSpec
        '''
        
        # list of node ids added
        new_node_ids = []
        
        # list of interfaces added
        new_iface_ids = []
        
        print("making client")
        # get a connector to the server
        #client = GeniLightClient(self.url, None, None)
        
        print("<2>")
        
        # read the rspec and parse it
        rspec = test_xml
        #rspec = client.list_nodes(None)
        
        print("Rspec read: "+rspec)
        
        rspecdoc = minidom.parseString(rspec)
        
        print("<3>")
        print(rspecdoc)

        print("Called get switches")
        
        # create the context
        rspec=rspecdoc.childNodes[0]
        print(rspec)
        print("<4>")
        ns_uri = rspec.namespaceURI
        print(ns_uri)
        
        # create a context
        context = xpath.Context.Context(rspec, 1, 1, 
                                        processorNss={"tns": ns_uri})
        
        # Get all the nodes
        nodes = xpath.Evaluate("*/tns:node", context=context)
        
        # In the first iteration create all the nodes
        for node in nodes:
            # move the context to the current node
            context.setNodePosSize((node, 1, 1))

            # get the node ID string
            nodeId = xpath.Evaluate("string(tns:nodeId)", context=context)
            node_type = xpath.Evaluate("name(..)", context=context)
            
            print "<x> %s" % node_type
            
            if(node_type == 'tns:remoteEntry'):
                remoteType = xpath.Evaluate("string(../tns:remoteType)", context=context)
                remoteURL = xpath.Evaluate("string(../tns:remoteURL)", context=context)
                
                # check if this clearinghouse knows about this AM
                try:
                    am = AggregateManager.objects.get(url=remoteURL)
                
                # Nope we don't know about the remote AM
                except AggregateManager.DoesNotExist:
                    node_obj = Node(nodeId=nodeId,
                                    type=remoteType,
                                    remoteURL=remoteURL,
                                    aggMgr=self,
                                    is_remote=True,
                                    )
                    node_obj.save()
                    self.node_set.add(node_obj)
                    new_node_ids.append(nodeId)
                
                # We do know about the remote AM
                else:
                    if remoteURL == self.URL:
                        raise Exception("Remote URL is my URL, but entry is remote.")
                    
                    node_obj = Node(nodeId=nodeId,
                                    type=remoteType,
                                    remoteURL=remoteURL,
                                    aggMgr=am,
                                    is_remote=True,
                                    )
            
            # Entry controlled by this AM
            else:
                node_obj = Node(nodeId=nodeId,
                                type=Node.TYPE_OF,
                                aggMgr=self,
                                remoteURL=self.url,
                                is_remote=False,
                                )
                new_node_ids.append(nodeId)
                node_obj.save()
                self.node_set.add(node_obj)
                
            node_obj.save()
            
        # delete all old nodes
        self.node_set.exclude(nodeId__in=new_node_ids).delete()
                
        # In the second iteration create all the interfaces and flowspaces
        context.setNodePosSize((rspec, 1, 1))
        interfaces = xpath.Evaluate("//tns:interfaceEntry", context=context)
        new_iface_ids = []
        for interface in interfaces:
            # move the context
            context.setNodePosSize((interface, 1, 1))
            nodeId = xpath.Evaluate("string(../tns:nodeId)", context=context)
            node_obj = self.node_set.get(pk=nodeId)
            
            portNum = int(xpath.Evaluate("number(tns:port)", context=context))
            print "<0> %s" % portNum
            
            # check if the iface exists
            iface_obj, created = \
                Interface.objects.get_or_create(portNum=portNum,
                                                ownerNode__nodeId=nodeId,
                                                defaults={'ownerNode': node_obj})
            
            new_iface_ids.append(iface_obj.id)
            
            if not created:
                iface_obj.ownerNode = node_obj
                
#            # get the flowspace entries
#            fs_entries = xpath.Evaluate("tns:flowSpaceEntry", context=context)
#            print fs_entries
#
#            # add all of them
#            interface.flowspace_set.all().delete()
#            for fs in fs_entries:
#                context.setNodePosSize((fs, 1, 1))
#                # parse the flowspace
#                p1 = lambda name: xpath.Evaluate("string(tns:%s)" % name,
#                                                 context=context)
#                
#                p = lambda x: p1(x) if (p1(x)) else "*"
#                
#                interface.flowspace_set.create(policy=p("policy"),
#                                               dl_src=p("dl_src"),
#                                               dl_dst=p("dl_dst"),
#                                               dl_type=p("dl_type"),
#                                               vlan_id=p("vlan_id"),
#                                               nw_src=p("ip_src"),
#                                               nw_dst=p("ip_dst"),
#                                               nw_proto=p("ip_proto"),
#                                               tp_src=p("tp_src"),
#                                               tp_dst=p("tp_dst"),
#                                               interface=iface)
        
        # delete extra ifaces: only those whom this AM created
        Interface.objects.exclude(
            id__in=new_iface_ids).filter(
                ownerNode__aggMgr=self).delete()
        
        # In the third iteration, add all the remote connections
        for interface in interfaces:
            # move the context
            context.setNodePosSize((interface, 1, 1))
            nodeId = xpath.Evaluate("string(../tns:nodeId)", context=context)
            portNum = int(xpath.Evaluate("number(tns:port)", context=context))
            iface_obj = Interface.objects.get(portNum__exact=portNum,
                                              ownerNode__nodeId=nodeId,
                                              ownerNode__aggMgr__pk=self.pk,
                                              )
            
            # get the remote ifaces
            other_nodeIDs = xpath.Evaluate("tns:remoteNodeId", context=context)
            other_ports = xpath.Evaluate("tns:remotePort", context=context)

            print "<1> nodes:%s ports:%s" % (other_nodeIDs, other_ports)
                
            other_ports.reverse()
            remote_iface_ids = []
            for nodeID in other_nodeIDs:
                # get the remote node object
                context.setNodePosSize((nodeID, 1, 1))
                id = xpath.Evaluate("string()", context=context)
                
                # get the remote interface at that remote node
                context.setNodePosSize((other_ports.pop(), 1, 1))
                num = int(xpath.Evaluate("number()", context=context))
                print "<8> %s %s" % (num, id)
                
                remote_iface_obj = Interface.objects.get(portNum__exact=num,
                                                         ownerNode__nodeId=id,
                                                         )
                
                remote_iface_ids.append(remote_iface_obj.id)
                iface_obj.remoteIfaces.add(remote_iface_obj)
                
                # add the connection
                print "<3>"; print id; print num
                
            # remove old connections
            iface_obj.remoteIfaces.exclude(id__in=remote_iface_ids).delete()
        
    def makeReservation(self, node_id, field_dict):
        '''Request a reservation and return a message on success or failure'''
        
        # get a connector to the server
        client = GeniLightClient(self.url, self.key_file, self.cert_file)
        
        # TODO: Fill this in
        return "Slice Reserved!"

class Node(models.Model):
    '''
    Anything that has interfaces. Can be a switch or a host or a stub.
    '''
    
    TYPE_OF = 'OF';
    TYPE_PL = 'PL';

    nodeId = models.CharField(max_length=200, primary_key=True)
    type = models.CharField(max_length=200)
    
    is_remote = models.BooleanField()
    
    # @ivar remoteURL: indicates URL of controller
    remoteURL = models.URLField("Controller URL", verify_exists=False)
    
    # @ivar aggMgr: The AM that created the node or controls it
    aggMgr = models.ForeignKey(AggregateManager)
    
    def __unicode__(self):
        return "Node %s" % self.nodeId
    
    def get_absolute_url(self):
        return('node_detail', [str(self.aggMgr.id), str(self.nodeId)])
    get_absolute_url = permalink(get_absolute_url)
    
    def is_in_clearinghouse(self):
        return self.aggMgr.url == self.remoteURL


class Interface(models.Model):
    '''Describes a port and its connection'''
    portNum = models.PositiveSmallIntegerField()
    ownerNode = models.ForeignKey(Node)
    remoteIfaces = models.ManyToManyField('self')
    
    def __unicode__(self):
        return "Interface "+portNum+" of node "+self.ownerNode.nodeId

class Slice(models.Model):
    '''This is created by a user (the owner) and contains
    multiple reservations from across different aggregate managers'''
    
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=200, unique=True)
    controller_url = models.URLField('Slice Controller URL', verify_exists=False)
    committed = models.BooleanField()
    nodes = models.ManyToManyField(Node)
    
    def get_absolute_url(self):
        return('slice_detail', [str(self.id)])
    get_absolute_url = permalink(get_absolute_url)
    
class SliceForm(ModelForm):
    class Meta:
        model = Slice
        fields = ('name', 'controller_url')

class FlowSpace(models.Model):
    policy = models.CharField(max_length=200)
    dl_src = models.CharField(max_length=200)
    dl_dst = models.CharField(max_length=200)
    dl_type = models.CharField(max_length=200)
    vlan_id = models.CharField(max_length=200)
    nw_src = models.CharField(max_length=200)
    nw_dst = models.CharField(max_length=200)
    nw_proto = models.CharField(max_length=200)
    tp_src = models.CharField(max_length=200)
    tp_dst = models.CharField(max_length=200)
    slice = models.ForeignKey(Slice)
    
    def __unicode__(self):
        return("Port: "+self.interface.portNum+", dl_src: "+self.dl_src
               +", dl_dst: "+self.dl_dst+", dl_type: "+self.dl_type
               +", vlan_id: "+self.vlan_id+", nw_src: "+self.nw_src
               +", nw_dst: "+self.nw_dst+", nw_proto: "+self.nw_proto
               +", tp_src: "+self.tp_src+", tp_dst: "+self.tp_dst)

class FlowSpaceForm(ModelForm):
    class Meta:
        model=FlowSpace
        exclude = ('slice')
        
