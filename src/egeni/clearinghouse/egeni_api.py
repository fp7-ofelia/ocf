'''
Created on Oct 16, 2009

Contains egeni specific functions

@author: jnaous, srini
'''
try:
    import xml.etree.ElementTree as et
except:
    import elementtree.ElementTree as et

from httplib import HTTPConnection
from sfa.util import soapprotocol
from sfa.trust.certificate import Keypair
from sfa.trust.credential import Credential
from sfa.util.geniclient import GeniClient
from sfa.util.record import *
from sfa.util.xmlrpcprotocol import ServerException
import os, sys

import models
from django.db.models import Count
import traceback
import os
from django.conf import settings

IMG_DICT = {'default': "/img/switch.png",
            'HP': "/img/switch-5406zl.png",
            'NEC': "/img/switch-nec-ip8800.png",
            'netfpga': "/img/switch-netfpga.png",
            'soekris': "/img/soekris-net4801.jpg",
            }


key_file = os.path.join(settings.EGENI_DIR, 'cred/seethara.pkey')
cert_file = os.path.join(settings.EGENI_DIR, 'cred/seethara.cert')
cred_file = os.path.join(settings.EGENI_DIR, 'cred/seethara.cred')
reg_url = 'http://www.planet-lab.org:12345'

CH_hrn = 'plc.openflow.seethara'
AUTH_hrn = 'plc.openflow'
key = Keypair(filename=key_file)
server = {}
done_init = False

#slice_name = 'plc.openflow.egeni'

en_debug = 0
def debug(s):
    if(en_debug):
        print(s)

def init():
    global CH_cred, auth_cred, cred_file, done_init, AUTH_hrn, registry
    CH_cred = Credential(filename=cred_file)
    done_init = True

    file = os.path.join(settings.EGENI_DIR, 'cred/authority.cred')
    registry = GeniClient(reg_url, key_file, cert_file) 

    if (os.path.isfile(file)):
       auth_cred = Credential(filename=file)
    else:
        # bootstrap authority credential from user credential
        auth_cred = registry.get_credential(CH_cred, "authority", AUTH_hrn)
        if auth_cred:
            auth_cred.save_to_file(file, save_parents=True)
        else: 
            print "Failed to get authority credential"

def add_slice(slice_id):
    global CH_cred, auth_cred, AUTH_hrn, key_file, cert_file, registry

    record = GeniRecord(string='<record authority="%s" description="GEC6" hrn="%s.%s" name="openflow_%s" type="slice" url="http://www.openflowswitch.org"><researcher>%s</researcher></record>' % (AUTH_hrn, AUTH_hrn, slice_id, slice_id, CH_hrn))
    registry.register(auth_cred, record)

def remove_slice(slice_id):
    global CH_cred, auth_cred, AUTH_hrn, key_file, cert_file, registry

    registry.remove(auth_cred, "slice", "%s.%s" % (AUTH_hrn, slice_id))

def connect_to_soap_server(am_url):
    global server, CH_hrn, key_file, cert_file, done_init
    
    if not done_init: init()
        
    print "Connecting to", am_url

    #Internet tells me to use the following to fix some array anomalies
    #imp = Import('http://schemas.xmlsoap.org/soap/encoding/')
    #d = ImportDoctor(imp)
    #server[am_url]= Client(sfa_wsdl_url, cache=None, location=am_url, doctor=d)

    server[am_url]= soapprotocol.get_server(am_url, key_file, cert_file)

