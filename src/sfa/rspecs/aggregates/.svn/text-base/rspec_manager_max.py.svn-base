#!/usr/bin/python

from sfa.util.rspec import Rspec
import sys
import pdb
from sfa.util.misc import *
from sfa.util.rspec import *
from sfa.util.specdict import *
from sfa.util.faults import *
from sfa.util.storage import *
from sfa.util.policy import Policy
from sfa.util.debug import log
from sfa.server.aggregate import Aggregates
from sfa.server.registry import Registries
from sfa.util.faults import *

import xml.dom.minidom

SFA_MAX_CONF_FILE = '/etc/sfa/max_allocations'
SFA_MAX_DEFAULT_RSPEC = '/etc/sfa/max_physical.xml'
SFA_MAX_CANNED_RSPEC = '/etc/sfa/max_physical_canned.xml'

topology = {}

class GeniOutOfResource(GeniFault):
    def __init__(self, interface):
        faultString = "Interface " + interface + " not available"
        GeniFault.__init__(self, 100, faultString, '')

class GeniNoPairRspec(GeniFault):
    def __init__(self, interface, interface2):
        faultString = "Interface " + interface + " should be paired with " + interface2
        GeniFault.__init__(self, 100, faultString, '')

# Returns a mapping from interfaces to the nodes they lie on and their peer interfaces
# i -> node,i_peer

def get_interface_map():
    r = Rspec()
    r.parseFile(SFA_MAX_DEFAULT_RSPEC)
    rspec = r.toDict()
    capacity = rspec['rspec']['capacity']
    netspec = capacity[0]['netspec'][0]
    linkdefs = {}
    for n in netspec['nodespec']:
        ifspecs = n['ifspec']
        nodename = n['node']
        for i in ifspecs:
            ifname = i['name']
            linkid = i['linkid']

            if (linkdefs.has_key(linkid)):
                linkdefs[linkid].extend([(nodename,ifname)])
            else:
                linkdefs[linkid]=[(nodename,ifname)]
    
    # topology maps interface x interface -> link,node1,node2
    topology={}

    for k in linkdefs.keys():
        (n1,i1) = linkdefs[k][0]
        (n2,i2) = linkdefs[k][1]

        topology[i1] = (n1, i2)
        topology[i2] = (n2, i1)
        

    return topology    

    
def allocations_to_rspec(allocations):
    rspec = xml.dom.minidom.parse(SFA_MAX_DEFAULT_RSPEC)
    req = rspec.firstChild.appendChild(rspec.createElement("request"))
    for (iname,ip) in allocations:
        ifspec = req.appendChild(rspec.createElement("ifspec"))
        ifspec.setAttribute("name","tns:"+iname)
        ifspec.setAttribute("ip",ip)

    return rspec.toxml()
        
    
def if_endpoints(ifs):
    nodes=[]
    for l in ifs:
        nodes.extend(topology[l][0])
    return nodes

def lock_state_file():
    # Noop for demo
    return True

def unlock_state_file():
    return True
    # Noop for demo

def read_alloc_dict():
    alloc_dict={}
    rows = open(SFA_MAX_CONF_FILE).read().split('\n')
    for r in rows:
        columns = r.split(' ')
        if (len(columns)==2):
            hrn = columns[0]
            allocs = columns[1].split(',')
            ipallocs = map(lambda alloc:alloc.split('/'), allocs)
            alloc_dict[hrn]=ipallocs
    return alloc_dict

def commit_alloc_dict(d):
    f = open(SFA_MAX_CONF_FILE, 'w')
    for hrn in d.keys():
        columns = d[hrn]
        ipcolumns = map(lambda x:"/".join(x), columns)
        row = hrn+' '+','.join(ipcolumns)+'\n'
        f.write(row)
    f.close()

def collapse_alloc_dict(d):
    ret = []
    for k in d.keys():
        ret.extend(d[k])
    return ret


def alloc_links(api, hrn, links_to_add, links_to_drop):
    slicename=hrn_to_pl_slicename(hrn)
    for (iface,ip) in links_to_add:
        node = topology[iface][0][0]
        try:
            api.plshell.AddSliceTag(api.plauth, slicename, "ip_addresses", ip, node)
            api.plshell.AddSliceTag(api.plauth, slicename, "vsys", "getvlan", node)
        except Exception: 
            # Probably a duplicate tag. XXX July 21
            pass
    return True

def alloc_nodes(api,hrn, requested_ifs):
    requested_nodes = if_endpoints(requested_ifs)
    create_slice_max_aggregate(api, hrn, requested_nodes)

# Taken from slices.py

