# Copyright (c) 2008 The Board of Trustees of The Leland Stanford
# Junior University
# 
# We are making the OpenFlow specification and associated documentation
# (Software) available for public use and benefit with the expectation
# that others will use, modify and enhance the Software and contribute
# those enhancements back to the community. However, since we would
# like to make the Software available for broadest use, with as few
# restrictions as possible permission is hereby granted, free of
# charge, to any person obtaining a copy of this Software to deal in
# the Software under the copyrights without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 
# The name and trademarks of copyright holder(s) may NOT be used in
# advertising or publicity pertaining to the Software or any
# derivatives without specific, written prior permission.

from omnilib.omnispec.omnispec import OmniSpec, OmniResource
import xml.etree.ElementTree as ET
from copy import deepcopy
import sys

def can_translate(rspec):
    return '<rspec type="openflow">' in rspec


def rspec_to_omnispec(urn, rspec):
    ospec = OmniSpec("rspec_of", urn)
    ospec = make_skeleton_of_ospec(ospec)
    doc = ET.fromstring(rspec)
    #sys.stderr.write(rspec)
    for network in doc.findall('network'):             
        net_name = network.get('name')
        switches = network.findall('switches')[0]
        swmap = {}
        for switch in switches.findall('switch'):
            # convert:
            #       "<switch urn="urn:publicid:IDN+openflow:stanford+switch:0" />"
            urn = switch.get('urn')
            # switchname = "stanford_network:switch:00:00:00:23:01:35:a5:5d"
            switchname = net_name + ':' + urn.split('+')[1]
            switchname += ':' + urn.split('+')[2].split(':')[1]
            s = OmniResource(switchname, "OpenFlow Switch" ,'switch') 

            options=['dl_src', 'dl_dst', 'dl_type', 'vlan_id', 'nw_src',\
                    'nw_dst', 'nw_proto', 'tp_src', 'tp_dst']
            
            for opt in options:
                s['options'][opt] = 'from=*, to=*'

            swmap[urn] = s
            ospec.add_resource(urn, s)
            
            for port in switch.findall('port'):
                port_urn = port.get('urn')
                port = 'port:' + port_urn.split('port:')[-1]
                swmap[urn]['options'][port] = "switch:* port:*"
                
        links = network.findall('links')[0]
        for link in links.findall('link'):
            # convert:
            #       <link
            #       src_urn="urn:publicid:IDN+openflow:stanford+switch:0+port:0
            #       dst_urn="urn:publicid:IDN+openflow:stanford+switch:1+port:0
            #       />
            _,domain,src_switch,src_port = link.get('src_urn').split('+')
            _,_,dst_switch,dst_port = link.get('dst_urn').split('+')
            
            switch_urn = "urn:publicid:IDN+" + domain + "+" + src_switch
            swmap[switch_urn]['options'][src_port] = dst_switch + " " + dst_port
            #sw_ports = swmap[switch_urn]['misc'].setdefault('ports', {})
            #sw_ports[src_port] = dst_switch + " " + dst_port
            
            #swmap[switch_urn]['options'][src_port] = "from=%s, to=%s" % (src_port.split(":")[-1], src_port.split(":")[-1])

    return ospec

def omnispec_to_rspec(omnispec, filter_allocated):
    # Todo: 
    # - combine flowspaces where they are identical for multiple ports/switches
    # If you reserved all the ports, just list the switch
    # else do not list the switch and just list the ports (which we now do always)
    # - Take ports out of options for code cleanup
    # - Clean up how you split a switch between flowspaces
    # - Allow a flowspace in the ospec that spans switches
    
    # Load up information about all the resources
    user = {}
    project = {}
    slice = {}
    flowspaces = []

    ports={}
    
    # parse though each item; collecting ports as we go
    for urn, r in omnispec.get_resources().items():
        # not sure about matching on urn here: 
        # why not type?  - Rob
        if '+user+sliceinfo' in urn:            
            user['firstname'] = r['options']['firstname']
            user['lastname'] = r['options']['lastname']
            user['email'] = r['options']['email']
            user['fv_password'] = r['options']['fv_password']
            
            project['project_name'] = r['options']['project_name']
            project['project_description'] = r['options']['project_description']
            
            slice['slice_name'] = r['options']['slice_name']
            slice['slice_description'] = r['options']['slice_description']
            slice['controller_url'] = r['options']['controller_url']


        if r['type'] == 'switch':
            if not r.get_allocate():
                continue       
            
            ports = []
            for (key,val) in r['options'].items():
                if key.startswith("port:"):
                    ports.append(key)
            for port in ports:
                r['options'].pop(port)
            
            
            # Okay, consider this switch part of a flowspace
            flowspace = {}

            # To let a user describe diff flowspace for
            # diff ports on a switch, they have to 
            # copy the resource def for that switch
            # and then edit the urn to something unique
            # so it looks like a unique ospec resource.
            # Then here we need to re extract the switch URN
            partInd = urn.find('+part:')
            if partInd > 0:
