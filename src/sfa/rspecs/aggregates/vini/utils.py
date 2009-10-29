import re
import socket
from sfa.util.faults import *
from sfa.rspecs.aggregates.vini.topology import *

default_topo_xml = """
            <LinkSpec>
                <endpoint>i2atla1</endpoint>
                <endpoint>i2chic1</endpoint>
                <bw>1Mbit</bw>
            </LinkSpec>
            <LinkSpec>
                <endpoint>i2atla1</endpoint>
                <endpoint>i2hous1</endpoint>
                <bw>1Mbit</bw>
            </LinkSpec>
            <LinkSpec>
                <endpoint>i2atla1</endpoint>
                <endpoint>i2wash1</endpoint>
                <bw>1Mbit</bw>
            </LinkSpec>
            <LinkSpec>
                <endpoint>i2chic1</endpoint>
                <endpoint>i2kans1</endpoint>
                <bw>1Mbit</bw>
            </LinkSpec>
            <LinkSpec>
                <endpoint>i2chic1</endpoint>
                <endpoint>i2wash1</endpoint>
                <bw>1Mbit</bw>
            </LinkSpec>
            <LinkSpec>
                <endpoint>i2hous1</endpoint>
                <endpoint>i2kans1</endpoint>
                <bw>1Mbit</bw>
            </LinkSpec>
            <LinkSpec>
                <endpoint>i2hous1</endpoint>
                <endpoint>i2losa1</endpoint>
                <bw>1Mbit</bw>
            </LinkSpec>
            <LinkSpec>
                <endpoint>i2kans1</endpoint>
                <endpoint>i2salt1</endpoint>
                <bw>1Mbit</bw>
            </LinkSpec>
            <LinkSpec>
                <endpoint>i2losa1</endpoint>
                <endpoint>i2salt1</endpoint>
                <bw>1Mbit</bw>
            </LinkSpec>
            <LinkSpec>
                <endpoint>i2losa1</endpoint>
                <endpoint>i2seat1</endpoint>
                <bw>1Mbit</bw>
            </LinkSpec>
            <LinkSpec>
                <endpoint>i2newy1</endpoint>
                <endpoint>i2wash1</endpoint>
                <bw>1Mbit</bw>
            </LinkSpec>
            <LinkSpec>
                <endpoint>i2salt1</endpoint>
                <endpoint>i2seat1</endpoint>
                <bw>1Mbit</bw>
            </LinkSpec>"""
      
# Taken from bwlimit.py
#
# See tc_util.c and http://physics.nist.gov/cuu/Units/binary.html. Be
# warned that older versions of tc interpret "kbps", "mbps", "mbit",
# and "kbit" to mean (in this system) "kibps", "mibps", "mibit", and
# "kibit" and that if an older version is installed, all rates will
# be off by a small fraction.
suffixes = {
    "":         1,
    "bit":	1,
    "kibit":	1024,
    "kbit":	1000,
    "mibit":	1024*1024,
    "mbit":	1000000,
    "gibit":	1024*1024*1024,
    "gbit":	1000000000,
    "tibit":	1024*1024*1024*1024,
    "tbit":	1000000000000,
    "bps":	8,
    "kibps":	8*1024,
    "kbps":	8000,
    "mibps":	8*1024*1024,
    "mbps":	8000000,
    "gibps":	8*1024*1024*1024,
    "gbps":	8000000000,
    "tibps":	8*1024*1024*1024*1024,
    "tbps":	8000000000000
}


def get_tc_rate(s):
    """
    Parses an integer or a tc rate string (e.g., 1.5mbit) into bits/second
    """

    if type(s) == int:
        return s
    m = re.match(r"([0-9.]+)(\D*)", s)
    if m is None:
        return -1
    suffix = m.group(2).lower()
    if suffixes.has_key(suffix):
        return int(float(m.group(1)) * suffixes[suffix])
    else:
        return -1

def format_tc_rate(rate):
    """
    Formats a bits/second rate into a tc rate string
    """

    if rate >= 1000000000 and (rate % 1000000000) == 0:
        return "%.0fgbit" % (rate / 1000000000.)
    elif rate >= 1000000 and (rate % 1000000) == 0:
        return "%.0fmbit" % (rate / 1000000.)
    elif rate >= 1000:
        return "%.0fkbit" % (rate / 1000.)
    else:
        return "%.0fbit" % rate


