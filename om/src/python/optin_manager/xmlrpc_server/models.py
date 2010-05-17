from django.db import models
from clearinghouse.xmlrpc_serverproxy.models import PasswordXMLRPCServerProxy
from optin_manager.flowspace.models import  Experiment, ExperimentFLowSpace
from optin_manager.flowspace.utils import long_to_dpid, dpid_to_long

class FVServerProxy(PasswordXMLRPCServerProxy):
    name = models.CharField("FV name",max_length = 40)
    
    def changePassword(self, sliceName, new_password):
        success = self.fv.change_password(sliceName, new_password)
        return success
        
    def get_switches(self):
        """
        Change from FV format to CH format
        """
        dpids = self.fv.listDevices()
        infos = [self.fv.getDeviceInfo() for d in dpids]
        dpids = map(dpid_to_long, dpids)
        return zip(dpids, infos)
    
    def get_links(self):
        """
        Change from FV format to CH format
        """
        return [(dpid_to_long(l.pop("srcDPID")),
                 l.pop("srcPort"),
                 dpid_to_long(l.pop("dstDPID")),
                 l.pop("dstPort"),
                 l) for l in self.fv.getLinks()]
    
    def addNewSlice(self,sliceName, passwd, controller, slice_email):
        return self.fv.createSlice(sliceName, passwd, controller, slice_email)
    
    def deleteSlice(self,sliceName):
        success = self.fv.deleteSlice(sliceName)
        return success
            

class CallBackServerProxy(models.Model):
    '''
    Stores some information for simple callbacks.
    '''
    
    username = models.CharField(max_length=100)
    url = models.URLField("Server URL", max_length=1024, verify_exists=False)
    cookie = models.TextField()

    def __getattr__(self, name):
        if name == "proxy":
            from xmlrpclib import ServerProxy
            self.proxy = ServerProxy(self.url)
            return self.proxy
        else:
            return getattr(self.proxy, name)
        
    def is_available(self):
        '''Call the server's ping method, and see if we get a pong'''
        try:
            if self.ping("PING") == "PONG: PING":
                return True
        except Exception, e:
            import traceback
            print "Exception while pinging server: %s" % e
            traceback.print_exc()
        return False
    