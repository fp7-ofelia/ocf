from django.db import models
from django.contrib import auth
from vt_manager.models import *

class Ip(models.Model):
    """IP"""

    class Meta:
        """Meta Class for your model."""
        app_label = 'vt_manager'

    projectID = models.CharField(max_length = 1024, default="")
    amID = models.CharField(max_length = 1024, default="")
    AMslotID = models.IntegerField()
    hostID = models.IntegerField()
    ip =models.IPAddressField(blank = True, null=True)
    mask = models.IPAddressField(blank = True, null=True)
    gw = models.IPAddressField(blank = True, null=True)
    dns1 = models.IPAddressField(blank = True, null=True)
    dns2 = models.IPAddressField(blank = True, null=True)
    vmID = models.CharField(max_length = 1024, default="")
    serverID = models.CharField(max_length = 1024, default="")
    isMgmt = models.BooleanField()    
    ifaceName = models.CharField(max_length = 512, default="")    

    def setServerID(self, value):
        self.serverID = value

    def getServerID(self):
        return self.serverID

    def setHostID(self, value):
        self.hostID = value

    def getHostID(self):
        return self.hostID

    def setProjectID(self, value):
        self.projectID = value

    def setAMid(self, value):
        self.amID = value

    def setSliceID(self, value):
        self.sliceID = value

    def setAMslotID(self, value):
        self.AMslotID = value

    def getProjectID(self):
        return self.projectID

    def getAMid(self):
        return self.amID

    def getSliceID(self):
        return self.sliceID

    def getAMslotID(self):
        return self.AMslotID

    def setVMid(self, value):
        self.vmID = value

    def getHostID(self):
        return self.vmID

    def setIp(self, ip):

        #TODO change ExceptionIp handleing. Here it should just raise the Exception and the Controller should handle it        

        digits = '0123456789'
        if not isinstance(ip,str):
            ip = str(ip)
        for i in ip:
            if not i in (digits + '.'):
                handleFault(ExceptionIp,ip)
                return
        if (len(ip.split(".")) != 4) or (ip.split(".")[0] == '0') or (ip.split(".")[3] == '0') :
            handleFault(ExceptionIp,ip)
            return
        for i in ip.split("."):
            if not (int(i) >= 0 and int(i) < 256):
                handleFault(ExceptionIp,ip)
                return
        print "normalized ip: %s" % ip
        self.ip = ip
        return 1

    def getIp(self):
        return self.ip

