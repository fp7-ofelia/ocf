from django.db import models
from geniLight.geniLight_client import GeniLightClient
from xml.dom import minidom
from xml import xpath
from django.db.models import permalink

test_xml = """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<tns:RSpec xmlns:tns="http://yuba.stanford.edu/geniLight/rspec" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://yuba.stanford.edu/geniLight/rspec http://yuba.stanford.edu/geniLight/rspec.xsd">

  <tns:version>1.0</tns:version>

  <tns:switchEntry>
    <tns:node>
      <tns:nodeId>640021f7cae400</tns:nodeId>
      <tns:interfaceEntry>
        <tns:port>26</tns:port>
        <tns:remoteNodeId>213109</tns:remoteNodeId>
        <tns:remotePort>38</tns:remotePort>
        <tns:remoteNodeId>134a34</tns:remoteNodeId>
        <tns:remotePort>2</tns:remotePort>
      </tns:interfaceEntry>
      <tns:interfaceEntry>
        <tns:port>28</tns:port>
      </tns:interfaceEntry>
      <tns:flowSpaceEntry>
          <tns:policy>0</tns:policy>
          <tns:port>3552</tns:port>
          <tns:dl_type>2</tns:dl_type>
          <tns:tp_dst>423</tns:tp_dst>
      </tns:flowSpaceEntry>
      <tns:flowSpaceEntry>
          <tns:policy>0</tns:policy>
          <tns:port>32</tns:port>
          <tns:dl_type>2</tns:dl_type>
          <tns:tp_dst>423</tns:tp_dst>
      </tns:flowSpaceEntry>
    </tns:node>
  </tns:switchEntry>

  <tns:switchEntry>
    <tns:node>
      <tns:nodeId>2580021f7cae400</tns:nodeId>
      <tns:interfaceEntry>
        <tns:port>46</tns:port>
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
      </tns:interfaceEntry>
      <tns:interfaceEntry>
        <tns:port>44</tns:port>
      </tns:interfaceEntry>
    </tns:node>
  </tns:switchEntry>

  <tns:switchEntry>
    <tns:node>
      <tns:nodeId>1900021f7cae400</tns:nodeId>
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
      <tns:interfaceEntry>
        <tns:port>1</tns:port>
      </tns:interfaceEntry>
      <tns:interfaceEntry>
        <tns:port>2</tns:port>
      </tns:interfaceEntry>
      <tns:interfaceEntry>
        <tns:port>3</tns:port>
      </tns:interfaceEntry>
      <tns:interfaceEntry>
        <tns:port>4</tns:port>
      </tns:interfaceEntry>
      <tns:interfaceEntry>
        <tns:port>5</tns:port>
      </tns:interfaceEntry>
      <tns:interfaceEntry>
        <tns:port>6</tns:port>
      </tns:interfaceEntry>
      <tns:interfaceEntry>
        <tns:port>7</tns:port>
      </tns:interfaceEntry>
      <tns:interfaceEntry>
        <tns:port>8</tns:port>
      </tns:interfaceEntry>
      <tns:interfaceEntry>
        <tns:port>9</tns:port>
      </tns:interfaceEntry>
      <tns:interfaceEntry>
        <tns:port>10</tns:port>
      </tns:interfaceEntry>
      <tns:interfaceEntry>
        <tns:port>11</tns:port>
      </tns:interfaceEntry>
      <tns:interfaceEntry>
        <tns:port>12</tns:port>
      </tns:interfaceEntry>
      <tns:interfaceEntry>
        <tns:port>13</tns:port>
      </tns:interfaceEntry>
      <tns:interfaceEntry>
        <tns:port>14</tns:port>
      </tns:interfaceEntry>
    </tns:node>
  </tns:switchEntry>

</tns:RSpec>
"""