def reserve_slice(am_url, rspec, slice_id, is_planetlab=0):
    '''
    Reserves the slice identified by slice_id or
    updates the slice if already reserved on the AM.
    
    On success, returns the empty string.
    On error, returns an rspec that has the failing nodes with their
    failing interfaces if the AM failed to reserve the interface.
    If reserving the node failed but not due to the interface, the
    rspec contains only the failing node without its interfaces.
    '''
    global server, key
    if am_url not in server:
        connect_to_soap_server(am_url)

    # TODO: the following should be loaded from the DB
    slice_cred = file('../cred/slice_egeni.cred').read()

    # The second param is supposed to be HRN, but replaced with slice_id
    if is_planetlab:
        result = server[am_url].create_slice(slice_cred, str(slice_id), str(rspec))
    else:
        request_hash = key.compute_hash([slice_cred, str(slice_id), str(rspec)])
        result = server[am_url].create_slice(slice_cred, str(slice_id), str(rspec), request_hash)

    debug(result)
    
    return ""    

def delete_slice(am_url, slice_id, is_planetlab=0):
    '''
    Delete the slice.
    '''
    
    return

    # TODO: remove after debugging
#    if not is_planetlab:
#        return

    global server, key
    if am_url not in server:
        connect_to_soap_server(am_url)

    # TODO: the following should be loaded from the DB
    slice_cred = file('../cred/slice_egeni.cred').read()

    # The second param is supposed to be HRN, but replaced with slice_id
    if is_planetlab:
        result = server[am_url].delete_slice(slice_cred, str(slice_id))
    else:
        request_hash = key.compute_hash([slice_cred, str(slice_id)])
        result = server[am_url].delete_slice(slice_cred, str(slice_id), request_hash)
    

def get_rspec(am_url, is_planetlab=0):
    '''
    Returns the RSpec of available resources.
    '''

    global server, CH_cred, CH_hrn
    
    debug("Called get rspec")

    if am_url not in server:
        debug("Connecting to server")
        connect_to_soap_server(am_url)

    # The HRN is used to identify the person issuing this call.
    # Currently unused
    debug("Getting result")
    if is_planetlab:
        result = server[am_url].get_resources(CH_cred)
    else:
        request_hash = key.compute_hash([CH_cred, CH_hrn])
        result = server[am_url].get_resources(CH_cred, CH_hrn, request_hash)
        
#    print result
    return result


