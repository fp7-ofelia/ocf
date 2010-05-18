import re

def int_to_dotted_ip( intip ):
        octet = ''
        for exp in [3,2,1,0]:
                octet = octet + str(intip / ( 256 ** exp )) + "."
                intip = intip % ( 256 ** exp )
        return(octet.rstrip('.'))
 
def dotted_ip_to_int( dotted_ip ):
        exp = 3
        intip = 0
        for quad in dotted_ip.split('.'):
                intip = intip + (int(quad) * (256 ** exp))
                exp = exp - 1
        return(intip)

def ip_range_to_string(intip1, intip2):
    frm = int_to_dotted_ip(intip1) + "-"
    total = frm + int_to_dotted_ip(intip2)
    return total

def mac_to_int(mac):
    assert(re.match("..:..:..:..:..:..", mac))
    parts = mac.split(":")
    return int("".join(parts), base=16)

def int_to_mac(mac):
    if type(mac) == str and ":" in str:
        return mac
    s = "%012x" % long(mac)
    m = re.findall("\w\w", s)
    return ":".join(m)

def dpid_to_long(dpid):
    assert(re.match("..:..:..:..:..:..:..:..", dpid))
    parts = dpid.split(":")
    return int("".join(parts), base=16)

def long_to_dpid(l):
    if type(l) == str and ":" in str:
        return l
    s = "%016x" % long(l)
    m = re.findall("\w\w", s)
    return ":".join(m)