#                print "URN was %s and will be %s" % (urn, urn[:partInd])
                urn = urn[:partInd]
            flowspace['switch'] = urn
            
            flowspace['options'] = []
            
            for (key,val) in r['options'].items():
                #sys.stderr.write("val = %s \n" % val)
                vfrom,vto = val.split(",")
                vfrom = vfrom.strip().replace("from=",'')
                vto = vto.strip().replace("to=",'')
                flowspace['options'].append((key,vfrom,vto))

            # Add an option for each port listed as part of this flowspace.
            # Ideally we'd notice if this is all ports on the switch and just list the switch
            # itself.
            # Note that you must list ports explicitly in the ospec or you get nothing
            for port in ports:                
                # Create an option named 'port' with 'from' port urn and to '*'
                # where the 'to' will be dropped below cause it is '*' (ugly)
                # and the 'from' attrib will be renamed as 'urn' (uglier)
                flowspace['options'].append(("port", flowspace['switch'] + '+port:' + port.split(':')[-1], '*'))
            flowspaces.append(flowspace)



    # Now build the rspec
     
    root = ET.Element('resv_rspec')
    ET.SubElement(root, 'user', firstname=user['firstname'],lastname=user['lastname'], \
                           email=user['email'], password=user['fv_password'])
    ET.SubElement(root, 'project', name=project['project_name'], \
                              description=project['project_description'])
    ET.SubElement(root, 'slice', name=slice['slice_name'],\
                            description=slice['slice_description'],\
                            controller_url=slice['controller_url'])

    # Now write out each flowspace (which is per set of ports on a single switch)
    for flowspace in flowspaces:
        urn = flowspace['switch']
        flow = ET.SubElement(root, 'flowspace')

        # If we write out all the ports, then we don't need to write out the switch
        # More particularly, I think writing the switch and a subset of the port
        # gives you all the ports, which is wrong if the user only wanted some ports.
        # So since we currently never suppress writing out ports,
        # we can suppress the switch
        # Note it will be an error to list no ports
        # The _right_ thing is to notice if this is all ports for the switch,
        # in which case we should just list the switch. Else just list the ports.
#        ET.SubElement(flow, 'switch', urn=urn)

        # UGLY: Ensure ports are written before other options
        # Clearly ports should not be stored in 'options' any more...

        # Now the port 'options'. 
        for (name,vfrom,vto) in flowspace['options']:
            if name != "port":
                continue
            # If vfrom and vto are * then skip this row
            if vfrom == "*" and vto == "*":
                continue 
            opt = ET.SubElement(flow, name)
            # If only 1 is * then skip just the one
            if vfrom != "*": 
                # Ugly! The 'port' option has
                # only a urn tag not a from
                if name == "port":
                    opt.attrib['urn'] = vfrom
                else:
                    opt.attrib['from'] = vfrom
            if vto != "*": 
                opt.attrib['to'] = vto

        # Now the non-port 'options'. Note that 1 is the port in question
        for (name,vfrom,vto) in flowspace['options']:
            # If vfrom and vto are * then skip this row
            if name == "port":
                continue
            if vfrom == "*" and vto == "*":
                continue 
            opt = ET.SubElement(flow, name)
            # If only 1 is * then skip just the one
            if vfrom != "*": 
                # Ugly! The 'port' option has
                # only a urn tag not a from
                if name == "port":
                    opt.attrib['urn'] = vfrom
                else:
                    opt.attrib['from'] = vfrom
            if vto != "*": 
                opt.attrib['to'] = vto
            
    xml = ET.tostring(root)
    return xml

