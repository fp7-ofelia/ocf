import re
import sqlite3
import socket
import struct
import sys
import binascii
import operator

class AggregateManager:
    """A single aggregate manager
    Agrs: its name, url, key file and cert file
    """
    def __init__(self, namein, urllink, key, cert):
        self.name = namein
        self.url = urllink
        self.key_file = key
        self.cert_file = cert
    def __unicode__(self):
        return 'AM ' + self.name + ' at ' + self.url


class Node:
    """A node
    Agrs: aggregate manager this node belongs to, node ID, type of the node (switch, host, or others)
    """
    def __init__(self ,am, node, typeofnode):
        self.aggMgr = am
        self.nodeid = nodeID
        self.type = type
        return 'Node ' + self.name 
        
class Interface:
    """An interface of a node
    Agrs: node of the interface, port number of this interface, remote interface of this interface
    """
#    QoS 
    def __init__(self,nodeown, port):
        self.ownerNode = nodeown
        self.portNum =  port
    def __unicode__(self):
        return 'Interface '+self.portNum

class Slice:
    """
    create a slice
    Agrs: 
    experimenter: experimenter ID
    name of the slice (or its ID)
    contr: controller URL
    reserve: true or false
    nodes: a set of nodes will be used in this slice
    interfaces: which interfaces or (links) this slice requests
    timestart and timeend are the time to reserve the experiment 
    flowspaces: a set of flowspaces 
    """
    def __init__(self, experimenter, nameOfSlice, contr, reserve, nodes, interfaces, timeA, timeB, flows):
        self.owner = experimenter
        self.name =  nameOfSlice
        self.controller_url = contr
        self.reserve = reserve
        self.nodes = nodes
        self.interfaces = interfaces
        self.timestart = timeA
        self.timeend = timeB
        self.flowspaces = flows
        
class FlowSpace:
    """
    FlowSpace with the policy and the slice associated with it
    Agrs:
    flow_id: id of the flowspace in the database
    policy: allow(1), deny(-1), readonly(0)
    dl_src: datalink source address (MAC)
    dl_dst: datalink destination address (MAC)
    dl_type: datalink type
    vlan_id: VLAN ID
    nw_src: IP source address
    nw_dst: IP destination address
    nw_proto: IP protocol version
    tp_src: transport source port/ ICMP type
    tp_dst: transport destination port/ ICMP type
    slice: slice ID of this flowspace
    """
    def __init__(self, flowid, pol, macSrc, macDst, dtype, vlan, ipSrc, ipDst, ipv, tcpSrc, tcpDst, sliceId):
        """ Initialize the object with the class FlowSpace. 
        flow_id: (string)  id of the flowspace in the database 
        policy: (int -1,0,1) allow(1), deny(-1), readonly(0)
        dl_src: (string) datalink source address (MAC)
        dl_dst: (string) datalink destination address (MAC)
        dl_type: (string) datalink type
        vlan_id: (string) VLAN ID
        nw_src: (string) IP source address
        nw_dst: (string) IP destination address
        nw_proto: (string) IP protocol version
        tp_src: (string) transport source port/ ICMP type
        tp_dst: (string) transport destination port/ ICMP type
        slice: (string) slice ID of this flowspace
        
        """

        self.flow_id = flowid
        self.policy = pol
        self.dl_src = macSrc
        self.dl_dst = macDst
        self.dl_type = dtype
        self.vlan_id = vlan
        self.nw_src = ipSrc
        self.nw_dst = ipDst
        self.nw_proto = ipv
        self.tp_src = tcpSrc
        self.tp_dst = tcpDst
        self.slice = sliceId

    def display(self):
        """Print out the flowspace object"""
        if self.policy == -1:
            print "deny: dl_src: "+ self.dl_src + " dl_dst: "+ self.dl_dst + " ether_type: "+ self.dl_type + " vlan_id: "+ self.vlan_id + " ip_src: "+ self.nw_src + " ip_dst: "+ self.nw_dst + " ip_proto: "+ self.nw_proto + " tp_src: "+ self.tp_src + " tp_dst: "+ self.tp_dst + " slice_id: "+ self.slice
        elif self.policy == 0:
            print "read-only: dl_src: "+ self.dl_src + " dl_dst: "+ self.dl_dst + " ether_type: "+ self.dl_type + " vlan_id: "+ self.vlan_id + " ip_src: "+ self.nw_src + " ip_dst: "+ self.nw_dst + " ip_proto: "+ self.nw_proto + " tp_src: "+ self.tp_src + " tp_dst: "+ self.tp_dst + " slice_id: "+ self.slice
        elif self.policy == 1:
            print "allow: dl_src: "+ self.dl_src + " dl_dst: "+ self.dl_dst + " ether_type: "+ self.dl_type + " vlan_id: "+ self.vlan_id + " ip_src: "+ self.nw_src + " ip_dst: "+ self.nw_dst + " ip_proto: "+ self.nw_proto + " tp_src: "+ self.tp_src + " tp_dst: "+ self.tp_dst + " slice_id: "+ self.slice 
        

    def equalfs(self,other):
        if flowSpace2bits(self) == flowSpace2bits(other):
            return 1
        return 0
        
