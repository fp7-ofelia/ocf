from sfa.util.faults import *
from sfa.util.misc import *
from sfa.util.rspec import Rspec
from sfa.server.registry import Registries
from sfa.plc.nodes import *
import sys

# Probably the following is not essential
#from soaplib.wsgi_soap import SimpleWSGISoapApp
#from soaplib.serializers.primitive import *
#from soaplib.serializers.clazz import *

import socket
import struct

SOAP_INTERFACE_PORT = 7889
AGGREGATE_MANAGER_PORT = 2603
AGGREGATE_MANAGER_IP = 'localhost'
#AGGREGATE_MANAGER_IP = 'openflowvisor.stanford.edu'

# Message IDs for all the GENI light calls
# This will be used by the aggrMgr controller
SFA_GET_RESOURCES = 101
SFA_CREATE_SLICE = 102
SFA_START_SLICE = 103
SFA_STOP_SLICE = 104
SFA_DELETE_SLICE = 105
SFA_GET_SLICES = 106
SFA_RESET_SLICES = 107

DEBUG = 1

def print_buffer(buf):
    for i in range(0,len(buf)):
        print('%x' % buf[i])

def extract(sock):
    # Shud we first obtain the message length?
    # msg_len = socket.ntohs(sock.recv(2))
    msg = ""

    while (1):
        try:
            chunk = sock.recv(1)
        except socket.error, message:
            if 'timed out' in message:
                break
            else:
                sys.exit("Socket error: " + message)

        if len(chunk) == 0:
            break
        msg += chunk

    print 'done extracting response from aggrMgr'
    return msg
   
def connect(server, port):
    '''Connect to the Aggregate Manager module'''
    sock = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
    sock.connect ( ( server, port) )
    sock.settimeout(1)
    print 'connected to aggregate manager module'
    return sock
    
def connect_aggrMgr():
    return connect(AGGREGATE_MANAGER_IP, AGGREGATE_MANAGER_PORT)

def generate_slide_id(cred, hrn):
    if cred == None:
        cred = ""
    if hrn == None:
        hrn = ""
    return cred + '_' + hrn

def msg_aggrMgr(cred, hrn, msg_id):
    slice_id = generate_slide_id(cred, hrn)

    msg = struct.pack('> B%ds' % len(slice_id), msg_id, slice_id)
    buf = struct.pack('> H', len(msg)+2) + msg

    try:
        aggrMgr_sock = connect_aggrMgr()
        aggrMgr_sock.send(buf)
        aggrMgr_sock.close()
        return 1
    except socketerror, message:
        print "Socket error"
    except IOerror, message:
        print "IO error"
    return 0

def start_slice(cred, hrn):
    if DEBUG: print "Received start_slice call"
    return msg_aggrMgr(SFA_START_SLICE)

def stop_slice(cred, hrn):
    if DEBUG: print "Received stop_slice call"
    return msg_aggrMgr(SFA_STOP_SLICE)

def delete_slice(cred, hrn):
    if DEBUG: print "Received delete_slice call"
    return msg_aggrMgr(SFA_DELETE_SLICE)

def reset_slices(cred, hrn):
    if DEBUG: print "Received reset_slices call"
    return msg_aggrMgr(SFA_RESET_SLICES)

def create_slice(cred, hrn, rspec):
    if DEBUG: print "Received create_slice call"
    slice_id = generate_slide_id(cred, hrn)

    msg = struct.pack('> B%ds%ds' % len(slice_id), SFA_CREATE_SLICE, slice_id, rspec)
    buf = struct.pack('> H', len(msg)+2) + msg

    try:
        aggrMgr_sock = connect_aggrMgr()
        aggrMgr_sock.send(buf)
        aggrMgr_sock.close()
        return 1
    except socketerror, message:
        print "Socket error"
    except IOerror, message:
        print "IO error"
    return 0

def get_resources(cred, hrn=None):
    if DEBUG: print "Received get_resources call"
    slice_id = generate_slide_id(cred, hrn)

    msg = struct.pack('> B%ds' % len(slice_id), SFA_GET_RESOURCES, slice_id)
    buf = struct.pack('> H', len(msg)+2) + msg

    try:
        aggrMgr_sock = connect_aggrMgr()
        aggrMgr_sock.send(buf)
        resource_list = extract(aggrMgr_sock);
        aggrMgr_sock.close()

        return resource_list 
    except socketerror, message:
        print "Socket error"
    except IOerror, message:
        print "IO error"
    return None

def fetch_context(slice_hrn, user_hrn, contexts):
    return None

def main():
    r = Rspec()
    r.parseFile(sys.argv[1])
    rspec = r.toDict()
    create_slice(None,'plc',rspec)
    
if __name__ == "__main__":
    main()
