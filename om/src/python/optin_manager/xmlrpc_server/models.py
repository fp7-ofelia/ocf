from django.db import models
from clearinghouse.xmlrpc_serverproxy.models import PasswordXMLRPCServerProxy
from optin_manager.flowspace.models import Topology, Experiment, ExperimentFLowSpace

class CallBackFVProxy(models.Model):
    fv = models.ForeignKey(PasswordXMLRPCServerProxy)
    
    def changePassword(self, sliceName, new_password):
        success = self.fv.change_password(sliceName, new_password)
        return success
        
    def get_switches(self):
        devices = self.fv.listDevices()
        return devices
    
    def get_links(self):
        links = self.fv.getLinks()
        return links
    
    def addNewSlice(self,sliceName, passwd, controller, slice_email):
        success = self.fv.createSlice(sliceName, passwd, controller, slice_email)
        return success
    
    def deleteSlice(self,sliceName):
        success = self.fv.deleteSlice(sliceName)
        return success
    
    def updateTopology(self):
        devices = self.fv.listDevices()
        links = self.fv.getLinks()
        Topology.objects.all().delete()
        for device in devices:
            t = Topology(dpid = device)
            t.save()
        for link in links:
            dstDPID = link['dstDPID']
            srcDPID = link['srcDPID']
            srcsw = Topology.objects.filter(dpid = srcDPID)
            dstsw = Topology.objects.filter(dpid = dstDPID)
            if (srcsw and dstsw):
                srcsw.egress_connections.add(dstsw)
            
            
        

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
    