def make_skeleton_of_ospec(ospec):
    ''' Add resources for the client to reserve.

        Hacking it in here because Expedient assumes the caller will add them
        themselves.
    '''
    # setup a resource for fv_account
    user = OmniResource("sliceinfo","Slice information for FlowVisor Access",'user')
    # goes in <user>
    user['options']['firstname'] = 'John'
    user['options']['lastname'] = 'Doe'
    user['options']['email'] = 'jdoe@geni.net'
    user['options']['fv_password'] = 'slice_pass'
    # goes in <project>
    user['options']['project_name'] = 'Stanford Networking Group'
    user['options']['project_description'] = 'Internet performance research to ...'
    # goes in <slice>
    user['options']['slice_name'] = 'Crazy Load Balancing Experiment'
    user['options']['slice_description'] = 'Does crazy load balancing and plate spinning'
    user['options']['controller_url'] = 'tcp:unknown:6633'
    user_urn = 'urn:publicid:IDN+openflow:stanford+user+' + user.get_name()

    ospec.add_resource(user_urn, user)
    return ospec

def set_dpid_port(ports,dpid, port):
        if not dpid in ports:
                sys.stderr.write("Adding switch %s\n" % ( dpid))
                ports['dpid'] = {}
        if not port in ports['dpid']:
                sys.stderr.write("Adding port %s to switch %s\n" % ( port, dpid))
                ports['dpid'][port]=True
    

##### Example OpenFlow advertisement rspec from expedient
'''
<rspec type="openflow">
    <network name="Stanford" location="Stanford, CA, USA">
        <switches>
            <switch urn="urn:publicid:IDN+openflow:stanford+switch:0" >
                <port urn="urn:publicid:IDN+openflow:stanford+switch:0+port:0" />
                <port urn="urn:publicid:IDN+openflow:stanford+switch:0+port:1" />
            </switch>
            <switch urn="urn:publicid:IDN+openflow:stanford+switch:1" />
                <port urn="urn:publicid:IDN+openflow:stanford+switch:1+port:0" />
                <port urn="urn:publicid:IDN+openflow:stanford+switch:1+port:1" />
            <switch urn="urn:publicid:IDN+openflow:stanford+switch:2" />
                <port urn="urn:publicid:IDN+openflow:stanford+switch:2+port:0" />
                <port urn="urn:publicid:IDN+openflow:stanford+switch:2+port:1" />
                <port urn="urn:publicid:IDN+openflow:stanford+switch:2+port:2" />
                <port urn="urn:publicid:IDN+openflow:stanford+switch:2+port:3" />
            </switch>
        </switches>
        <links>
            <link
            src_urn="urn:publicid:IDN+openflow:stanford+switch:0+port:0"
            dst_urn="urn:publicid:IDN+openflow:stanford+switch:1+port:0"
            />
            <link
            src_urn="urn:publicid:IDN+openflow:stanford+switch:1+port:0"
            dst_urn="urn:publicid:IDN+openflow:stanford+switch:0+port:0"
            />
            <link
            src_urn="urn:publicid:IDN+openflow:stanford+switch:0+port:1"
            dst_urn="urn:publicid:IDN+openflow:stanford+switch:2+port:0"
            />
            <link
            src_urn="urn:publicid:IDN+openflow:stanford+switch:2+port:0"
            dst_urn="urn:publicid:IDN+openflow:stanford+switch:0+port:1"
            />
            <link
            src_urn="urn:publicid:IDN+openflow:stanford+switch:1+port:1"
            dst_urn="urn:publicid:IDN+openflow:stanford+switch:2+port:1"
            />
            <link
            src_urn="urn:publicid:IDN+openflow:stanford+switch:2+port:1"
            dst_urn="urn:publicid:IDN+openflow:stanford+switch:1+port:1"
            />
        </links>
    </network>
    <network name="Princeton" location="USA">
        <switches>
            <switch urn="urn:publicid:IDN+openflow:stanford+switch:3" >
                <port urn="urn:publicid:IDN+openflow:stanford+switch:3+port:0" />
            </switch>
            <switch urn="urn:publicid:IDN+openflow:stanford+switch:4" >
                <port urn="urn:publicid:IDN+openflow:stanford+switch:4+port:0" />
            </switch>
        </switches>
        <links>
            <link
            src_urn="urn:publicid:IDN+openflow:stanford+switch:3+port:0"
            dst_urn="urn:publicid:IDN+openflow:stanford+switch:4+port:0"
            />
            <link
            src_urn="urn:publicid:IDN+openflow:stanford+switch:4+port:0"
            dst_urn="urn:publicid:IDN+openflow:stanford+switch:3+port:0"
            />
        </links>
    </network>
</rspec>

specifies a triangular graph at the Stanford network and a single link
at the Princeton network
'''