def _readfile(filename):
    """
    f = open('/tmp/workfile', 'w')
    print f
    <open file '/tmp/workfile', mode 'w' at 80a0960>

    f.read()
    This is the entire file.\n'
    f.read()
    >>> f.readlines()
    >>> for line in f:
    print line,
    [x.strip() for x in open ('source.txt', 'r')]

    (value, key) = re.split('\t+?\#', line)
    """
    t=[]
    f = open(filename, 'r')
    for line in f:
        line.rstrip('\n')
        test = re.split(':',line.rstrip('\n'))
        t.append(FlowSpace(test[0],test[1],test[2],test[3],test[4],test[5],test[6],test[7],test[8],test[9],test[10],test[11]))
        print t[-1].nw_src
    return t


def _readDB(dbfile):
    con = sqlite3.connect(dbfile)
    con.isolation_level = None
    cur = con.cursor()
    
    buffer = ""

    print "Enter your SQL commands to execute in sqlite3."
    print "Enter a blank line to exit."
    
    while True:
        line = raw_input()
        if line == "":
            break
        buffer += line
        if sqlite3.complete_statement(buffer):
            try:
                buffer = buffer.strip()
                cur.execute(buffer)
                
                if buffer.lstrip().upper().startswith("SELECT"):
                    print cur.fetchall()
            except sqlite3.Error, e:
                print "An error occurred:", e.args[0]
            buffer = ""
                
    con.close()


def _is_ipv4address(str):
    """
    _is_ipv4address(str) returns 1 if the str is an IPv4 addresss. It returns 0 if the str is not an IPv4 address.
    
    Agr: IP address in quotation. 
    """
    if str.count(".") != 3:
        return 0
    if str.count("/") > 1 :
        return 0
    if str.count("/") == 0:
        for i in str.split("."):
            if not i.isdigit():
                return 0
            i = int(i)
            if i>255 or i<0:
                return 0
        return 1
    elif str.count("/") == 1:
        [prefix,mask] = str.split("/")
        if not mask.isdigit():
            return 0
        if int(mask)>32 or int(mask)<0:
            return 0
        for i in prefix.split("."):
            if not i.isdigit():
                return 0
            i = int(i)
            if i>255 or i<0:
                return 0
        return 1

def _interpret_addr(str):
    """ check whether it is an IPv4 address and return the address with x bits. 
    For e.g. 192.168.100.1/16 will give 192.168.x.x in binary. 
    
    """
    if _is_ipv4address(str):
        if str.count("/") == 1: 
            [prefix,mask] = str.split("/")
            host = _ipv42int(prefix) 
            binarypre = _IPint2binary(host)
            new = binarypre[0:int(mask)]
            hostpart = 32 - int(mask)
            for i in range(0, hostpart):
                new = new + 'x'
            return new
        else:
            host =_ipv42int(str)
            return _IPint2binary(host)
    else:
        return 0

def _interpret_bit2addr(addrbits):
    """Convert the IP addresses in binary string into IP addresses in a human readable form. """

    if len(addrbits)==32:
        n = 0
        prefix = ''
        prefix0 = ''
        prefix1 = ''
        prefix2 = ''
        prefix3 = ''
        while (n<32):
            if (addrbits[n] != 'x'):
                if n < 8:
                    prefix0 = prefix0 + addrbits[n]
                if n>= 8 and n < 16:
                    prefix1 = prefix1 + addrbits[n]
                if n>= 16 and n < 24:
                    prefix2 = prefix2 + addrbits[n]
                if n>= 24:
                    prefix3 = prefix3 + addrbits[n]
                n = n + 1
            else:
                break
        if n < 32:
            mask = n
            if n < 8:
                prefix0 = prefix0 + '0' * (8 - n)
                prefix1 = '0'*8
                prefix2 = '0'*8
                prefix3 = '0'*8

            if n>= 8 and n < 16:
                prefix1 = prefix1 + '0' * (16 - n)
                prefix2 = '0'*8
                prefix3 = '0'*8
            if n>= 16 and n < 24:
                prefix2 = prefix2 + '0' * (24 - n)
                prefix3 = '0'*8

            if n>= 24:
                prefix3 = prefix3 + '0' * (32 - n)

            prefix = str(int(prefix0,2))+'.'+str(int(prefix1,2))+'.'+str(int(prefix2,2))+'.'+str(int(prefix3,2))+'/'+str(n)
        else:
            prefix = str(int(prefix0,2))+'.'+str(int(prefix1,2))+'.'+str(int(prefix2,2))+'.'+str(int(prefix3,2))
        return prefix
    else:
        return 0