class AggregateManager(models.Model):
    name = models.TextField(max_length=200)
    url = models.URLField('Aggregate Manager URL')
    key_file = models.TextField(max_length=200)
    cert_file = models.TextField(max_length=200)
    rspec = models.TextField()
    
    def __unicode__(self):
        return 'AM ' + self.name + ' at ' + self.url
    
    def get_absolute_url(self):
        return ('am_details', [str(self.id)])
    get_absolute_url = permalink(get_absolute_url)

    def updateRSpec(self):
        '''Read the RSpec from the aggregate manager'''
        
        print("making client")
        # get a connector to the server
        client = GeniLightClient(self.url, self.key_file, self.cert_file)
        
        print("<2>")
        
        # read the rspec and parse it
        self.rspec = test_xml
        #self.rspec = client.list_nodes(None)
        
        print("Rspec read: "+self.rspec)
        
    def getSwitchesInfo(self):
        '''Get a list of 2-tuples (my_nodeID, connections) where 
        my_nodeID is a string that is the node ID of a node and 
        connections is a list of triples((my_port, otherNodeID, other_port) that
        describes the connections the node has'''
        
        
        rspecdoc = minidom.parseString(self.rspec)
        
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
        
        # For each node in the list
        retval = []
        for node in nodes:
            # move the context to the current node
            context.setNodePosSize((node, 1, 1))

            # get the node ID string
            my_nodeID = xpath.Evaluate("string(tns:nodeId)", context=context)
            
            # get all the connections
            connections = []
            interfaces = xpath.Evaluate("tns:interfaceEntry", context=context)
            # for each interface node
            for interface in interfaces:
                # move the context
                context.setNodePosSize((interface, 1, 1))
                
                # get my port number
                my_port = int(xpath.Evaluate("number(tns:port)", context=context))
                
                # get the first connection
                # TODO: This will only display the first connection
                other_nodeID = xpath.Evaluate("string(tns:remoteNodeId)", context=context)
                if(other_nodeID):
                    other_port = int(xpath.Evaluate("number(tns:remotePort)", context=context))
                
                    # add the connection
                    connections.append((my_port, other_nodeID, other_port))
                
            # add the node info
            retval.append((my_nodeID, connections))
        
        return retval

    def getNodeDetail(self, nodeID):
        '''Return a tuple (connections, flowspace) where connections
        is a list of tuples (my_port, remote_nodes), and remote_nodes is a list
        of tuples (remote_nodeID, remote_port). flowspace is a list tuples
        (port, dl_src, dl_dst, dl_type, vlan_id, nw_src, nw_dst, nw_proto, tp_src, tp_dst).
        If the node is not found, returns None.'''
        
        rspecdoc = minidom.parseString(self.rspec)
        
        # create the context
        rspec = rspecdoc.childNodes[0]
        ns_uri = rspec.namespaceURI
        
        # create a context
        context = xpath.Context.Context(rspec, 1, 1, 
                                        processorNss={"tns": ns_uri})

        # get the node
        node = xpath.Evaluate("*/tns:node[tns:nodeId='%s']" % nodeID, context=context)
        if(len(node) == 0):
            return None
        
        node = node[0]
        
        # move the context to the current node
        context.setNodePosSize((node, 1, 1))

        # get all the connections
        connections = []
        interfaces = xpath.Evaluate("tns:interfaceEntry", context=context)
        # for each interface node
        for interface in interfaces:
            # move the context
            context.setNodePosSize((interface, 1, 1))
            
            # get my port number
            my_port = int(xpath.Evaluate("number(tns:port)", context=context))
            print "<0> %s" % my_port
            
            # get all the connections
            other_nodeIDs = xpath.Evaluate("tns:remoteNodeId", context=context)
            other_ports = xpath.Evaluate("tns:remotePort", context=context)
            
            print "<1> nodes:%s ports:%s" % (other_nodeIDs, other_ports)
            
            # arrange in pairs
            other_pairs = []
            other_ports.reverse()
            for nodeID in other_nodeIDs:
                context.setNodePosSize((nodeID, 1, 1))
                id = xpath.Evaluate("string()", context=context)
                context.setNodePosSize((other_ports.pop(), 1, 1))
                num = xpath.Evaluate("string()", context=context)
                other_pairs.append((id, num))
                print "<2> %s %s" % (id, num)
                
            # add the connection
            print "<3>"; print other_pairs
            connections.append((my_port, other_pairs))
            
        print connections
        
        # reset the context to the node
        context.setNodePosSize((node, 1, 1))
        print node
        
        # get the flowspace
        fs_entries = xpath.Evaluate("tns:flowSpaceEntry", context=context)
        print fs_entries

        flowspace = []
        for fs in fs_entries:
            context.setNodePosSize((fs, 1, 1))
            # parse the flowspace
            p1 = lambda name: xpath.Evaluate("string(tns:%s)" % name,
                                            context=context)
            p = lambda x: p1(x) if (p1(x)) else "*"
            flowspace.append((p("port"), p("dl_src"), p("dl_dst"), 
                              p("dl_type"), p("vlan_id"), p("nw_src"),
                              p("nw_dst"), p("nw_proto"), p("tp_src"), 
                              p("tp_dst")))
        
        print flowspace    
        return (connections, flowspace)
    
    def makeReservation(self, node_id, field_dict):
        '''Request a reservation and return a message on success or failure'''
        
        # get a connector to the server
        client = GeniLightClient(self.url, self.key_file, self.cert_file)
        
        # TODO: Fill this in
        return "Slice Reserved!"