def update_rspec(self_am):
    '''
    Read and parse the RSpec specifying all 
    nodes from the aggregate manager using the E-GENI
    RSpec
    '''
    
    ns = "http://yuba.stanford.edu/egeni/rspec"
    
    debug("Getting XML")

    xml_str = get_rspec(self_am.url)

    debug("Parsing xml:")
    debug(xml_str)

    tree = et.ElementTree(et.fromstring(xml_str))
    parent_map = dict((c, p) for p in tree.getiterator() for c in p)
    
    # list of node ids added
    new_local_ids = []
    new_remote_ids = []
    
    debug("-----My AM id: %s" %  self_am.id)
    
    node_elems = tree.findall("*/{%s}node" % ns)
    debug("node elems:")
    debug(node_elems)
    
    # In the first iteration create all the nodes
    for node_elem in node_elems:
        # get the node ID string
        nodeId = node_elem.findtext("{%s}nodeId" % ns)
        try:
            nodeName = node_elem.findtext("{%s}nodeName" % ns)
            if not nodeName:
                nodeName = ""
        except:
            nodeName = nodeId
        parent = parent_map[node_elem]
        node_type = parent.tag
        
        debug("node_type for %s is %s" % (nodeId, node_type))
        
        kwargs = {'nodeId': nodeId,
                  'img_url': IMG_DICT['default'],
                  'name': nodeName,
                  }

        if('remoteNodeEntry' in node_type):
            # check if this clearinghouse knows about this node
            try:
                node_obj = models.Node.objects.get(pk=nodeId)
            
            # Nope we don't know about the node
            except models.Node.DoesNotExist:
                
                debug("+++++ Adding remote out CH Node %s" % nodeId)
                
                mod = {'is_remote':True}
                kwargs.update(**mod)
                
                node_obj = models.Node.objects.create(**kwargs)
                node_obj.save()
                
                self_am.remote_node_set.add(node_obj)
                new_remote_ids.append(nodeId)
            
            # We do know about the remote node
            else:
                debug("+++++ Not doing anything already known %s" % nodeId)
                self_am.remote_node_set.add(node_obj)
                new_remote_ids.append(nodeId)
        
        # Entry controlled by this AM
        else:
            debug("+++++ Adding local Node %s" % nodeId)
            
            mod = {'type':models.Node.TYPE_OF,
                   'aggMgr':self_am,
                   'name': nodeName,
                   'is_remote':False}

            features = parent.findtext("{%s}switchFeatures" % ns)
            debug("Features: %s" % features)
            for k,v in IMG_DICT.items():
                if k in features or k in nodeName:
                    mod['img_url'] = v
                    break
            
            mod['extra_context'] = features
            
            debug("Adding new node")
            kwargs.update(**mod)
            debug("node added")
            
            node_obj, created = models.Node.objects.get_or_create(
                                        nodeId=nodeId, defaults=kwargs)
            for k,v in mod.items():
                node_obj.__setattr__(k, v)

            new_local_ids.append(nodeId)
            node_obj.save()
            debug("node saved")
        
        self_am.connected_node_set.add(node_obj)
        node_obj.save()
    
    debug("*** All local nodes")
    for n in self_am.local_node_set.filter():
        debug("    %s" % n.nodeId)
    
    debug("*** All old local nodes")
    for n in self_am.local_node_set.exclude(nodeId__in=new_local_ids):
        debug("    %s" % n.nodeId)

    debug("*** All old local moved nodes")
    for n in self_am.local_node_set.filter(nodeId__in=new_remote_ids):
        debug("    %s" % n.nodeId)

    # delete all old local nodes
    self_am.local_node_set.exclude(nodeId__in=new_local_ids).delete()
    
    debug("*** All local nodes now")
    for n in self_am.local_node_set.filter():
        debug("    %s" % n.nodeId)

    # Remove stale remote nodes
    [self_am.remote_node_set.remove(n) for n in self_am.remote_node_set.exclude(nodeId__in=new_remote_ids)]
    
    debug("*** All connected nodes")
    for n in self_am.connected_node_set.filter():
        debug("    %s" % n.nodeId)
    
    debug("*** All now unconnected nodes")
    for n in self_am.connected_node_set.exclude(
                nodeId__in=new_local_ids).exclude(
                    nodeId__in=new_remote_ids):
        debug("    %s" % n.nodeId)

    # Remove Unconnected nodes
    [self_am.connected_node_set.remove(n)
        for n in self_am.connected_node_set.exclude(
                    nodeId__in=new_local_ids).exclude(
                        nodeId__in=new_remote_ids)]
    
    debug("*** New connected nodes")
    for n in self_am.connected_node_set.filter():
        debug("    %s" % n.nodeId)

    # Delete unconnected nodes that no AM is connected to
    debug("*** Deleting nodes")
    for n in models.Node.objects.annotate(
        num_cnxns=Count('connected_am_set')).filter(
            num_cnxns=0):
        debug("    %s" % n.nodeId)
    
    models.Node.objects.annotate(
        num_cnxns=Count('connected_am_set')).filter(
            num_cnxns=0).delete()
    
    # In the second iteration create all the interfaces
    interfaces = tree.findall("//{%s}interfaceEntry" % ns)

    # list of interfaces added
    new_iface_ids = []
    new_ifaces = []
    for interface in interfaces:
        nodeId = parent_map[interface].findtext("{%s}nodeId" % ns)
        debug("*** Getting connected node %s" % nodeId)
        node_obj = self_am.connected_node_set.get(pk=nodeId)
        
        portNum = int(interface.findtext("{%s}port" % ns))
        debug("<0> %s" % portNum)
        
        # check if the iface exists
        try:
            iface_obj, created = \
                    models.Interface.objects.get_or_create(portNum=portNum,
                                            ownerNode__nodeId=nodeId,
                                            defaults={'ownerNode': node_obj})
        except models.Interface.MultipleObjectsReturned, e:
            print "Found duplicate iface for node %s, port %s" % (nodeId, portNum)
            models.Interface.objects.filter(portNum=portNum,
                                            ownerNode__nodeId=nodeId).delete()
            iface_obj, created = \
                    models.Interface.objects.get_or_create(portNum=portNum,
                                            ownerNode__nodeId=nodeId,
                                            defaults={'ownerNode': node_obj})
        
        new_iface_ids.append(iface_obj.id)
        new_ifaces.append(iface_obj)
        iface_obj.save()
        debug("+++++ Added interface: id %s port %s node %s" % (iface_obj.id, iface_obj.portNum, iface_obj.ownerNode))
        debug("Iface new: %s" % created)
    
    # delete extra ifaces: only those whom this AM created
    for i in models.Interface.objects.filter(
        ownerNode__aggMgr=self_am).exclude(
            id__in=new_iface_ids):
        debug("Print deleting iface: %s" % i)

    models.Interface.objects.filter(
        ownerNode__aggMgr=self_am).exclude(
            id__in=new_iface_ids).delete()
    
    # In the third iteration, add all the remote connections
    for interface, iface_obj in zip(interfaces, new_ifaces):
        # get the remote ifaces
        other_nodeIDs = interface.findall("{%s}remoteNodeId" % ns)
        other_ports = interface.findall("{%s}remotePort" % ns)

        debug("<1> nodes:%s ports:%s" % (other_nodeIDs, other_ports))

        nodes_ports = zip(other_nodeIDs, other_ports)
        remote_iface_ids = []
        src_link_ids = []
        dst_link_ids = []
        for remote_node_id_elem, remote_port_elem in nodes_ports:
            # get the remote node object
            id = remote_node_id_elem.text
            
            # get the remote interface at that remote node
            num = int(remote_port_elem.text)
            debug("<8> %s %s" % (num, id))
            
            try:
                remote_iface_obj = models.Interface.objects.get(portNum=num,
                                                                ownerNode__nodeId=id,
                                                                )
            except models.Interface.DoesNotExist, e:
                print "XML malformed. Remote iface for node id %s and port num %s does not exist." % (id, num)
                continue
            
            remote_iface_ids.append(remote_iface_obj.id)
            
            # get the link or create one if it doesn't exist
            link, created = models.Link.objects.get_or_create(
                                src=iface_obj, dst=remote_iface_obj)
            link.save()
            src_link_ids.append(link.id)
            
            link, created = models.Link.objects.get_or_create(
                                dst=iface_obj, src=remote_iface_obj)
            link.save()
            dst_link_ids.append(link.id)

            debug("<3>"); debug(id); debug(num)
            
        # delete old links
        iface_obj.src_link_set.exclude(id__in=src_link_ids).delete()
        iface_obj.dst_link_set.exclude(id__in=dst_link_ids).delete()

    # parse the flowspace
    fs_entries = tree.findall("*/{%s}flowSpaceEntry" % ns)
    debug(fs_entries)

    # add all of them
    for fs in fs_entries:
        # parse the flowspace
        p1 = lambda name: fs.findtext("{%s}%s" % (name, ns))
        
        p = lambda x: p1(x) if (p1(x)) else "*"
        
        models.FlowSpace.objects.get_or_create(
                                policy=p("policy"),
                                dl_src=p("dl_src"),
                                dl_dst=p("dl_dst"),
                                dl_type=p("dl_type"),
                                vlan_id=p("vlan_id"),
                                nw_src=p("ip_src"),
                                nw_dst=p("ip_dst"),
                                nw_proto=p("ip_proto"),
                                tp_src=p("tp_src"),
                                tp_dst=p("tp_dst"))

