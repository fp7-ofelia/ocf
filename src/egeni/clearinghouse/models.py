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
    '''A single aggregate manager'''
    name = models.TextField(max_length=200, unique=True)
    url = models.URLField('Aggregate Manager URL', unique=True, verify_exists=False)
    key_file = models.TextField(max_length=200)
    cert_file = models.TextField(max_length=200)
    
    def __unicode__(self):
        return 'AM ' + self.name + ' at ' + self.url
    
    def get_absolute_url(self):
        return ('am_detail', [str(self.id)])
    get_absolute_url = permalink(get_absolute_url)

    def updateRSpec(self):
        '''Read and parse the RSpec from the aggregate manager'''
        
        # clear the old nodes
        self.node_set.all().delete()
        
        print("making client")
        # get a connector to the server
        client = GeniLightClient(self.url, self.key_file, self.cert_file)
        
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
        nodes = xpath.Evaluate("tns:switchEntry/tns:node", context=context)
        
        # In the first iteration create all the nodes
        for node in nodes:
            # move the context to the current node
            context.setNodePosSize((node, 1, 1))

            # get the node ID string
            nodeId = xpath.Evaluate("string(tns:nodeId)", context=context)
            node_type = xpath.Evaluate("string(tns:nodeId)", context=context)
            self.node_set.create(aggMgr=self,
                                 nodeId=nodeId,
                                 type=node_type)
            
        # In the second iteration create all the interfaces and flowspaces
        context.setNodePosSize((rspec, 1, 1))
        interfaces = xpath.Evaluate("//tns:interfaceEntry", context=context)
        for interface in interfaces:
            # move the context
            context.setNodePosSize((interface, 1, 1))
            nodeId = xpath.Evaluate("string(../tns:nodeId)", context=context)
            node_obj = self.node_set.get(pk=nodeId)
            
            portNum = int(xpath.Evaluate("number(tns:port)", context=context))
            print "<0> %s" % portNum
            iface = node_obj.interface_set.create(portNum=portNum,
                                                  ownerNode=node_obj)
            
            # get the flowspace entries
            fs_entries = xpath.Evaluate("tns:flowSpaceEntry", context=context)
            print fs_entries

            # add all of them
            for fs in fs_entries:
                context.setNodePosSize((fs, 1, 1))
                # parse the flowspace
                p1 = lambda name: xpath.Evaluate("string(tns:%s)" % name,
                                                 context=context)
                
                p = lambda x: p1(x) if (p1(x)) else "*"
                
                iface.flowspace_set.create(policy=p("policy"),
                                           dl_src=p("dl_src"),
                                           dl_dst=p("dl_dst"),
                                           dl_type=p("dl_type"),
                                           vlan_id=p("vlan_id"),
                                           nw_src=p("ip_src"),
                                           nw_dst=p("ip_dst"),
                                           nw_proto=p("ip_proto"),
                                           tp_src=p("tp_src"),
                                           tp_dst=p("tp_dst"),
                                           interface=iface)

            
        # In the third iteration, add all the remote connections
        for interface in interfaces:
            # move the context
            context.setNodePosSize((interface, 1, 1))
            nodeId = xpath.Evaluate("string(../tns:nodeId)", context=context)
            portNum = int(xpath.Evaluate("number(tns:port)", context=context))
            iface_obj = Interface.objects.get(portNum__exact=portNum,
                                              ownerNode__nodeId__exact=nodeId)
            
            # get the remote ifaces
            other_nodeIDs = xpath.Evaluate("tns:remoteNodeId", context=context)
            other_ports = xpath.Evaluate("tns:remotePort", context=context)
                
            print "<1> nodes:%s ports:%s" % (other_nodeIDs, other_ports)
                
            other_ports.reverse()
            for nodeID in other_nodeIDs:
                # get the remote node object
                context.setNodePosSize((nodeID, 1, 1))
                id = xpath.Evaluate("string()", context=context)
                
                # get the remote interface at that remote node
                context.setNodePosSize((other_ports.pop(), 1, 1))
                num = int(xpath.Evaluate("number()", context=context))
                print "<8> %s %s" % (num, id)
                remote_iface_obj = Interface.objects.get(portNum__exact=num,
                                                         ownerNode__nodeId__exact=id)
                    
                
                # add the remote interface
                iface_obj.remoteIfaces.add(remote_iface_obj)

                # add the connection
                print "<3>"; print id; print num
        
    def makeReservation(self, node_id, field_dict):
        '''Request a reservation and return a message on success or failure'''
        
        # get a connector to the server
        client = GeniLightClient(self.url, self.key_file, self.cert_file)
        
        # TODO: Fill this in
        return "Slice Reserved!"

class Node(models.Model):
    '''Anything that has interfaces. Can be a switch or a host'''
    aggMgr = models.ForeignKey(AggregateManager)
    nodeId = models.CharField(max_length=200, primary_key=True)
    type = models.CharField(max_length=200)
    
    def __unicode__(self):
        return "Node %s" % self.nodeId
    
    def get_absolute_url(self):
        return('node_detail', [str(self.aggMgr.id), str(self.nodeId)])
    get_absolute_url = permalink(get_absolute_url)
    

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
        
