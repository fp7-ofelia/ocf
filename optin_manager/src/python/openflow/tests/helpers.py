'''
Created on May 15, 2010

@author: jnaous
'''

import re

SWITCH_URN_REGEX = r"^(?P<prefix>.*)\+switch:(?P<dpid>[:a-fA-F\d]+)$"
PORT_URN_REGEX = r"%s\+port:(?P<port>\d+)$" % SWITCH_URN_REGEX[:-1]

def _long_to_mac(l):
    if type(l) == str:
        return l
    s = "%012x" % l
    m = re.findall("\w\w", s)
    return ":".join(m)
    
def _int_to_ip(i):
    if type(i) == str:
        return i
    return "%s.%s.%s.%s" % (
        (i >> 24) & 0xff,
        (i >> 16) & 0xff,
        (i >> 8) & 0xff,
        i & 0xff,
    )

class Switch(object):
    def __init__(self, urn):
        match = re.search(SWITCH_URN_REGEX, urn)
        if not match:
            raise Exception("Bad switch URN: %s" % urn)
        self.prefix = match.group("prefix")
        self.dpid = match.group("dpid")
        self.urn = urn
        
    def __str__(self):
        return self.dpid
    
    def __unicode__(self):
        return self.__str__()
        
    def add_to_resv_switches_elem(self, switches_elem):
        from xml.etree import cElementTree as et
        return et.SubElement(
            switches_elem, "switch", {
                "urn": self.urn,
            }
        )
        
class Link(object):
    def __init__(self, src_urn, dst_urn):
        self.src_urn = src_urn
        self.dst_urn = dst_urn

        match = re.search(PORT_URN_REGEX, src_urn)
        if not match:
            raise Exception("Bad port URN: %s" % src_urn)
        self.src_prefix = match.group("prefix")
        self.src_dpid = match.group("dpid")
        self.src_port = match.group("port")
        
        match = re.search(PORT_URN_REGEX, dst_urn)
        if not match:
            raise Exception("Bad port URN: %s" % dst_urn)
        self.dst_prefix = match.group("prefix")
        self.dst_dpid = match.group("dpid")
        self.dst_port = match.group("port")
        
    def __str__(self):
        return "Link from %s.%s to %s.%s" % (
            self.src_dpid, self.src_port, self.dst_dpid, self.dst_port)

    def __unicode__(self):
        return self.__str__()
                
class Flowspace(object):
    
    @classmethod
    def create_controlled_random(cls, all_switches):
        import random
        
        if len(all_switches) == 1:
            switches = all_switches
        else:
            # pick a number of switches for the flowspace
            num_sw = random.randint(1,len(all_switches))
            
            # choose switches
            switches = random.sample(all_switches, num_sw)
                    
                    
        attrs = {}
        