class Node:
    def __init__(self, node, bps = 1000 * 1000000):
        self.id = node['node_id']
        self.hostname = node['hostname']
        self.shortname = self.hostname.replace('.vini-veritas.net', '')
        self.site_id = node['site_id']
        self.ipaddr = socket.gethostbyname(self.hostname)
        self.bps = bps
        self.links = set()

    def get_link_id(self, remote):
        if self.id < remote.id:
            link = (self.id<<7) + remote.id
        else:
            link = (remote.id<<7) + self.id
        return link
        
    def get_iface_id(self, remote):
        if self.id < remote.id:
            iface = 1
        else:
            iface = 2
        return iface
    
    def get_virt_ip(self, remote):
        link = self.get_link_id(remote)
        iface = self.get_iface_id(remote)
        first = link >> 6
        second = ((link & 0x3f)<<2) + iface
        return "192.168.%d.%d" % (first, second)

    def get_virt_net(self, remote):
        link = self.get_link_id(remote)
        first = link >> 6
        second = (link & 0x3f)<<2
        return "192.168.%d.%d/30" % (first, second)
        
    def get_site(self, sites):
        return sites[self.site_id]
    
    def get_topo_rspec(self, link):
        if link.end1 == self:
            remote = link.end2
        elif link.end2 == self:
            remote = link.end1
        else:
            raise Error("Link does not connect to Node")
            
        my_ip = self.get_virt_ip(remote)
        remote_ip = remote.get_virt_ip(self)
        net = self.get_virt_net(remote)
        bw = format_tc_rate(link.bps)
        return (remote.id, remote.ipaddr, bw, my_ip, remote_ip, net)
        
    def add_link(self, link):
        self.links.add(link)
        
    def add_tag(self, sites):
        s = self.get_site(sites)
        words = self.hostname.split(".")
        index = words[0].replace("node", "")
        if index.isdigit():
            self.tag = s.tag + index
        else:
            self.tag = None

    # Assumes there is at most one Link between two sites
    def get_sitelink(self, node, sites):
        site1 = sites[self.site_id]
        site2 = sites[node.site_id]
        sl = site1.links.intersection(site2.links)
        if len(sl):
            return sl.pop()
        return None
    

class Link:
    def __init__(self, end1, end2, bps = 1000 * 1000000):
        self.end1 = end1
        self.end2 = end2
        self.bps = bps
        
        end1.add_link(self)
        end2.add_link(self)
        
        
class Site:
    def __init__(self, site):
        self.id = site['site_id']
        self.node_ids = site['node_ids']
        self.name = site['abbreviated_name'].replace(" ", "_")
        self.tag = site['login_base']
        self.public = site['is_public']
        self.enabled = site['enabled']
        self.links = set()

    def get_sitenodes(self, nodes):
        n = []
        for i in self.node_ids:
            n.append(nodes[i])
        return n
    
    def add_link(self, link):
        self.links.add(link)
    
    
