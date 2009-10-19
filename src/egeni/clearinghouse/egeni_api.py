'''
Created on Oct 16, 2009

Contains egeni specific functions

@author: jnaous
'''

from xml.dom import minidom
from xml import xpath
import models
from django.db.models import Count

def reserve_slice(am_url, rspec, slice_id):
    '''
    Reserves the slice identified by slice_id or
    updates the slice if already reserved on the AM.
    
    On success, returns the empty string.
    On error, returns an rspec that has the failing nodes with their
    failing interfaces if the AM failed to reserve the interface.
    If reserving the node failed but not due to the interface, the
    rspec contains only the failing node without its interfaces.
    '''

    return ""    

def delete_slice(am_url, slice_id):
    '''
    Delete the slice.
    '''
    pass

def get_rspec(am_url):
    '''
    Returns the RSpec of available resources.
    '''
    
    return """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
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

def update_rspec(self_am):
    '''
    Read and parse the RSpec specifying all 
    nodes from the aggregate manager using the E-GENI
    RSpec
    '''
    
    print("making client")
    rspec = get_rspec(self_am.url)
    
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
    
    # list of node ids added
    new_local_ids = []
    new_remote_ids = []

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
                am = models.AggregateManager.objects.get(url=remoteURL)
            
            # Nope we don't know about the remote AM
            except models.AggregateManager.DoesNotExist:
                remoteAM, created = models.AggregateManager.objects.get_or_create(
                    name="RemoteAM",
                    defaults={"url": "non.existant.org",
                              "type": models.AggregateManager.TYPE_OF,
                              },
                    )
                remoteAM.save()
                node_obj = models.Node(nodeId=nodeId,
                                type=remoteType,
                                remoteURL=remoteURL,
                                aggMgr=remoteAM,
                                is_remote=True,
                                x=0,
                                y=0,
                                sel_img_url="localhost:8000/clearinghouse/img/sel_of_img.png",
                                unsel_img_url="localhost:8000/clearinghouse/img/unsel_of_img.png",
                                err_img_url="localhost:8000/clearinghouse/img/err_of_img.png",                                
                                )
                node_obj.save()
                self_am.remote_node_set.add(node_obj)
                new_remote_ids.append(nodeId)
            
            # We do know about the remote AM
            else:
                if remoteURL == self_am.URL:
                    raise Exception("Remote URL is my URL, but entry is remote.")
                
                node_obj = models.Node(nodeId=nodeId,
                                type=remoteType,
                                remoteURL=remoteURL,
                                aggMgr=am,
                                is_remote=False,
                                x=0,
                                y=0,
                                sel_img_url="localhost:8000/clearinghouse/img/sel_of_img.png",
                                unsel_img_url="localhost:8000/clearinghouse/img/unsel_of_img.png",
                                err_img_url="localhost:8000/clearinghouse/img/err_of_img.png",                                
                                )
                node_obj.save()
                self_am.remote_node_set.add(node_obj)
                new_remote_ids.append(nodeId)
        
        # Entry controlled by this AM
        else:
            node_obj = models.Node(nodeId=nodeId,
                            type=models.Node.TYPE_OF,
                            aggMgr=self_am,
                            remoteURL=self_am.url,
                            is_remote=False,
                            x=0,
                            y=0,
                            sel_img_url="localhost:8000/clearinghouse/img/sel_of_img.png",
                            unsel_img_url="localhost:8000/clearinghouse/img/unsel_of_img.png",
                            err_img_url="localhost:8000/clearinghouse/img/err_of_img.png",                                
                            )
            new_local_ids.append(nodeId)
            node_obj.save()
        
        self_am.connected_node_set.add(node_obj)
        node_obj.save()
        
    # delete all old local nodes
    self_am.local_node_set.exclude(nodeId__in=new_local_ids).delete()
    self_am.local_node_set.filter(nodeId__in=new_remote_ids).delete()
    
    # Remove stale remote nodes
    [self_am.remote_node_set.remove(n) for n in self_am.remote_node_set.exclude(nodeId__in=new_remote_ids)]
    [self_am.remote_node_set.remove(n) for n in self_am.remote_node_set.filter(nodeId__in=new_local_ids)]
    
    # Remove Unconnected nodes
    [self_am.connected_node_set.remove(n)
        for n in self_am.connected_node_set.exclude(
                    nodeId__in=new_local_ids).exclude(
                        nodeId__in=new_remote_ids)]
    
    # Delete unconnected nodes that no AM is connected to
    models.Node.objects.annotate(
        num_cnxns=Count('connected_am_set')).filter(
            num_cnxns=0).delete()
    
    # In the second iteration create all the interfaces and flowspaces
    context.setNodePosSize((rspec, 1, 1))
    interfaces = xpath.Evaluate("//tns:interfaceEntry", context=context)
    # list of interfaces added
    new_iface_ids = []
    for interface in interfaces:
        # move the context
        context.setNodePosSize((interface, 1, 1))
        nodeId = xpath.Evaluate("string(../tns:nodeId)", context=context)
        node_obj = self_am.connected_node_set.get(pk=nodeId)
        
        portNum = int(xpath.Evaluate("number(tns:port)", context=context))
        print "<0> %s" % portNum
        
        # check if the iface exists
        iface_obj, created = \
            models.Interface.objects.get_or_create(portNum=portNum,
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
    models.Interface.objects.exclude(
        id__in=new_iface_ids).filter(
            ownerNode__aggMgr=self_am).delete()
    
    # In the third iteration, add all the remote connections
    for interface in interfaces:
        # move the context
        context.setNodePosSize((interface, 1, 1))
        nodeId = xpath.Evaluate("string(../tns:nodeId)", context=context)
        portNum = int(xpath.Evaluate("number(tns:port)", context=context))
        iface_obj = models.Interface.objects.get(portNum__exact=portNum,
                                                 ownerNode__nodeId=nodeId,
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
            
            remote_iface_obj = models.Interface.objects.get(portNum__exact=num,
                                                            ownerNode__nodeId=id,
                                                            )
            
            remote_iface_ids.append(remote_iface_obj.id)
            
            # get the link or create one if it doesn't exist
            link, created = models.Link.objects.get_or_create(
                                src=iface_obj, dst=remote_iface_obj)
            link.save()
            
            # add the connection
            print "<3>"; print id; print num
            
        # remove old connections
        iface_obj.remoteIfaces.exclude(id__in=remote_iface_ids).delete()
