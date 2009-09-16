from soaplib.wsgi_soap import SimpleWSGISoapApp
from soaplib.service import soapmethod

from soaplib.serializers.primitive import *
from soaplib.serializers.clazz import *

import socket
import struct
import sys

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

##
# The GeniServer class provides stubs for executing Geni operations at
# the Aggregate Manager.

class GeniLightServer(SimpleWSGISoapApp):
    def __init__(self):
        self.__tns__ = "http://yuba.stanford.edu/geniLight/"

    def msg_aggrMgr(self, cred, hrn, msg_id):
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

    # implicitly no __init__()
    @soapmethod(String,String,_returns=Integer)
    def start_slice(self, cred, hrn):
        if DEBUG: print "Received start_slice call"
        return msg_aggrMgr(SFA_START_SLICE)

    @soapmethod(String,String,_returns=Integer)
    def stop_slice(self, cred, hrn):
        if DEBUG: print "Received stop_slice call"
        return msg_aggrMgr(SFA_STOP_SLICE)

    @soapmethod(String,String,_returns=Integer)
    def delete_slice(self, cred, hrn):
        if DEBUG: print "Received delete_slice call"
        return msg_aggrMgr(SFA_DELETE_SLICE)

    @soapmethod(String,String,_returns=Integer)
    def reset_slices(self, cred, hrn):
        if DEBUG: print "Received reset_slices call"
        return msg_aggrMgr(SFA_RESET_SLICES)

    @soapmethod(String,String,String,_returns=String)
    def create_slice(self, cred, hrn, rspec):
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

    @soapmethod(String,_returns=String)
    def get_slices(self, cred):
        if DEBUG: print "Received get_slices call"
        msg = struct.pack('> B%ds%ds' % len(cred), SFA_GET_SLICES, cred)
        buf = struct.pack('> H', len(msg)+2) + msg

        try:
            aggrMgr_sock = connect_aggrMgr()
            aggrMgr_sock.send(buf)
            slice_list = extract(aggrMgr_sock);
            aggrMgr_sock.close()

            return slice_list
        except socketerror, message:
            print "Socket error"
        except IOerror, message:
            print "IO error"
        return None

    @soapmethod(String,String,_returns=Array(String))
    def get_resources(self, cred, hrn=None):
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

if __name__=='__main__':
    try:from cherrypy.wsgiserver import CherryPyWSGIServer
    except:from cherrypy._cpwsgiserver import CherryPyWSGIServer
    
    if len(sys.argv) > 2:
        AGGREGATE_MANAGER_IP = sys.argv[1]
        AGGREGATE_MANAGER_PORT = int(sys.argv[2])
        
    gls = GeniLightServer()
    server = CherryPyWSGIServer(('localhost',SOAP_INTERFACE_PORT),gls)

    try:
        server.start()
    except (KeyboardInterrupt):
        sys.exit(0)