#### Omnispec translation of above Ad RSpec:
'''
{
    "http://localhost:8001": {
        "urn": "urn:publicid:IDN+geni:gpo:gcf+am1+authority+am", 
        "type": "rspec_of", 
        "resources": {
            "urn:publicid:IDN+openflow:stanford+switch:2": {
                "name": "Stanford:openflow:stanford:2", 
                "misc": {}, 
                "allocate": false, 
                "allocated": false, 
                "type": "switch", 
                "options": {
                    "dl_type": "from=*, to=*", 
                    "port:1": "switch:1 port:1", 
                    "port:0": "switch:0 port:1", 
                    "port:3": "switch:* port:*", 
                    "nw_dst": "from=*, to=*", 
                    "port:2": "switch:* port:*", 
                    "dl_src": "from=*, to=*", 
                    "nw_proto": "from=*, to=*", 
                    "tp_dst": "from=*, to=*", 
                    "tp_src": "from=*, to=*", 
                    "dl_dst": "from=*, to=*", 
                    "nw_src": "from=*, to=*", 
                    "vlan_id": "from=*, to=*"
                }, 
                "description": "OpenFlow Switch"
            }, 
            "urn:publicid:IDN+openflow:stanford+switch:3": {
                "name": "Princeton:openflow:stanford:3", 
                "misc": {}, 
                "allocate": false, 
                "allocated": false, 
                "type": "switch", 
                "options": {
                    "dl_type": "from=*, to=*", 
                    "port:0": "switch:4 port:0", 
                    "nw_dst": "from=*, to=*", 
                    "dl_src": "from=*, to=*", 
                    "nw_proto": "from=*, to=*", 
                    "tp_dst": "from=*, to=*", 
                    "tp_src": "from=*, to=*", 
                    "dl_dst": "from=*, to=*", 
                    "nw_src": "from=*, to=*", 
                    "vlan_id": "from=*, to=*"
                }, 
                "description": "OpenFlow Switch"
            }, 
            "urn:publicid:IDN+openflow:stanford+switch:0": {
                "name": "Stanford:openflow:stanford:0", 
                "misc": {}, 
                "allocate": false, 
                "allocated": false, 
                "type": "switch", 
                "options": {
                    "dl_type": "from=*, to=*", 
                    "port:1": "switch:2 port:0", 
                    "port:0": "switch:1 port:0", 
                    "nw_dst": "from=*, to=*", 
                    "dl_src": "from=*, to=*", 
                    "nw_proto": "from=*, to=*", 
                    "tp_dst": "from=*, to=*", 
                    "tp_src": "from=*, to=*", 
                    "dl_dst": "from=*, to=*", 
                    "nw_src": "from=*, to=*", 
                    "vlan_id": "from=*, to=*"
                }, 
                "description": "OpenFlow Switch"
            }, 
            "urn:publicid:IDN+openflow:stanford+switch:1": {
                "name": "Stanford:openflow:stanford:1", 
                "misc": {}, 
                "allocate": false, 
                "allocated": false, 
                "type": "switch", 
                "options": {
                    "dl_type": "from=*, to=*", 
                    "port:1": "switch:2 port:1", 
                    "port:0": "switch:0 port:0", 
                    "nw_dst": "from=*, to=*", 
                    "dl_src": "from=*, to=*", 
                    "nw_proto": "from=*, to=*", 
                    "tp_dst": "from=*, to=*", 
                    "tp_src": "from=*, to=*", 
                    "dl_dst": "from=*, to=*", 
                    "nw_src": "from=*, to=*", 
                    "vlan_id": "from=*, to=*"
                }, 
                "description": "OpenFlow Switch"
            }, 
            "urn:publicid:IDN+openflow:stanford+user+sliceinfo": {
                "name": "sliceinfo", 
                "misc": {}, 
                "allocate": false, 
                "allocated": false, 
                "type": "user", 
                "options": {
                    "project_description": "Internet performance research to ...", 
                    "controller_url": "tcp:unknown:6633", 
                    "slice_name": "Crazy Load Balancing Experiment", 
                    "firstname": "John", 
                    "lastname": "Doe", 
                    "project_name": "Stanford Networking Group", 
                    "fv_password": "slice_pass", 
                    "slice_description": "Does crazy load balancing and plate spinning", 
                    "email": "jdoe@geni.net"
                }, 
                "description": "Slice information for FlowVisor Access"
            }, 
            "urn:publicid:IDN+openflow:stanford+switch:4": {
                "name": "Princeton:openflow:stanford:4", 
                "misc": {}, 
                "allocate": false, 
                "allocated": false, 
                "type": "switch", 
                "options": {
                    "dl_type": "from=*, to=*", 
                    "port:0": "switch:3 port:0", 
                    "nw_dst": "from=*, to=*", 
                    "dl_src": "from=*, to=*", 
                    "nw_proto": "from=*, to=*", 
                    "tp_dst": "from=*, to=*", 
                    "tp_src": "from=*, to=*", 
                    "dl_dst": "from=*, to=*", 
                    "nw_src": "from=*, to=*", 
                    "vlan_id": "from=*, to=*"
                }, 
                "description": "OpenFlow Switch"
            }
        }
    }
}

- Note that the port entries indicate the network topology. EG switch 4 port 0
is listed as "port:0": "switch:3 port:0", indicating that the port is connected to
switch 3 port 0

'''