class Slice:
    def __init__(self, slice):
        self.id = slice['slice_id']
        self.name = slice['name']
        self.node_ids = set(slice['node_ids'])
        self.slice_tag_ids = slice['slice_tag_ids']
    
    def get_tag(self, tagname, slicetags, node = None):
        for i in self.slice_tag_ids:
            tag = slicetags[i]
            if tag.tagname == tagname:
                if (not node) or (node.id == tag.node_id):
                    return tag
        else:
            return None
        
    def get_nodes(self, nodes):
        n = []
        for id in self.node_ids:
            n.append(nodes[id])
        return n
             
    
    # Add a new slice tag   
    def add_tag(self, tagname, value, slicetags, node = None):
        record = {'slice_tag_id':None, 'slice_id':self.id, 'tagname':tagname, 'value':value}
        if node:
            record['node_id'] = node.id
        else:
            record['node_id'] = None
        tag = Slicetag(record)
        slicetags[tag.id] = tag
        self.slice_tag_ids.append(tag.id)
        tag.changed = True       
        tag.updated = True
        return tag
    
    # Update a slice tag if it exists, else add it             
    def update_tag(self, tagname, value, slicetags, node = None):
        tag = self.get_tag(tagname, slicetags, node)
        if tag and tag.value == value:
            value = "no change"
        elif tag:
            tag.value = value
            tag.changed = True
        else:
            tag = self.add_tag(tagname, value, slicetags, node)
        tag.updated = True
            
    def assign_egre_key(self, slicetags):
        if not self.get_tag('egre_key', slicetags):
            try:
                key = free_egre_key(slicetags)
                self.update_tag('egre_key', key, slicetags)
            except:
                # Should handle this case...
                pass
        return
            
    def turn_on_netns(self, slicetags):
        tag = self.get_tag('netns', slicetags)
        if (not tag) or (tag.value != '1'):
            self.update_tag('netns', '1', slicetags)
        return
   
    def turn_off_netns(self, slicetags):
        tag = self.get_tag('netns', slicetags)
        if tag and (tag.value != '0'):
            tag.delete()
        return
    
    def add_cap_net_admin(self, slicetags):
        tag = self.get_tag('capabilities', slicetags)
        if tag:
            caps = tag.value.split(',')
            for cap in caps:
                if cap == "CAP_NET_ADMIN":
                    return
            else:
                newcaps = "CAP_NET_ADMIN," + tag.value
                self.update_tag('capabilities', newcaps, slicetags)
        else:
            self.add_tag('capabilities', 'CAP_NET_ADMIN', slicetags)
        return
    
    def remove_cap_net_admin(self, slicetags):
        tag = self.get_tag('capabilities', slicetags)
        if tag:
            caps = tag.value.split(',')
            newcaps = []
            for cap in caps:
                if cap != "CAP_NET_ADMIN":
                    newcaps.append(cap)
            if newcaps:
                value = ','.join(newcaps)
                self.update_tag('capabilities', value, slicetags)
            else:
                tag.delete()
        return

    # Update the vsys/setup-link and vsys/setup-nat slice tags.
    def add_vsys_tags(self, slicetags):
        link = nat = False
        for i in self.slice_tag_ids:
            tag = slicetags[i]
            if tag.tagname == 'vsys':
                if tag.value == 'setup-link':
                    link = True
                elif tag.value == 'setup-nat':
                    nat = True
        if not link:
            self.add_tag('vsys', 'setup-link', slicetags)
        if not nat:
            self.add_tag('vsys', 'setup-nat', slicetags)
        return


class Slicetag:
    newid = -1 
    def __init__(self, tag):
        self.id = tag['slice_tag_id']
        if not self.id:
            # Make one up for the time being...
            self.id = Slicetag.newid
            Slicetag.newid -= 1
        self.slice_id = tag['slice_id']
        self.tagname = tag['tagname']
        self.value = tag['value']
        self.node_id = tag['node_id']
        self.updated = False
        self.changed = False
        self.deleted = False
    
    # Mark a tag as deleted
    def delete(self):
        self.deleted = True
        self.updated = True
    
    def write(self, api):
        if self.changed:
            if int(self.id) > 0:
                api.plshell.UpdateSliceTag(api.plauth, self.id, self.value)
            else:
                api.plshell.AddSliceTag(api.plauth, self.slice_id, 
                                        self.tagname, self.value, self.node_id)
        elif self.deleted and int(self.id) > 0:
            api.plshell.DeleteSliceTag(api.plauth, self.id)