#def update_rspec_old(self_am):
#    '''
#    Read and parse the RSpec specifying all 
#    nodes from the aggregate manager using the E-GENI
#    RSpec
#    '''
#
#    rspec = get_rspec(self_am.url)
#    
#    rspecdoc = minidom.parseString(rspec)
#    
#    # create the context
#    rspec=rspecdoc.childNodes[0]
#    ns_uri = rspec.namespaceURI
#    
#    # create a context
#    context = xpath.Context.Context(rspec, 1, 1, 
#                                    processorNss={"tns": ns_uri})
#    
#    # Get all the nodes
#    nodes = xpath.Evaluate("*/tns:node", context=context)
#    
#    # list of node ids added
#    new_local_ids = []
#    new_remote_ids = []
#    
#    debug("-----My AM id: %s" %  self_am.id)
#    
#    # In the first iteration create all the nodes
#    for node in nodes:
#        # move the context to the current node
#        context.setNodePosSize((node, 1, 1))
#
#        # get the node ID string
#        nodeId = xpath.Evaluate("string(tns:nodeId)", context=context)
#        node_type = xpath.Evaluate("name(..)", context=context)
#        
#        kwargs = {'nodeId': nodeId,
#                  'img_url': OFSWITCH_DEFAULT_IMG,
#                  }
#
#        if(node_type == 'tns:remoteEntry'):
#            remoteType = xpath.Evaluate("string(../tns:remoteType)", context=context)
#            remoteURL = xpath.Evaluate("string(../tns:remoteURL)", context=context)
#            
#            # check if this clearinghouse knows about this AM
#            try:
#                am = models.AggregateManager.objects.get(url=remoteURL)
#            
#            # Nope we don't know about the remote AM
#            except models.AggregateManager.DoesNotExist:
#                
#                debug("+++++ Adding remote out CH Node %s" % nodeId)
#                
#                mod = {'type':remoteType,
#                       'remoteURL':remoteURL,
#                       'name': nodeId,
#                       'is_remote':True}
#                kwargs.update(**mod)
#                
#                node_obj, created = models.Node.objects.get_or_create(
#                                            nodeId=nodeId, defaults=kwargs)
#                for k,v in mod.items():
#                    node_obj.__setattr__(k, v)
#                    
#                node_obj.save()
#                
#                self_am.remote_node_set.add(node_obj)
#                new_remote_ids.append(nodeId)
#            
#            # We do know about the remote AM
#            else:
#                if remoteURL == self_am.URL:
#                    raise Exception("Remote URL is my URL, but entry is remote.")
#                
#                debug("+++++ Adding remote in CH Node %s" % nodeId)
#
#                mod = {'type':remoteType,
#                       'remoteURL':remoteURL,
#                       'aggMgr':am,
#                       'name': nodeId,
#                       'is_remote':False}
#                kwargs.update(**mod)
#                
#                node_obj, created = models.Node.objects.get_or_create(
#                                            nodeId=nodeId, defaults=kwargs)
#                for k,v in mod.items():
#                    node_obj.__setattr__(k, v)
#
#                node_obj.save()
#                self_am.remote_node_set.add(node_obj)
#                new_remote_ids.append(nodeId)
#        
#        # Entry controlled by this AM
#        else:
#            debug("+++++ Adding local Node %s" % nodeId)
#
#            mod = {'type':models.Node.TYPE_OF,
#                   'remoteURL':self_am.url,
#                   'aggMgr':self_am,
#                   'name': nodeId,
#                   'is_remote':False}
#            debug("Adding new node")
#            kwargs.update(**mod)
#            debug("node added")
#            
#            node_obj, created = models.Node.objects.get_or_create(
#                                        nodeId=nodeId, defaults=kwargs)
#            for k,v in mod.items():
#                node_obj.__setattr__(k, v)
#
#            new_local_ids.append(nodeId)
#            node_obj.save()
#            debug("node saved")
#        
#        self_am.connected_node_set.add(node_obj)
#        node_obj.save()
#    
#    debug("*** All local nodes")
#    for n in self_am.local_node_set.filter():
#        debug("    %s" % n.nodeId)
#    
#    debug("*** All old local nodes")
#    for n in self_am.local_node_set.exclude(nodeId__in=new_local_ids):
#        debug("    %s" % n.nodeId)
#
#    debug("*** All old local moved nodes")
#    for n in self_am.local_node_set.filter(nodeId__in=new_remote_ids):
#        debug("    %s" % n.nodeId)
#
#    # delete all old local nodes
#    self_am.local_node_set.exclude(nodeId__in=new_local_ids).delete()
#    self_am.local_node_set.filter(nodeId__in=new_remote_ids).delete()
#    
#    debug("*** All new nodes")
#    for n in self_am.local_node_set.filter():
#        debug("    %s" % n.nodeId)
#
#    # Remove stale remote nodes
#    [self_am.remote_node_set.remove(n) for n in self_am.remote_node_set.exclude(nodeId__in=new_remote_ids)]
#    [self_am.remote_node_set.remove(n) for n in self_am.remote_node_set.filter(nodeId__in=new_local_ids)]
#    
#    debug("*** All connected nodes")
#    for n in self_am.connected_node_set.filter():
#        debug("    %s" % n.nodeId)
#    
#    debug("*** All old connected nodes")
#    for n in self_am.connected_node_set.exclude(
#                nodeId__in=new_local_ids).exclude(
#                    nodeId__in=new_remote_ids):
#        debug("    %s" % n.nodeId)
#
#    # Remove Unconnected nodes
#    [self_am.connected_node_set.remove(n)
#        for n in self_am.connected_node_set.exclude(
#                    nodeId__in=new_local_ids).exclude(
#                        nodeId__in=new_remote_ids)]
#    
#    debug("*** New connected nodes")
#    for n in self_am.connected_node_set.filter():
#        debug("    %s" % n.nodeId)
#
#    # Delete unconnected nodes that no AM is connected to
#    debug("*** Deleting nodes")
#    for n in models.Node.objects.annotate(
#        num_cnxns=Count('connected_am_set')).filter(
#            num_cnxns=0):
#        debug("    %s" % n.nodeId)
#    
#    models.Node.objects.annotate(
#        num_cnxns=Count('connected_am_set')).filter(
#            num_cnxns=0).delete()
#    
#    # In the second iteration create all the interfaces and flowspaces
#    context.setNodePosSize((rspec, 1, 1))
#    interfaces = xpath.Evaluate("//tns:interfaceEntry", context=context)
#    # list of interfaces added
#    new_iface_ids = []
#    for interface in interfaces:
#        # move the context
#        context.setNodePosSize((interface, 1, 1))
#        nodeId = xpath.Evaluate("string(../tns:nodeId)", context=context)
#        debug("*** Getting connected node %s" % nodeId)
#        node_obj = self_am.connected_node_set.get(pk=nodeId)
#        
#        portNum = int(xpath.Evaluate("number(tns:port)", context=context))
#        debug("<0> %s" % portNum)
#        
#        # check if the iface exists
#        iface_obj, created = \
#            models.Interface.objects.get_or_create(portNum=portNum,
#                                            ownerNode__nodeId=nodeId,
#                                            defaults={'ownerNode': node_obj})
#        
#        new_iface_ids.append(iface_obj.id)
#        
#        if not created:
#            iface_obj.ownerNode = node_obj
#            
##            # get the flowspace entries
##            fs_entries = xpath.Evaluate("tns:flowSpaceEntry", context=context)
##            debug(fs_entries)
##
##            # add all of them
##            interface.flowspace_set.all().delete()
##            for fs in fs_entries:
##                context.setNodePosSize((fs, 1, 1))
##                # parse the flowspace
##                p1 = lambda name: xpath.Evaluate("string(tns:%s)" % name,
##                                                 context=context)
##                
##                p = lambda x: p1(x) if (p1(x)) else "*"
##                
##                interface.flowspace_set.create(policy=p("policy"),
##                                               dl_src=p("dl_src"),
##                                               dl_dst=p("dl_dst"),
##                                               dl_type=p("dl_type"),
##                                               vlan_id=p("vlan_id"),
##                                               nw_src=p("ip_src"),
##                                               nw_dst=p("ip_dst"),
##                                               nw_proto=p("ip_proto"),
##                                               tp_src=p("tp_src"),
##                                               tp_dst=p("tp_dst"),
##                                               interface=iface)
#    
#    # delete extra ifaces: only those whom this AM created
#    models.Interface.objects.exclude(
#        id__in=new_iface_ids).filter(
#            ownerNode__aggMgr=self_am).delete()
#    
#    # In the third iteration, add all the remote connections
#    for interface in interfaces:
#        # move the context
#        context.setNodePosSize((interface, 1, 1))
#        nodeId = xpath.Evaluate("string(../tns:nodeId)", context=context)
#        portNum = int(xpath.Evaluate("number(tns:port)", context=context))
#        iface_obj = models.Interface.objects.get(portNum__exact=portNum,
#                                                 ownerNode__nodeId=nodeId,
#                                                 )
#        
#        # get the remote ifaces
#        other_nodeIDs = xpath.Evaluate("tns:remoteNodeId", context=context)
#        other_ports = xpath.Evaluate("tns:remotePort", context=context)
#
#        debug("<1> nodes:%s ports:%s" % (other_nodeIDs, other_ports))
#
#        other_ports.reverse()
#        remote_iface_ids = []
#        for nodeID in other_nodeIDs:
#            # get the remote node object
#            context.setNodePosSize((nodeID, 1, 1))
#            id = xpath.Evaluate("string()", context=context)
#            
#            # get the remote interface at that remote node
#            context.setNodePosSize((other_ports.pop(), 1, 1))
#            num = int(xpath.Evaluate("number()", context=context))
#            debug("<8> %s %s" % (num, id))
#            
#            try:
#                remote_iface_obj = models.Interface.objects.get(portNum=num,
#                                                                ownerNode__nodeId=id,
#                                                                )
#            except models.Interface.DoesNotExist, e:
#                print "XML malformed. Remote iface for node id %s and port num %s does not exist." % (id, num)
#                continue
#            
#            remote_iface_ids.append(remote_iface_obj.id)
#            
#            # get the link or create one if it doesn't exist
#            link, created = models.Link.objects.get_or_create(
#                                src=iface_obj, dst=remote_iface_obj)
#            link.save()
#            
#            # add the connection
#            debug("<3>"); debug(id); debug(num)
#            
#        # remove old connections
#        iface_obj.remoteIfaces.exclude(id__in=remote_iface_ids).delete()
#
#    # parse the flowspace
#    context.setNodePosSize((rspec, 1, 1))    
#    fs_entries = xpath.Evaluate("tns:flowSpaceEntry", context=context)
#    debug(fs_entries)
#
#    # add all of them
#    for fs in fs_entries:
#        context.setNodePosSize((fs, 1, 1))
#        
#        # parse the flowspace
#        p1 = lambda name: xpath.Evaluate("string(tns:%s)" % name,
#                                         context=context)
#        
#        p = lambda x: p1(x) if (p1(x)) else "*"
#        
#        # TODO Finish up this stuff here
#        
#        models.FlowSpace.objects.get_or_create(
#                                policy=p("policy"),
#                                dl_src=p("dl_src"),
#                                dl_dst=p("dl_dst"),
#                                dl_type=p("dl_type"),
#                                vlan_id=p("vlan_id"),
#                                nw_src=p("ip_src"),
#                                nw_dst=p("ip_dst"),
#                                nw_proto=p("ip_proto"),
#                                tp_src=p("tp_src"),
#                                tp_dst=p("tp_dst"))

# Unit test
#init()
#get_rspec("http://171.67.75.2:12346")
#add_slice('slice3')