##### Example reservation back to OpenFlow/Expedient
'''
    Parses the reservation RSpec and returns a tuple:
    (project_name, project_desc, slice_name, slice_desc, 
    controller_url, email, password, agg_slivers) where slivers
    is a list of (aggregate, slivers) tuples, and slivers is a dict suitable
    for use in the create_slice xml-rpc call of the opt-in manager.
    
    The reservation rspec looks like the following:
    
    <resv_rspec>
        <user
            firstname="John"
            lastname="Doe"
            email="john.doe@geni.net"
            password="slice_pass"
        />
        <project
            name="Stanford Networking Group"
            description="Internet performance research to ..."
        />
        <slice
            name="Crazy Load Balancer"
            description="Does this and that..."
            controller_url="tcp:controller.stanford.edu:6633"
        />
        <flowspace>
            <switch urn="urn:publicid:IDN+openflow:stanford+switch:0">
            <port urn="urn:publicid:IDN+openflow:stanford+switch:2+port:1">
            <port urn="urn:publicid:IDN+openflow:stanford+switch:2+port:2">
            <port urn="urn:publicid:IDN+openflow:stanford+switch:2+port:3">
            <dl_src from="22:33:44:55:66:77" to="22:33:44:55:66:77" />
            <dl_type from="0x800" to="0x800" />
            <vlan_id from="15" to="20" />
            <nw_src from="192.168.3.0" to="192.168.3.255" />
            <nw_dst from="192.168.3.0" to="192.168.3.255" />
            <nw_proto from="17" to="17" />
            <tp_src from="100" to="100" />
            <tp_dst from="100" />
        </flowspace>
        <flowspace>
            <switch urn="urn:publicid:IDN+openflow:stanford+switch:1">
            <tp_src from="100" to="100" />
            <tp_dst from="100" />
        </flowspace>
    </resv_rspec>
    
    Including a switch means all ports on that switch.
    OF stack will union your list of switches/ports/flowspaces as needed.
    So if you list both a switch AND some of its ports, then all ports on the switch
    are included. 

    Any missing fields from the flowspace mean wildcard. "*" should
    not be written - leave it out.
        
    All integers can be specified as hex or decimal.
    '''