"""
A topology is a compound object consisting of:
* a dictionary mapping site IDs to Site objects
* a dictionary mapping node IDs to Node objects
* the Site objects are connected via SiteLink objects representing
  the physical topology and available bandwidth
* the Node objects are connected via Link objects representing
  the requested or assigned virtual topology of a slice
"""
class Topology:
    def __init__(self, api):
        self.api = api
        self.sites = get_sites(api)
        self.nodes = get_nodes(api)
        self.tags = get_slice_tags(api)
        self.sitelinks = []
        self.nodelinks = []
    
        for (s1, s2) in PhysicalLinks:
            self.sitelinks.append(Link(self.sites[s1], self.sites[s2]))
        
        for id in self.nodes:
            self.nodes[id].add_tag(self.sites)
        
        for t in self.tags:
            tag = self.tags[t]
            if tag.tagname == 'topo_rspec':
                node1 = self.nodes[tag.node_id]
                l = eval(tag.value)
                for (id, realip, bw, lvip, rvip, vnet) in l:
                    allocbps = get_tc_rate(bw)
                    node1.bps -= allocbps
                    try:
                        node2 = self.nodes[id]
                        if node1.id < node2.id:
                            sl = node1.get_sitelink(node2, self.sites)
                            sl.bps -= allocbps
                    except:
                        pass

    
    def lookupSite(self, id):
        val = None
        try:
            val = self.sites[id]
        except:
            raise KeyError("site ID %s not found" % id)
        return val
    
    def getSites(self):
        sites = []
        for s in self.sites:
            sites.append(self.sites[s])
        return sites
        
    def lookupNode(self, id):
        val = None
        try:
            val = self.nodes[id]
        except:
            raise KeyError("node ID %s not found" % id)
        return val
    
    def getNodes(self):
        nodes = []
        for n in self.nodes:
            nodes.append(self.nodes[n])
        return nodes
    
    def nodesInTopo(self):
        nodes = []
        for n in self.nodes:
            if self.nodes[n].links:
                nodes.append(self.nodes[n])
        return nodes
            
    def lookupSliceTag(self, id):
        val = None
        try:
            val = self.tags[id]
        except:
            raise KeyError("slicetag ID %s not found" % id)
        return val
    
    def getSliceTags(self):
        tags = []
        for t in self.tags:
            tags.append(self.tags[t])
        return tags
    
    def lookupSiteLink(self, node1, node2):
        site1 = self.sites[node1.site_id]
        site2 = self.sites[node2.site_id]
        for link in self.sitelinks:
            if site1 == link.end1 and site2 == link.end2:
                return link
            if site2 == link.end1 and site1 == link.end2:
                return link
        return None
    
    def nodeTopoFromRspec(self, rspec):
        if self.nodelinks:
            raise Error("virtual topology already present")
            
        rspecdict = rspec.toDict()
        nodedict = {}
        for node in self.getNodes():
            nodedict[node.tag] = node
            
        linkspecs = rspecdict['RSpec']['Request'][0]['NetSpec'][0]['LinkSpec']    
        for l in linkspecs:
            n1 = nodedict[l['endpoint'][0]]
            n2 = nodedict[l['endpoint'][1]]
            bps = get_tc_rate(l['bw'][0])
            self.nodelinks.append(Link(n1, n2, bps))
 
    def nodeTopoFromSliceTags(self, slice):
        if self.nodelinks:
            raise Error("virtual topology already present")
            
        for node in slice.get_nodes(self.nodes):
            linktag = slice.get_tag('topo_rspec', self.tags, node)
            if linktag:
                l = eval(linktag.value)
                for (id, realip, bw, lvip, rvip, vnet) in l:
                    if node.id < id:
                        bps = get_tc_rate(bw)
                        remote = self.lookupNode(id)
                        self.nodelinks.append(Link(node, remote, bps))

    def updateSliceTags(self, slice):
        if not self.nodelinks:
            return
 
        slice.update_tag('vini_topo', 'manual', self.tags)
        slice.assign_egre_key(self.tags)
        slice.turn_on_netns(self.tags)
        slice.add_cap_net_admin(self.tags)

        for node in slice.get_nodes(self.nodes):
            linkdesc = []
            for link in node.links:
                linkdesc.append(node.get_topo_rspec(link))
            if linkdesc:
                topo_str = "%s" % linkdesc
                slice.update_tag('topo_rspec', topo_str, self.tags, node)

        # Update slice tags in database
        for tag in self.getSliceTags():
            if tag.slice_id == slice.id:
                if tag.tagname == 'topo_rspec' and not tag.updated:
                    tag.delete()
                tag.write(self.api)
                
    """
    Check the requested topology against the available topology and capacity
    """
    def verifyNodeTopo(self, hrn, topo, maxbw):
        maxbps = get_tc_rate(maxbw)
        for link in self.nodelinks:
            if link.bps <= 0:
                raise GeniInvalidArgument(bw, "BW")
            if link.bps > maxbps:
                raise PermissionError(" %s requested %s but max BW is %s" % 
                                      (hrn, format_tc_rate(link.bps), maxbw))
                
            n1 = link.end1
            n2 = link.end2
            sitelink = self.lookupSiteLink(n1, n2)
            if not sitelink:
                raise PermissionError("%s: nodes %s and %s not adjacent" % (hrn, n1.tag, n2.tag))
            if sitelink.bps < link.bps:
                raise PermissionError("%s: insufficient capacity between %s and %s" % (hrn, n1.tag, n2.tag))
                
    """
    Produce XML directly from the topology specification.
    """
    def toxml(self, hrn = None):
        xml = """<?xml version="1.0"?>
<RSpec xmlns="http://www.planet-lab.org/sfa/rspec/" name="vini">
    <Capacity>
        <NetSpec name="physical_topology">"""

        for site in self.getSites():
            if not (site.public and site.enabled):
                continue
            
            xml += """
            <SiteSpec name="%s"> """ % site.name

            for node in site.get_sitenodes(self.nodes):
                if not node.tag:
                    continue
                
                xml += """
                <NodeSpec name="%s">
                    <hostname>%s</hostname>
                    <bw>%s</bw>
                </NodeSpec>""" % (node.tag, node.hostname, format_tc_rate(node.bps))
            xml += """
            </SiteSpec>"""
            
        for link in self.sitelinks:
            xml += """
            <SiteLinkSpec>
                <endpoint>%s</endpoint>
                <endpoint>%s</endpoint> 
                <bw>%s</bw>
            </SiteLinkSpec>""" % (link.end1.name, link.end2.name, format_tc_rate(link.bps))
            
        
        if hrn:
            name = hrn
        else:
            name = 'default_topology'
        xml += """
        </NetSpec>
    </Capacity>
    <Request>
        <NetSpec name="%s">""" % name
        
        if hrn:
            for link in self.nodelinks:
                xml += """
            <LinkSpec>
                <endpoint>%s</endpoint>
                <endpoint>%s</endpoint> 
                <bw>%s</bw>
            </LinkSpec>""" % (link.end1.tag, link.end2.tag, format_tc_rate(link.bps))
        else:
            xml += default_topo_xml
            
        xml += """
        </NetSpec>
    </Request>
</RSpec>"""

        # Remove all leading whitespace and newlines
        lines = xml.split("\n")
        noblanks = ""
        for line in lines:
            noblanks += line.strip()
        return noblanks


