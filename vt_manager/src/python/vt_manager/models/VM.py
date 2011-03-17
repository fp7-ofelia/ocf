from django.db import models
from django.contrib import auth
from datetime import datetime
#from common.sfa.trust.gid import *
from vt_manager.models.faults import *
from vt_manager.models import Mac, Ip
#from vt_manager.models.Mac import Mac
#from vt_manager.models.Ip import Ip 

#TODO When an exception is raised because a wrong value, delete any previous value saved in that variable???

class VM(models.Model):
    """VM data model class"""

    class Meta:
        """Meta Class for your model."""
        app_label = 'vt_manager'
                
    uuid = models.CharField(max_length = 1024, default="")
    name = models.CharField(max_length = 512, default="")
    memory = models.IntegerField(blank = True, null=True)
    cpuNumber = models.IntegerField(blank = True, null=True)
    virtTech = models.CharField(max_length = 10, default="")
    operatingSystemType = models.CharField(max_length = 512, default="")
    operatingSystemVersion = models.CharField(max_length = 512, default="")
    operatingSystemDistribution = models.CharField(max_length = 512, default="")

    callBackURL = models.URLField()
    projectId = models.CharField(max_length = 1024, default="")
    projectName = models.CharField(max_length = 1024, default="")
    sliceId = models.CharField(max_length = 1024, default="")
    sliceName = models.CharField(max_length = 1024, default="")
    expedientId = models.IntegerField(blank = True, null=True)
    state = models.CharField(max_length = 24, default="")
    serverID = models.CharField(max_length = 1024, default="")    
    hdSetupType = models.CharField(max_length = 1024, default="")
    hdOriginPath = models.CharField(max_length = 1024, default="")
    virtualizationSetupType = models.CharField(max_length = 1024, default="")
    macs = models.ManyToManyField('Mac', blank = True, null = True)#, on_delete=models.SET_NULL) 
    ips = models.ManyToManyField('Ip', blank = True, null = True)

    def setMacs(self):
        macs = Mac.objects.filter(vmID = self.uuid)
        for mac in macs:
            self.macs.add(mac)

    def getMacs(self):
        return self.macs

    def setIPs(self):
        ips = Ip.objects.filter(vmID = self.uuid)
	for ip in ips:
            self.ips.add(ip)
	
    def getIPs(self):
        return self.macs


    def setProjectId(self,projectId):
        if not isinstance(projectId,str):
            projectId = str(projectId)
        self.projectId = projectId

    def getProjectId(self):
        return self.projectId

    def setProjectName(self,projectName):
        if not isinstance(projectName,str):
            projectName = str(projectName)
        self.projectName = projectName

    def getProjectName(self):
        return self.projectName

    def setSliceId(self, value):
        self.sliceId = value

    def getSliceId(self):
        return self.sliceId 

    def setSliceName(self, value):
        self.sliceName = value

    def getSliceName(self):
        return self.sliceName

    def setExpedientId(self,expedientId):
        if not isinstance(expedientId,int):
            expedientId = int(expedientId)
        self.expedientId = expedientId

    def getExpedientId(self):
        return self.expedientId

    def setState(self,state):
        possibleStats = ('running', 'created (stopped)', 'stopped', 'unknown', 'failed', 'on queue', 'starting...', 'stopping...', 'creating...','deleting...','rebooting...')
        if state not in possibleStats:
            raise KeyError, "Unknown state"
        else:
            self.state = state

    def getState(self):
        return self.state
		
    def setServerID(self, server_id):
        self.serverID = server_id

    def getServerID(self):
        return self.serverID

    def getMac(self):
        return self.mac

    def setMemory(self,memory):
        if not memory in range(1,4000):
            handleFault(ExceptionMemory,memory)
            return
        else:
            self.memory = memory

    def getMemory(self):
        return self.memory


    def setCpu(self):
        pass

    def setVirtTech(self,virtTech):
        possibleVirtTech = ('xen')
        if virtTech not in possibleVirtTech:
            raise KeyError, "Unknown Virtualization Technology"
        else:
            self.virtTech = virtTech

    def getVirtTech(self):
        return self.virtTech

    def setDiscSpace(self):
        pass

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def setUUID(self, uuid):
        self.uuid = uuid

    def getUUID(self):
        return self.uuid

    def setOStype(self, type):
        self.operatingSystemType = type

    def getOStype(self):
        return self.operatingSystemType

    def setOSversion(self, version):
        self.operatingSystemVersion = version

    def getOSversion(self):
        return self.operatingSystemVersion

    def setOSdist(self, dist):
        self.operatingSystemDistribution = dist

    def getOSdist(self):
        return self.operatingSystemDistribution

    def setHDsetupType(self, value):
        self.hdSetupType = value

    def getHDsetupType(self):
        return self.hdSetupType

    def setHDoriginPath(self, value):
        self.hdOriginPath = value

    def getHDoriginPath(self):
        return self.hdOriginPath

    def setVirtualizationSetupType(self, value):
        self.virtualizationSetupType = value

    def getVirtualizationSetupType(self):
        return self.virtualizationSetupType

    def setCallBackURL(self, url):
        self.callBackURL = url

    def getCallBackURL(self):
        return self.callBackURL

    def delete(self):
        self.action_set.clear()
        super(VM, self).delete()