#### Example OmniSpec that turns into the above reservation RSpec (approx)
'''
    "http://localhost:8001": {
        "urn": "urn:publicid:IDN+geni:gpo:gcf+am1+authority+am",
        "type": "rspec_of",
        "resources": {
            "urn:publicid:IDN+openflow:stanford+switch:2": {
                "name": "Stanford:openflow:stanford:2",
                "misc": {},
                "allocate": true,
                "allocated": false,
                "type": "switch",
                "options": {
                    "dl_type": "from=0x800, to=0x800",
                    "port:1": "switch:1 port:1",
                    "port:3": "switch:* port:*",
                    "port:2": "switch:* port:*",
                    "nw_dst": "from=192.168.3.0, to=192.168.3.255",
                    "dl_src": "from=22:33:44:55:66:77, to=22:33:44:55:66:77",
                    "nw_proto": "from=17, to=17",
                    "tp_dst": "from=100, to=*",
                    "tp_src": "from=100, to=100",
                    "dl_dst": "from=*, to=*",
                    "nw_src": "from=192.168.3.0, to=192.168.3.255",
                    "vlan_id": "from=15, to=20"
                },
                "description": "OpenFlow Switch"
            },
            "urn:publicid:IDN+openflow:stanford+switch:3": {
                "name": "Princeton:openflow:stanford:3",
                "misc": {},
                "allocate": false,
                "allocated": false,
                "type": "switch",
                "options": {
                    "dl_type": "from=*, to=*",
                    "port:0": "switch:4 port:0",
                    "nw_dst": "from=*, to=*",
                    "dl_src": "from=*, to=*",
                    "nw_proto": "from=*, to=*",
                    "tp_dst": "from=*, to=*",
                    "tp_src": "from=*, to=*",
                    "dl_dst": "from=*, to=*",
                    "nw_src": "from=*, to=*",
                    "vlan_id": "from=*, to=*"
                },
                "description": "OpenFlow Switch"
            },
            "urn:publicid:IDN+openflow:stanford+switch:0": {
                "name": "Stanford:openflow:stanford:0",
                "misc": {},
                "allocate": true,
                "allocated": false,
                "type": "switch",
                "options": {
                    "dl_type": "from=0x800, to=0x800",
                    "port:1": "switch:2 port:0",
                    "port:0": "switch:1 port:0",
                    "nw_dst": "from=192.168.3.0, to=192.168.3.255",
                    "dl_src": "from=22:33:44:55:66:77, to=22:33:44:55:66:77",
                    "nw_proto": "from=17, to=17",
                    "tp_dst": "from=100, to=*",
                    "tp_src": "from=100, to=100",
                    "dl_dst": "from=*, to=*",
                    "nw_src": "from=192.168.3.0, to=192.168.3.255",
                    "vlan_id": "from=15, to=20"
                },
                "description": "OpenFlow Switch"
            },
            "urn:publicid:IDN+openflow:stanford+switch:1": {
                "name": "Stanford:openflow:stanford:1",
                "misc": {},
                "allocate": true,
                "allocated": false,
                "type": "switch",
                "options": {
                    "dl_type": "from=*, to=*",
                    "port:1": "switch:2 port:1",
                    "port:0": "switch:0 port:0",
                    "nw_dst": "from=*, to=*",
                    "dl_src": "from=*, to=*",
                    "nw_proto": "from=*, to=*",
                    "tp_dst": "from=100, to=*",
                    "tp_src": "from=100, to=100",
                    "dl_dst": "from=*, to=*",
                    "nw_src": "from=*, to=*",
                    "vlan_id": "from=*, to=*"
                },
                "description": "OpenFlow Switch"
            },
            "urn:publicid:IDN+openflow:stanford+user+sliceinfo": {
                "name": "sliceinfo",
                "misc": {},
                "allocate": false,
                "allocated": false,
                "type": "user",
                "options": {
                    "project_description": "Internet performance research to ...",
                    "controller_url": "tcp:controller.stanford.edu:6633",
                    "slice_name": "Crazy Load Balancer",
                    "firstname": "John",
                    "lastname": "Doe",
                    "project_name": "Stanford Networking Group",
                    "fv_password": "slice_pass",
                    "slice_description": "Does this and that...",
                    "email": "john.doe@geni.net"
                },
                "description": "Slice information for FlowVisor Access"
            },
            "urn:publicid:IDN+openflow:stanford+switch:4": {
                "name": "Princeton:openflow:stanford:4",
                "misc": {},
                "allocate": false,
                "allocated": false,
                "type": "switch",
                "options": {
                    "dl_type": "from=*, to=*",
                    "port:0": "switch:3 port:0",
                    "nw_dst": "from=*, to=*",
                    "dl_src": "from=*, to=*",
                    "nw_proto": "from=*, to=*",
                    "tp_dst": "from=*, to=*",
                    "tp_src": "from=*, to=*",
                    "dl_dst": "from=*, to=*",
                    "nw_src": "from=*, to=*",
                    "vlan_id": "from=*, to=*"
                },
                "description": "OpenFlow Switch"
            }
        }
    }
}

Some notes on making reservations using Omnispecs:
- Mark allocate: true for all switches you want part of
- Remove any port: options that you do not want included as part of your reservation
- Be sure to fill out the sliceinfo section with your experiment, project, user info
---- particularly your controller hostname and port
- You must list at least 1 port per resource section
- If you want the same flowspace across 2 switches, you must duplicate the settings for each
switch/resource
- If you want to split a switch, with some ports in 1 flowspace and some in another,
then you must duplicate the resource section for that switch, and change
the URN (first line) of the resource (for at least parts 2+) to be [orig urn]+part:<unique ID>. EG
     .....+switch:1, and ...+switch:1+part:2, and ....+switch:1+part:ComplexFinalBit
Then, as usual, delete the ports to be excluded from each flowspace, set the appropriate options

'''