"""
Create a dictionary of site objects keyed by site ID
"""
def get_sites(api):
    tmp = []
    for site in api.plshell.GetSites(api.plauth):
        t = site['site_id'], Site(site)
        tmp.append(t)
    return dict(tmp)


"""
Create a dictionary of node objects keyed by node ID
"""
def get_nodes(api):
    tmp = []
    for node in api.plshell.GetNodes(api.plauth):
        t = node['node_id'], Node(node)
        tmp.append(t)
    return dict(tmp)

"""
Create a dictionary of slice objects keyed by slice ID
"""
def get_slice(api, slicename):
    slice = api.plshell.GetSlices(api.plauth, [slicename])
    if slice:
        return Slice(slice[0])
    else:
        return None

"""
Create a dictionary of slicetag objects keyed by slice tag ID
"""
def get_slice_tags(api):
    tmp = []
    for tag in api.plshell.GetSliceTags(api.plauth):
        t = tag['slice_tag_id'], Slicetag(tag)
        tmp.append(t)
    return dict(tmp)
    
"""
Find a free EGRE key
"""
def free_egre_key(slicetags):
    used = set()
    for i in slicetags:
        tag = slicetags[i]
        if tag.tagname == 'egre_key':
            used.add(int(tag.value))
                
    for i in range(1, 256):
        if i not in used:
            key = i
            break
    else:
        raise KeyError("No more EGRE keys available")
        
    return "%s" % key
   