def create_slice_max_aggregate(api, hrn, nodes):
    # Get the slice record from geni
    global topology
    topology = get_interface_map()
    slice = {}
    registries = Registries(api)
    registry = registries[api.hrn]
    credential = api.getCredential()
    records = registry.resolve(credential, hrn)
    for record in records:
        if record.get_type() in ['slice']:
            slice = record.as_dict()
    if not slice:
        raise RecordNotFound(hrn)   

    # Make sure slice exists at plc, if it doesnt add it
    slicename = hrn_to_pl_slicename(hrn)
    slices = api.plshell.GetSlices(api.plauth, [slicename], ['node_ids'])
    if not slices:
        parts = slicename.split("_")
        login_base = parts[0]
        # if site doesnt exist add it
        sites = api.plshell.GetSites(api.plauth, [login_base])
        if not sites:
            authority = get_authority(hrn)
            site_records = registry.resolve(credential, authority)
            site_record = {}
            if not site_records:
                raise RecordNotFound(authority)
            site_record = site_records[0]
            site = site_record.as_dict()
                
            # add the site
            site.pop('site_id')
            site_id = api.plshell.AddSite(api.plauth, site)
        else:
            site = sites[0]
            
        slice_fields = {}
        slice_keys = ['name', 'url', 'description']
        for key in slice_keys:
            if key in slice and slice[key]:
                slice_fields[key] = slice[key]  
        api.plshell.AddSlice(api.plauth, slice_fields)
        slice = slice_fields
        slice['node_ids'] = 0
    else:
        slice = slices[0]    

    # get the list of valid slice users from the registry and make 
    # they are added to the slice 
    researchers = record.get('researcher', [])
    for researcher in researchers:
        person_record = {}
        person_records = registry.resolve(credential, researcher)
        for record in person_records:
            if record.get_type() in ['user']:
                person_record = record
        if not person_record:
            pass
        person_dict = person_record.as_dict()
        persons = api.plshell.GetPersons(api.plauth, [person_dict['email']],
                                         ['person_id', 'key_ids'])

        # Create the person record 
        if not persons:
            person_id=api.plshell.AddPerson(api.plauth, person_dict)

            # The line below enables the user account on the remote aggregate
            # soon after it is created.
            # without this the user key is not transfered to the slice
            # (as GetSlivers returns key of only enabled users),
            # which prevents the user from login to the slice.
            # We may do additional checks before enabling the user.

            api.plshell.UpdatePerson(api.plauth, person_id, {'enabled' : True})
            key_ids = []
        else:
            key_ids = persons[0]['key_ids']

        api.plshell.AddPersonToSlice(api.plauth, person_dict['email'],
                                     slicename)        

        # Get this users local keys
        keylist = api.plshell.GetKeys(api.plauth, key_ids, ['key'])
        keys = [key['key'] for key in keylist]

        # add keys that arent already there 
        for personkey in person_dict['keys']:
            if personkey not in keys:
                key = {'key_type': 'ssh', 'key': personkey}
                api.plshell.AddPersonKey(api.plauth, person_dict['email'], key)

    # find out where this slice is currently running
    nodelist = api.plshell.GetNodes(api.plauth, slice['node_ids'],
                                    ['hostname'])
    hostnames = [node['hostname'] for node in nodelist]

    # remove nodes not in rspec
    deleted_nodes = list(set(hostnames).difference(nodes))
    # add nodes from rspec
    added_nodes = list(set(nodes).difference(hostnames))

    api.plshell.AddSliceToNodes(api.plauth, slicename, added_nodes) 
    api.plshell.DeleteSliceFromNodes(api.plauth, slicename, deleted_nodes)

    return 1


def get_rspec(api, hrn):
    # Eg. config line:
    # plc.princeton.sapan vlan23,vlan45

    allocations = read_alloc_dict()
    if (hrn and allocations.has_key(hrn)):
            ret_rspec = allocations_to_rspec(allocations[hrn])
    else:
        ret_rspec = open(SFA_MAX_CANNED_RSPEC).read()

    return (ret_rspec)


def create_slice(api, hrn, rspec_xml):
    global topology
    topology = get_interface_map()

    # Check if everything in rspec is either allocated by hrn
    # or not allocated at all.
    r = Rspec()
    r.parseString(rspec_xml)
    rspec = r.toDict()

    lock_state_file()

    allocations = read_alloc_dict()
    requested_allocations = rspec_to_allocations (rspec)
    current_allocations = collapse_alloc_dict(allocations)
    try:
        current_hrn_allocations=allocations[hrn]
    except KeyError:
        current_hrn_allocations=[]

    # Check request against current allocations
    requested_interfaces = map(lambda(elt):elt[0], requested_allocations)
    current_interfaces = map(lambda(elt):elt[0], current_allocations)
    current_hrn_interfaces = map(lambda(elt):elt[0], current_hrn_allocations)

    for a in requested_interfaces:
        if (a not in current_hrn_interfaces and a in current_interfaces):
            raise GeniOutOfResource(a)
        if (topology[a][1] not in requested_interfaces):
            raise GeniNoPairRspec(a,topology[a][1])
    # Request OK

    # Allocations to delete
    allocations_to_delete = []
    for a in current_hrn_allocations:
        if (a not in requested_allocations):
            allocations_to_delete.extend([a])

    # Ok, let's do our thing
    alloc_nodes(api, hrn, requested_interfaces)
    alloc_links(api, hrn, requested_allocations, allocations_to_delete)
    allocations[hrn] = requested_allocations
    commit_alloc_dict(allocations)

    unlock_state_file()

    return True

def rspec_to_allocations(rspec):
    ifs = []
    try:
        ifspecs = rspec['rspec']['request'][0]['ifspec']
        for l in ifspecs:
            ifs.extend([(l['name'].replace('tns:',''),l['ip'])])
    except KeyError:
        # Bad Rspec
        pass
    return ifs

def main():
    t = get_interface_map()
    r = Rspec()
    rspec_xml = open(sys.argv[1]).read()
    #get_rspec(None,'foo')
    create_slice(None, "plc.princeton.sap0", rspec_xml)
    
if __name__ == "__main__":
    main()
