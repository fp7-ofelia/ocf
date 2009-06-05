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
        <tns:remoteNodeId>929123</tns:remoteNodeId>
        <tns:remotePort>3</tns:remotePort>
      </tns:interfaceEntry>
      <tns:interfaceEntry>
        <tns:port>28</tns:port>
      </tns:interfaceEntry>
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
      <tns:nodeId>1900021f7cae400</tns:nodeId>
    </tns:node>
  </tns:switchEntry>

</tns:RSpec>
"""

class AggregateManager(models.Model):
    name = models.TextField(max_length=200)
    url = models.URLField('Aggregate Manager URL')
    key_file = models.TextField(max_length=200)
    cert_file = models.TextField(max_length=200)
    
    def __unicode__(self):
        return 'AM ' + self.name + ' at ' + self.url
    
    def get_absolute_url(self):
        return ('details', [str(self.id)])
    get_absolute_url = permalink(get_absolute_url)

    def _updateRSpec(self):
        '''Read the RSpec from the aggregate manager and 
        store the parsed DOM'''
        
        print("making client")
        # get a connector to the server
        client = GeniLightClient(self.url, self.key_file, self.cert_file)
        
        print("<2>")
        
        # read the rspec and parse it
        #rspec_xml = test_xml
        rspec_xml = client.list_nodes(None)
        
        print("Rspec read: "+rspec_xml)
        
        self.rspecdoc = minidom.parseString(rspec_xml)
        
        print("<3>")
        print(self.rspecdoc)
        
    def _makeXPathQuery(self, query):
        '''Create a context from the doc and make the query. Returns
        the result.'''
        
        # get the namespace uri
        rspec=self.rspecdoc.childNodes[0]
        ns_uri = rspec.namespaceURI
        
        # create a context
        context = xpath.Context.Context(rspec, 1, 1, 
                                        processorNss={"tns": ns_uri})
        
        return xpath.Evaluate(query, context=context)

    def getSwitchesInfo(self):
        '''Get a list of 2-tuples (my_nodeID, connections) where 
        my_nodeID is a string that is the node ID of a node and 
        connections is a list of triples((my_port, otherNodeID, other_port) that
        describes the connections the node has'''
        
        print("Called get switches")
        
        # update the rspec
        self._updateRSpec()
        
        print("Done update rspec")
        
        # create the context
        rspec=self.rspecdoc.childNodes[0]
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
            print("<5>")
            print(node)

            # get the node ID string
            my_nodeID = xpath.Evaluate("string(tns:nodeId)", context=context)
            print("<6>")
            print(my_nodeID)
            
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


