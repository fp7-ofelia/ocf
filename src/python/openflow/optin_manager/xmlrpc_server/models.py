from django.db import models
from expedient.common.xmlrpc_serverproxy.models import PasswordXMLRPCServerProxy

class FVServerProxy(PasswordXMLRPCServerProxy):
    name = models.CharField("FV name",max_length = 40)
    

    @classmethod
    def get_or_create_fv(self):
        fv = self.objects.all()
        if (len(fv) == 0):
            fv = self.objects.create(name="",
                username="",
                password="",
                url = "",)
        else:
            fv = fv[0]

        return fv
    

    def get_switches(self):
        """
        Change from FV format to CH format
        """
        dpids = self.api.listDevices()
        infos = [self.api.getDeviceInfo(d) for d in dpids]
        return zip(dpids, infos)
    
    def get_links(self):
        """
        Change from FV format to CH format
        """
        return [(l.pop("srcDPID"),
                 l.pop("srcPort"),
                 l.pop("dstDPID"),
                 l.pop("dstPort"),
                 l) for l in self.api.getLinks()]

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
    