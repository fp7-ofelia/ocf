#----------------------------------------------------------------------
# Copyright (c) 2010 Raytheon BBN Technologies
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and/or hardware specification (the "Work") to
# deal in the Work without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Work, and to permit persons to whom the Work
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Work.
#
# THE WORK IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE WORK OR THE USE OR OTHER DEALINGS
# IN THE WORK.
#----------------------------------------------------------------------

import xml.etree.ElementTree as ET
from omnilib.omnispec.omnispec import OmniSpec, OmniResource

# This is an Unbound Request RSpec for testing.
ONE_NODE_RSPEC = """
<rspec xmlns=\"http://protogeni.net/resources/rspec/0.2\">
  <node virtual_id=\"geni1\"
        virtualization_type=\"emulab-vnode\"
        startup_command=\"/bin/ls > /tmp/foo\">
  </node>" +\
</rspec>
"""

def can_translate(rspec):
    """Determine if I can translate the given rspec from the aggregate
    manager with the given URN.
     
    Returns True if it can be translated, False otherwise.
    
    """
    # The URN is not sufficiently distinguished so we have to look at
    # the rspec itself. We should really parse it and pull some
    # information out of the 'rspec' tag. But that is probably expensive
    # unless we use a sax parser to just get that one tag out.
    #
    # For now, do a simple string match.
    return 'http://www.protogeni.net/resources' in rspec

def pg_tag(tag):
    # The elementtree parser throws away namespace declarations.
    # Hardcoded for now, but...
    # TODO: use a different xml parser or some other way of preserving xmlns
    return '{http://www.protogeni.net/resources/rspec/0.2}' + tag

def add_options(ospec, root):
    onode = OmniResource("RandomNode", "Let Protogeni select available nodes for you", "RandomPC")
    misc = onode['misc']
    free = 0
    used = 0
    for res in root.findall(pg_tag('node')):
        if res.find(pg_tag('disk_image')) is None:
            continue
        if res.find(pg_tag('available')).text.lower() == 'false':
            used += 1
        else:
            free += 1
            
    misc['free nodes'] = free
    misc['used nodes'] = used
    options = onode['options']
    options['startup command'] = '/bin/ls > /dev/null'
    options['virtual'] = True
    options['number'] = 1
    options['os'] = 'FEDORA10-STD'
    ospec.add_resource('RandomNode', onode)

def add_nodes(ospec, root):
    for res in root.findall(pg_tag('node')):
        name = res.attrib['component_name']
        description = 'ProtoGENI Node'
        type = 'node'
        omni_res = OmniResource(name, description, type)
        
        available = res.find(pg_tag('available')).text.lower() == 'true'
        omni_res.set_allocated(not(available))
        omni_res['orig_xml'] = ET.tostring(res)
        
        id = res.attrib['component_uuid']
        ospec.add_resource(id, omni_res)
        
def add_links(ospec, root):
    for res in root.findall(pg_tag('link')):
        name = res.attrib['component_name']
        description = 'ProtoGENI Link'
        type = 'link'
        omni_res = OmniResource(name, description, type)
        
        # Links appear to be always available
        available = True
        omni_res.set_allocated(not(available))
        omni_res['orig_xml'] = ET.tostring(res)
        id = res.attrib['component_uuid']
        ospec.add_resource(id, omni_res)

def rspec_to_omnispec(urn, rspec):
    ospec = OmniSpec("rspec_pg", urn)
    doc = ET.fromstring(rspec)
    #add_nodes(ospec, doc)
    #add_links(ospec, doc)
    add_options(ospec, doc)
    return ospec

def add_node(root, onode):
    root.append(ET.fromstring(onode['orig_xml']))

def add_link(root, olink):
    root.append(ET.fromstring(olink['orig_xml']))

def wannabe_omnispec_to_rspec(omnispec, filter_allocated):
    # Convert it to XML
    root = ET.Element('rspec')
    for id, r in omnispec.get_resources().items():
        if filter_allocated and not r.get_allocate():
            continue
        res_type = r.get_type()
        if res_type == 'node':
            add_node(root, r)
        elif res_type == 'link':
            add_link(root, r)
        else:
            raise(Exception('Unknown resource type ' + res_type))

    return ET.tostring(root)

def get_options_rspec(omnispec, filter_allocated):
    # Convert it to XML
    root = ET.Element('rspec')
    root.set('xmlns', "http://protogeni.net/resources/rspec/0.2")
    
        
    for id, r in omnispec.get_resources().items():
        if filter_allocated and not r.get_allocate():
            continue
        res_type = r.get_type()
        if res_type == 'RandomPC':
            for i in range(0, r['options']['number']):
                node = ET.SubElement(root, 'node', virtual_id='geni%s'%i, virtualization_type='emulab_vnode',
                              startup_command=r['options']['startup command'] )
                if r['options']['os'] != '':
                    ET.SubElement(node, 'disk_image', name='urn:publicid:IDN+emulab.net+image+emulab-ops//%s' % r['options']['os'])
                
        else:
            raise(Exception('Unknown resource type ' + res_type))

    return ET.tostring(root)

def omnispec_to_rspec(omnispec, filter_allocated):
    """Return a static rspec for testing."""
    return get_options_rspec(omnispec, filter_allocated)
    #return ONE_NODE_RSPEC