def _ipv42int(str):
    ''' converting IPv4 addresses into integer'''
    if _is_ipv4address(str):
        q = str.split(".")
        res = reduce(lambda a,b: long(a)*256 + long(b), q) 

    if res == -1:
        return 0
    return res

def _IPint2binary(n):
    '''convert IP address in integer n to binary string bStr'''
    bStr = ''
    if n < 0: raise ValueError, "must be a positive integer"

    if n == 0: return '0'
    
    while n > 0:
        bStr = str(n % 2) + bStr
        n = n >> 1
    if len(bStr) < 32:
        bStr = '0'* (32-len(bStr)) + bStr
    return bStr

def _MAChex2binary(n):
    '''convert MAC address in Hex with ":"s n to a binary string bStr'''
    bStr = ''
    Str = ''
    if n < 0: raise ValueError, "must be a positive integer"
    if n == 0: return '0'
    q = n.split(":")
    
    for x in range(0, 6):
        qn = int(q[x],16)
        bStr = ''
        while qn > 0:
            bStr = str(qn % 2) + bStr
            qn = qn >> 1
        while len(bStr)<8:
            bStr = '0' + bStr 
        Str = Str + bStr
    return Str
    
def _pack2bits(str1,b,n):
    """ Pack str1 which is in integer with base b into a length n binary string.
    Agrs: 
    str1: the string of the integer
    b: the base of the string. for e.g. the base of hexadecimal is 16
    n: the length of the output in binary (pack with 0s) 
    For e.g.
    _pack2bits('12',16,8) = '00010010'
    """
    bStr = ''
    if str1 < 0: raise ValueError, "must be a positive integer"
    if str1 == 0: return '0'
    str1 = int(str1,b)
    while str1 > 0:
        bStr = str(str1 % 2) + bStr
        str1 = str1 >> 1
    while len(bStr)<n:
        bStr = '0' + bStr 
    return bStr
    

def _binary2twobit(n):
    '''convert binary into 2 bits for Q-intersection computation'''
    bStr = ''
#    bin = _IPint2binary(n)
    bin = n
    for i in range(0,len(bin)):
        if bin[i] == '0':
            bStr = bStr + bin[i] + '1'
        elif bin[i] == '1':
            bStr = bStr + bin[i] + '0' 
        else:
            bStr = bStr + '1' + '1'
    return bStr


def _twobit2binary(n,length):
    '''convert every 2 bits into 1 bit for the result of Q-intersection computation
    Args: 
    n : input integer
    length : length of the input in binary bits
    '''
    bStr = ''
    bin = _IPint2binary(n)
    if len(bin) < length:
        bin = '0' * (length-len(bin))+ bin
    for i in range(0,len(bin)/2):
        if bin[i*2:i*2+2] == '00':
            bStr = bStr + 'z'
        elif bin[i*2:i*2+2] == '11':
            bStr = bStr + 'x' 
        else:
            bStr = bStr + bin[i*2]
#        print i, ' ', bin[i*2:i*2+2]
    return bStr
    

    
def q_intersection(objFS1, objFS2):
    """find out the q-intersection of FlowSpace objFS1 and objFS2
    For example: 
    after we converted the flowspace into bits,
    if objFS1 in bits = '1000xxxx' and objFS2 in bits = '1000100x',
    it returns the q-intersection of '1000100x'
    """
    return _twobit2binary(int(_binary2twobit(flowSpace2bits(objFS1)),2)& int(_binary2twobit(flowSpace2bits(objFS2)),2),456)


def _which_q_intersect(set, objFS):
    """ find out the q-intersection of set[] and objFS if they intersect
    Args: 
    set[]:  Reserved FlowSpaces
    objFS:  a new request FlowSpace object. 
    """
    inter = []
    for i in range(0,len(set)):
        if _if_q_intersect(q_intersection(set[i],objFS)):
            inter.append(q_intersection(set[i],objFS))
            print bits2FlowSpace(inter[-1]).display()
    return inter

