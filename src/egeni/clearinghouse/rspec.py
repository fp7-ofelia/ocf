'''
Created on Oct 6, 2009

@author: jnaous
'''

from xml.dom import minidom
from xml import xpath

class RSpecParser(object):
    '''
    Interface for parsing RSpecs.
    '''
    
    TYPE_OF = 'OF'
    TYPE_PL = 'PL'

    def __init__(self, type):
        '''
        Constructor
        
        @param type: is the type of RSpec this parser parses
        '''
        
        if type == TYPE_OF:
            self.parse_nodes = self.of_parse_nodes
            self.parse_ifaces = self.of_parse_nodes
            self.parse_nodes = self.of_parse_nodes
            
        elif type == TYPE_PL:
            self.parse = self.pl_parse
            
        else:
            raise Exception("Unknown type %s" % type)
        
    def of_parse_nodes(self, rspec):
        '''
        Parses an OpenFlow rspec and returns a topology.
        
        @param rspec: is an OpenFlow Rspec as a string XML
        '''
        
        node_set = QuerySet()
        
        print("Rspec read: "+rspec)
        
        rspecdoc = minidom.parseString(rspec)
        
        print("<3>")
        print(rspecdoc)

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
            nodes[nodeId] = {'type': node_type,
                             'config': OFConfig,
                             'ifaces': {},
                             }
            
        # In the second iteration create all the interfaces and flowspaces
        context.setNodePosSize((rspec, 1, 1))
        interfaces = xpath.Evaluate("//tns:interfaceEntry", context=context)
        for interface in interfaces:
            # move the context
            context.setNodePosSize((interface, 1, 1))
            nodeId = xpath.Evaluate("string(../tns:nodeId)", context=context)
            
            portNum = int(xpath.Evaluate("number(tns:port)", context=context))
            print "<0> %s" % portNum
            nodes[nodeId]['ifaces'][portNum] = {'flowspace': [],
                                                'remote': []}
            iface = node_obj['ifaces'][portNum]
            
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
                
                iface['flowspace'].append({'policy': p("policy"),
                                           'dl_src': p("dl_src"),
                                           'dl_dst': p("dl_dst"),
                                           'dl_type': p("dl_type"),
                                           'vlan_id': p("vlan_id"),
                                           'nw_src': p("ip_src"),
                                           'nw_dst': p("ip_dst"),
                                           'nw_proto': p("ip_proto"),
                                           'tp_src': p("tp_src"),
                                           'tp_dst': p("tp_dst"),
                                           })

            
        # In the third iteration, add all the remote connections
        for interface in interfaces:
            # move the context
            context.setNodePosSize((interface, 1, 1))
            nodeId = xpath.Evaluate("string(../tns:nodeId)", context=context)
            portNum = int(xpath.Evaluate("number(tns:port)", context=context))
            iface_obj = nodes[nodeId]['ifaces'][portNum]
            
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
                remote_iface_obj = nodes[id]['ifaces'][num]
                
                # add the remote interface
                iface_obj['remote'].append(remote_iface_obj)

                # add the connection
                print "<3>"; print id; print num

        return nodes
    