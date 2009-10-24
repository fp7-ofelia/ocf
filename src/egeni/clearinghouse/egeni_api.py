'''
Created on Oct 16, 2009

Contains egeni specific functions

@author: jnaous, srini
'''

from httplib import HTTPConnection
from sfa.util import xmlrpcprotocol
from sfa.util import soapprotocol
from sfa.trust.certificate import Keypair

from xml.dom import minidom
from xml import xpath
import models
from django.db.models import Count
import random

MAX_X = 200
MAX_Y = 200

key_file = './geniclearinghouse.pkey'
cert_file = './geniclearinghouse.cert'
cred_file = './geniclearinghouse.cred'
CH_hrn = 'plc.openflow.geniclearinghouse'
key = Keypair(filename=key_file)
server = {}

def init():
    global CH_cred, cred_file
    CH_cred = file(cred_file).read()

def connect_to_soap_server(am_url):
    global server, CH_hrn, key_file, cert_file
    print "Connecting to", am_url

    #Internet tells me to use the following to fix some array anomalies
    #imp = Import('http://schemas.xmlsoap.org/soap/encoding/')
    #d = ImportDoctor(imp)
    #server[am_url]= Client(sfa_wsdl_url, cache=None, location=am_url, doctor=d)

    server[am_url]= soapprotocol.get_server(am_url, key_file, cert_file)

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
    global server, CH_cred
    if am_url not in server:
        connect_to_soap_server(am_url)

    # The second param is supposed to be HRN, but replaced with slice_id
    request_hash = key.compute_hash([CH_cred, str(slice_id), str(rspec)])
    result = server[am_url].create_slice(CH_cred, str(slice_id), str(rspec), request_hash)
    print result
    
    return ""    

def delete_slice(am_url, slice_id):
    '''
    Delete the slice.
    '''
    global server, CH_cred
    if am_url not in server:
        connect_to_soap_server(am_url)

    # The second param is supposed to be HRN, but replaced with slice_id
    request_hash = key.compute_hash([CH_cred, str(slice_id)])
    result = server[am_url].delete_slice(CH_cred, str(slice_id), request_hash)
    pass

def get_rspec(am_url):
    '''
    Returns the RSpec of available resources.
    '''
    global server, CH_cred, CH_hrn
    if am_url not in server:
        connect_to_soap_server(am_url)

    # The HRN is used to identify the person issuing this call.
    # Currently unused
    request_hash = key.compute_hash([CH_cred, CH_hrn])
    result = server[am_url].get_resources(CH_cred, CH_hrn, request_hash)
    print result
    return result

def update_rspec(self_am):
    '''
    Read and parse the RSpec specifying all 
    nodes from the aggregate manager using the E-GENI
    RSpec
    '''
    
    if self_am.name == "RemoteAM":
        return
    
    rspec = get_rspec(self_am.url)
    
    rspecdoc = minidom.parseString(rspec)
    
    # create the context
    rspec=rspecdoc.childNodes[0]
    ns_uri = rspec.namespaceURI
    
    # create a context
    context = xpath.Context.Context(rspec, 1, 1, 
                                    processorNss={"tns": ns_uri})
    
    # Get all the nodes
    nodes = xpath.Evaluate("*/tns:node", context=context)
    
    # list of node ids added
    new_local_ids = []
    new_remote_ids = []
    
    print "-----My AM id: %s" %  self_am.id
    
    # In the first iteration create all the nodes
    for node in nodes:
        # move the context to the current node
        context.setNodePosSize((node, 1, 1))

        # get the node ID string
        nodeId = xpath.Evaluate("string(tns:nodeId)", context=context)
        node_type = xpath.Evaluate("name(..)", context=context)
        
        kwargs = {'nodeId':nodeId,
                  'x':0,
                  'y':0,
                  'img_url':"/img/blue_circle.png",
                  }

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
                
                print "+++++ Adding remote out CH Node %s to AM %s" % (nodeId, remoteAM.id)
                
                mod = {'type':remoteType,
                       'remoteURL':remoteURL,
                       'aggMgr':remoteAM,
                       'is_remote':True}
                kwargs.update(**mod)
                
                node_obj = models.Node(**kwargs)
                node_obj.save()
                self_am.remote_node_set.add(node_obj)
                new_remote_ids.append(nodeId)
            
            # We do know about the remote AM
            else:
                if remoteURL == self_am.URL:
                    raise Exception("Remote URL is my URL, but entry is remote.")
                
                print "+++++ Adding remote in CH Node %s" % nodeId

                mod = {'type':remoteType,
                       'remoteURL':remoteURL,
                       'aggMgr':am,
                       'is_remote':False}
                kwargs.update(**mod)
                
                node_obj = models.Node(**kwargs)
                node_obj.save()
                self_am.remote_node_set.add(node_obj)
                new_remote_ids.append(nodeId)
        
        # Entry controlled by this AM
        else:
            print "+++++ Adding local Node %s" % nodeId

            mod = {'type':models.Node.TYPE_OF,
                   'remoteURL':self_am.url,
                   'aggMgr':self_am,
                   'is_remote':False}
            print "Doing random"
            mod['x'] = random.randint(0, MAX_X-50)
            mod['y'] = random.randint(0, MAX_Y-50)
            print "Adding new node"
            kwargs.update(**mod)
            print "node added"
            
            node_obj = models.Node(**kwargs)
            new_local_ids.append(nodeId)
            node_obj.save()
            print "node saved"
        
        self_am.connected_node_set.add(node_obj)
        node_obj.save()
    
    print "*** All local nodes"
    for n in self_am.local_node_set.filter():
        print "    %s" % n.nodeId
    
    print "*** All old local nodes"
    for n in self_am.local_node_set.exclude(nodeId__in=new_local_ids):
        print "    %s" % n.nodeId

    print "*** All old local moved nodes"
    for n in self_am.local_node_set.filter(nodeId__in=new_remote_ids):
        print "    %s" % n.nodeId

    # delete all old local nodes
    self_am.local_node_set.exclude(nodeId__in=new_local_ids).delete()
    self_am.local_node_set.filter(nodeId__in=new_remote_ids).delete()
    
    print "*** All new nodes"
    for n in self_am.local_node_set.filter():
        print "    %s" % n.nodeId

    # Remove stale remote nodes
    [self_am.remote_node_set.remove(n) for n in self_am.remote_node_set.exclude(nodeId__in=new_remote_ids)]
    [self_am.remote_node_set.remove(n) for n in self_am.remote_node_set.filter(nodeId__in=new_local_ids)]
    
    print "*** All connected nodes"
    for n in self_am.connected_node_set.filter():
        print "    %s" % n.nodeId
    
    print "*** All old connected nodes"
    for n in self_am.connected_node_set.exclude(
                nodeId__in=new_local_ids).exclude(
                    nodeId__in=new_remote_ids):
        print "    %s" % n.nodeId

    # Remove Unconnected nodes
    [self_am.connected_node_set.remove(n)
        for n in self_am.connected_node_set.exclude(
                    nodeId__in=new_local_ids).exclude(
                        nodeId__in=new_remote_ids)]
    
    print "*** New connected nodes"
    for n in self_am.connected_node_set.filter():
        print "    %s" % n.nodeId

    # Delete unconnected nodes that no AM is connected to
    print "*** Deleting nodes"
    for n in models.Node.objects.annotate(
        num_cnxns=Count('connected_am_set')).filter(
            num_cnxns=0):
        print "    %s" % n.nodeId
    
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
        print "*** Getting connected node %s" % nodeId
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


# Unit test
#init()
#get_rspec("http://171.67.75.2:12346")