def q_intersectionD(set, objFS, dbits):
    """ find out the q-intersection of set[] and objFS if they intersect
    Args: 
    set[]:  Reserved FlowSpaces
    objFS:  a new request FlowSpace object. 
    dbits: Don't care bits of a FlowSpace. 
    If we have 8 bits and the d bits are the 1st and the 2nd bits, it will be represented
    like this "00000011"
    
    There are several cases:
    - no intersection and the new request can be granted.
    - intersection doesn't occur when there are options for the don't care bit.
    - intersection occur and we can still grant the new request with part of the exceptions of the flowspace.
    - no way to grant the new request because the new requested flowspace is totally unavailable. 
    """

    inter = []
    intero = []

    if re.search('1',flowSpace2bits(dbits)): #if don't care bits are declared 
        twodbits = re.sub('1','11',re.sub('0','00',flowSpace2bits(dbits))) #convert the dbits to 2 bits for the convertion
        
        newobjFS = bits2FlowSpace(_twobit2binary((int(_binary2twobit(flowSpace2bits(objFS)),2) | int(twodbits,2)),456)) 
        #put 'x' on objFS on the marked dbits

        for i in range(0,len(set)):
            if _if_q_intersect(q_intersection(set[i],objFS)):
                newinter = bits2FlowSpace(q_intersection(set[i],objFS))
                newinter.policy = -1
                intero.append(newinter)

            if _if_q_intersect(q_intersection(set[i],newobjFS)):
                newinter = bits2FlowSpace(q_intersection(set[i],newobjFS))
                newinter.policy = -1
                inter.append(newinter)

    else: # doesn't have don't care bits
        for i in range(0,len(set)):
            if _if_q_intersect(q_intersection(set[i],objFS)):
                newinter = bits2FlowSpace(q_intersection(set[i],objFS))
                newinter.policy = -1
                intero.append(newinter)

         
    if (len(intero)< 1) and (len(inter)<1):
        print 'Granted! (no intersection)'
        objFS.display()
        print '==============================='
    else:
        if re.search('1',flowSpace2bits(dbits)):
            for j in range(0, len(intero)):
                if (objFS.equalfs(intero[j])):
                    print "Not Granted!"
                    return intero
                else: 
                    intero[j].display()
            print "Granted!"
            objFS.display()
            return inter
        else:
            g = 0 #need to figure out which one is bigger
            for j in range(0, len(intero)):
                if (objFS.equalfs(intero[j])):
                    print "Not Granted!"
                    return intero
                else: 
                    intero[j].display()
            print "Granted!"
            objFS.display()
            
    return inter
        

def _count_x(inbits):
    counter =0
    for i in range(0,len(inbits)):
        if inbits[i]=='x':
            counter =counter+1
    return counter
    #need to calculate for each obj, whether we can solve the D problem
    #return _twobit2binary(int(_binary2twobit(str1),2)& int(_binary2twobit(str2),2))

def _solve_matrix(mat,dbits):
    d = 0
    bit = ''
    while d < len(flowSpace2bits(dbits)):
        for i in range(1,len(mat)):
            if mat[i-1] != 'x':
                bit = mat[i-1][d]
                for j in range(0,len(mat)):
                    if (j != i) :
#                        if mat[i-1][d] != mat[i][d]:
                        check = mat[j][0:d] + bit + mat[j][(d+1):]
#                        if (is_or_positive(mat[j],mat[i],dbits)==0):
                            

def _is_or_positive(str1, str2, dbits):
    ''' 
    return whether str1 is true where str2 is the testing bits and str1 is the bits that flip over with the intersection
    '''
    for i in range(0,len(str1)):

        if dbits[i] == '1' :
            if (str1[i] != 'x') and (str2[i] != 'x') :
                if operator.xor(int(str1[i],2),int(str2[i],2))==0:
                    return 1
    return 0
                

def _if_q_intersect(result):
    """
    check whether there is a 'z' in the intersection result. 
    Agr:
    result: result of q_intersection() of 2 flowspaces
    Return:
    0 if they don't intersect
    1 if they intersect
    """
    if re.search('z',result):
        return 0
    else:
        return 1

def _topo2matrix(req_nodes,req_flow,set_interfaces):
    """
    Take the nodes interfaces information to check the available flowspace
    1. read db for the data of those nodes
    form the flowspaces for each interfaces
    2. match the new with the reserved flowce
    """
    

    