#        attrs["nw_src"] = \
#            (_int_to_ip(random.randint(0,0x80000000) & 0xFFFF0000),
#            _int_to_ip(random.randint(0x80000000,0xFFFFFFFF) & 0xFFFF0000))
        return cls(attrs, switches)
    
    @classmethod
    def create_random(cls, all_switches):
        import random
        
        if len(all_switches) == 1:
            switches = all_switches
        else:
            # pick a number of switches for the flowspace
            num_sw = random.randint(1,len(all_switches))
            
            # choose switches
            switches = random.sample(all_switches, num_sw)
        
        def flip_coin():
            return random.choice([True, False])
        
        def rand_val(width, min="*"):
            if min == "*":
                min = 0
            if flip_coin():
                return random.randint(min, 2**width - 1)
            else:
                return "*"
        
        def rand_range(width, to_x=None):
            a = rand_val(width)
            b = rand_val(width, a)
            if to_x:
                return (to_x(a), to_x(b))
            else:
                return (a, b)
            
        def same(val):
            return "%s" % val
            
        # information on the attributes:
        attr_funcs = {
            # attr_name: (func to turn to xml, width)
            "dl_src": (_long_to_mac, 48),
            "dl_dst": (_long_to_mac, 48),
            "dl_type": (same, 16),
            "vlan_id": (same, 12),
            "nw_src": (_int_to_ip, 32),
            "nw_dst": (_int_to_ip, 32),
            "nw_proto": (same, 8),
            "tp_src": (same, 16),
            "tp_dst": (same, 16),
            "port_num": (same, 2),
        }
        
        # select some of the attributes
        num_attr_sel = random.randint(1, len(attr_funcs))
        attr_sel = random.sample(attr_funcs.items(), num_attr_sel)
        
        # create items
        attrs = {}
        for item in attr_sel:
            key = item[0]
            to_x, width = item[1]
            val = rand_range(width, to_x)
            attrs[key] = val
        
        return cls(attrs, switches)
    
    def __init__(self, attrs, switches):
        """
        attrs is a dict with the following keys:
        dl_src/dst/type
        vlan_id
        nw_src/dst/proto
        tp_src/dst
        
        Each key maps to a tuple specifying a range. e.g.
        {'dl_src': ('*', '*'),
         'nw_src': ('192.168.0.0', '192.168.255.255'),
        }
        
        Some keys can be missing.
         
        switches is a list of Switch objects
        """
        self.attrs = attrs.copy()
        self.switches = switches
        
    def __str__(self):
        return "Switches: %s, %s" % (
            " ".join([sw.dpid for sw in self.switches]),
            self.attrs
        )
        
    def add_to_rspec(self, root):
        from xml.etree import cElementTree as et
        fs_elem = et.SubElement(root, "flowspace")
        switches_elem = et.SubElement(fs_elem, "switches")
        for s in self.switches:
            s.add_to_resv_switches_elem(switches_elem)

        for k,v in self.attrs.items():
            et.SubElement(
                fs_elem, k, {
                    "from": v[0],
                    "to": v[1],
                }
            )
    
    def get_full_attrs(self):
        attr_names = ["dl_src", "dl_dst", "dl_type", "vlan_id", "nw_src",
                      "nw_dst", "nw_proto", "tp_src", "tp_dst", "port_num"]

        # make the local attrs dict full with _start and _end
        temp = {}
        for attr in attr_names:
            if attr not in self.attrs:
                temp["%s_start" % attr] = "*"
                temp["%s_end" % attr] = "*"
            else:
                temp["%s_start" % attr] = self.attrs[attr][0]
                temp["%s_end" % attr] = self.attrs[attr][1]
        return temp
    
    def compare_to_sliver_fs(self, sliver_fs):
        full = self.get_full_attrs()
        return full == sliver_fs

def parse_rspec(rspec):
    """
    parse the rspec and return a tuple of lists of switches and links
    """
    from xml.etree import cElementTree as et
    
    root = et.fromstring(rspec)
    
    switch_elems = root.findall(".//switch")
    switches = []
    for switch_elem in switch_elems:
        switches.append(Switch(switch_elem.get("urn")))
        
    link_elems = root.findall(".//link")
    links = []
    for link_elem in link_elems:
        links.append(Link(link_elem.get("src_urn"),
                          link_elem.get("dst_urn")))
        
    return (switches, links)

def create_random_resv(num_flowspaces, switches,
                       firstname="John", lastname="Doe",
                       email="john.doe@geni.net", password="slice_pass",
                       proj_name="Stanford Networking",
                       proj_desc="Making the world better.",
                       slice_name="Crazy Load Balancer",
                       slice_desc="Does this and that...",
                       ctrl_url="tcp:controller.stanford.edu:6633",
                       flowspaces=None,
                       fs_randomness=True):
    from xml.etree import cElementTree as et
    
    root = et.Element("resv_rspec")
    
    et.SubElement(
        root, "user", dict(
            firstname=firstname,
            lastname=lastname,
            email=email,
            password=password,
        )
    )
    
    et.SubElement(
        root, "project", dict(
            name=proj_name,
            description=proj_desc,
        )
    )
    
    et.SubElement(
        root, "slice", dict(
            name=slice_name,
            description=slice_desc,
            controller_url=ctrl_url,
        )
    )
    
    if not flowspaces:
        flowspaces = []
        for i in range(num_flowspaces):
            if (fs_randomness):
                f = Flowspace.create_random(switches)
            else:
                f = Flowspace.create_controlled_random(switches)
            flowspaces.append(f)
            
    for f in flowspaces:
        f.add_to_rspec(root)

    return (et.tostring(root), flowspaces)

def kill_old_procs(self, *ports):
    import shlex, subprocess, os, signal, time
    cmd = "netstat -l -t -p --numeric-ports"
    args = shlex.split(cmd)
    p = subprocess.Popen(args,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.wait()
    o, e = p.communicate()
    lines = o.splitlines()
    for l in lines:
        for p in ports:
            if "localhost:%s" % p in l:
#                print "killed process listening at localhost:%s" % p
                cols = l.split()
                prog = cols[6]
                pid,sep,progname = prog.partition("/")
                os.kill(int(pid), signal.SIGHUP)
    
    time.sleep(1)