def flowSpace2bits(flow):
    """
    Convert a FlowSpace object into bits.
    Agrs: A FlowSpace object
    flow.dl_src has 48 bits
    flow.dl_dst has 48 bits
    flow.dl_type has 16 bits
    flow.vlan_id has 12 bits
    flow.nw_src has 32 bits
    flow.nw_dst has 32 bits
    flow.nw_proto has 8 bits
    flow.tp_src has 16 bits
    flow.tp_dst has 16 bits
    """
    bStr = ''
    if flow.dl_src == '*':
        bStr = bStr + 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    else:
        bStr = bStr + _MAChex2binary(flow.dl_src)

    if flow.dl_dst == '*':
        bStr = bStr + 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    else:
        bStr = bStr + _MAChex2binary(flow.dl_dst)

    if flow.dl_type == '*':
        bStr = bStr + 'xxxxxxxxxxxxxxxx'
    else:
        bStr = bStr + _pack2bits(flow.dl_type,10,16)

    if flow.vlan_id == '*':
        bStr = bStr + 'xxxxxxxxxxxx'
    else:
        bStr = bStr + _pack2bits(flow.vlan_id,10,12)

    if flow.nw_src == '*':
        bStr = bStr + 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    else:
        bStr = bStr + _interpret_addr(flow.nw_src)

    if flow.nw_dst == '*':
        bStr = bStr + 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    else:
        bStr = bStr + _interpret_addr(flow.nw_dst)

    if flow.nw_proto == '*':
        bStr = bStr + 'xxxxxxxx'
    else:
        bStr = bStr + _pack2bits(flow.nw_proto,10,8)
    
    if flow.tp_src == '*':
        bStr = bStr + 'xxxxxxxxxxxxxxxx'
    else:
        bStr = bStr + _pack2bits(flow.tp_src, 10, 16)

    if flow.tp_dst == '*':
        bStr = bStr + 'xxxxxxxxxxxxxxxx'
    else:
        bStr = bStr + _pack2bits(flow.tp_dst, 10, 16)
        
    return bStr

def bits2FlowSpace(bits):
    """ Convert the result flowspace intersection from the q_intersection into flowspace object
    flow.dl_src has 48 bits
    flow.dl_dst has 48 bits
    flow.dl_type has 16 bits
    flow.vlan_id has 12 bits
    flow.nw_src has 32 bits
    flow.nw_dst has 32 bits
    flow.nw_proto has 8 bits
    flow.tp_src has 16 bits
    flow.tp_dst has 16 bits
    """
    if _if_q_intersect(bits):
        if bits[0:48] == 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx':
            dl_src = '*'
        else:
            dl_src =  "0x%x" % int(bits[0:48], 2)
            if len(dl_src) < 14:
                dl_src = '0'* (14-len(dl_src)) + dl_src[2:]
            else:
                dl_src = dl_src[2:]
            dl_src = dl_src[0:2]+':'+dl_src[2:4]+':'+dl_src[4:6]+':'+dl_src[6:8]+':'+dl_src[8:10]+':'+dl_src[10:12]
        if bits[48:96] == 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx':
            dl_dst = '*'
        else:
            dl_dst = "0x%x" % int(bits[48:96], 2)
            if len(dl_dst) < 14:
                dl_dst = '0'* (14-len(dl_dst)) + dl_dst[2:]
            else:
                dl_dst = dl_dst[2:]
            dl_dst = dl_dst[0:2]+':'+dl_dst[2:4]+':'+dl_dst[4:6]+':'+dl_dst[6:8]+':'+dl_dst[8:10]+':'+dl_dst[10:12]


        if bits[96:112] == 'xxxxxxxxxxxxxxxx':
            dl_type = '*'
        else:
            dl_type = str(int(bits[96:112],2))

        if bits[112:124] == 'xxxxxxxxxxxx':
            vlan_id = '*'
        else:
            vlan_id = str(int(bits[112:124],2))
    
        if bits[124:156] == 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx':
            nw_src = '*'
        else:
            nw_src = _interpret_bit2addr(bits[124:156])
        
        if bits[156:188] == 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx':
            nw_dst = '*'
        else:
            nw_dst = _interpret_bit2addr(bits[156:188])

        if bits[188:196] == 'xxxxxxxx':
            nw_proto = '*'
        else:
            nw_proto = str(int(bits[188:196],2))

        if bits[196:212] == 'xxxxxxxxxxxxxxxx':
            tp_src = '*'
        else:
            tp_src = str(int(bits[196:212],2))

        if bits[212:228] == 'xxxxxxxxxxxxxxxx':
            tp_dst = '*'
        else:
            tp_dst = str(int(bits[212:228],2))
        return FlowSpace('',1,dl_src,dl_dst,dl_type,vlan_id,nw_src,nw_dst,nw_proto,tp_src,tp_dst,'*')
    else:
        return 0

