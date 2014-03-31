from django.db import models
#from django.db.models.fields import IPAddressField
from expedient.clearinghouse.resources.models import Resource
from vt_plugin.models import *
from vt_plugin.utils.validators import *

DISC_IMAGE_CHOICES = (
                        ('default','Default'),
                        ('spirent','Spirent'),
                        ('irati','IRATI'),
                        ('debian7','Debian Wheezy'),
                        #('test','Test'),
                      )
HD_SETUP_TYPE_CHOICES = (
                        ('file-image','File Image'),
                        #('logical-volume-image','Logical Volume'),
                        ('full-file-image','File Image with Partitions'),
                      )
VIRTUALIZATION_SETUP_TYPE_CHOICES = (
                        ('paravirtualization','Paravirtualization'),
                        ('hvm','HVM'),
                      )
class VM(Resource):
    
    '''
    virtual machine class
    '''

    uuid = models.CharField(max_length = 1024, default="")
    memory = models.IntegerField(blank = True, null=True, validators=[validate_memory])
    
  #  cpuNumber = models.IntegerField(blank = True, null=True)
    virtTech = models.CharField(max_length = 10, default="")
    operatingSystemType = models.CharField(max_length = 512, default="")
    operatingSystemVersion = models.CharField(max_length = 512, default="")
    operatingSystemDistribution = models.CharField(max_length = 512, default="")

    projectId = models.CharField(max_length = 1024, default="")
    projectName = models.CharField(max_length = 1024, default="")
    sliceId = models.CharField(max_length = 1024, default="")
    sliceName = models.CharField(max_length = 1024, default="")
#    ipControl = models.IPAddressField(blank = True, null=True)
#    gw = models.IPAddressField(blank = True, null=True)
#    dns1 = models.IPAddressField(blank = True, null=True)
#    dns2 = models.IPAddressField(blank = True, null=True)
    state = models.CharField(max_length = 24, default="")

    serverID = models.CharField(max_length = 1024, default="")

    #serverID = models.CharField(max_length = 1024, default="")    
    #hdSetupType = models.CharField(max_length = 1024, default="")
    hdSetupType = models.CharField(max_length = 20, choices = HD_SETUP_TYPE_CHOICES, validators=[validate_hdSetupType], 
                                   verbose_name = "HD Setup Type")
    hdOriginPath = models.CharField(max_length = 1024, default="")    
    #virtualizationSetupType = models.CharField(max_length = 1024, default="")
    virtualizationSetupType = models.CharField(max_length = 20, choices = VIRTUALIZATION_SETUP_TYPE_CHOICES,
                                               validators=[validate_virtualizationSetupType],verbose_name = "Virtualization Setup Type")
#    macs = models.ManyToManyField('Mac', blank = True, null = True)#, on_delete=models.SET_NULL)
    ifaces = models.ManyToManyField('iFace', blank = True, null = True)
    
    disc_image = models.CharField(max_length = 20, choices = DISC_IMAGE_CHOICES,validators=[validate_discImage],
                                  verbose_name = "Disc Image")
    
    class Meta:
        """Meta Class for your model."""
        app_label = 'vt_plugin'


    def setMemory(self,memory):
        self.memory = memory

    def getMemory(self):
        return self.memory

    def setVirtTech(self,virtTech):
        self.virtTech = virtTech

    def getVirtTech(self):
        return self.virtTech

    def setName(self, name):
        if not self.name:
            resourceVMNameValidator(name)
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

    def setServerID(self, server_id):
        #from vt_manager.models.VTServer import VTServer
        #self.serverID = VTServer.objects.get(name = server)
        self.serverID = server_id

    def getServerID(self):
        return self.serverID

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

    def setState(self,state):
        possibleStats = ('running', 'created (stopped)', 'stopped', 'unknown', 'failed', 'on queue', 'starting...', 'stopping...', 'creating...','deleting...','rebooting...')
        if state not in possibleStats:
            raise KeyError, "Unknown state"
        else:
            self.state = state

    def getState(self):
        return self.state

#    def setMacs(self):
#        macs = Mac.objects.filter(vmID = self.name)
#        for mac in macs:
#            self.macs.add(mac)
#
#    def getMacs(self):
#        return self.macs

    def setIpType(self, ip, type):

        if type is "ip":
            self.ipControl = ip
        elif type is "gw":
            self.gw = ip
        elif type is "dns1":
            self.dns1 = ip
        elif type is "dns2":
            self.dns2 = ip

    def getIpType(self, type):
        if type is "ip":
            return self.ipControl
        elif type is "gw":
            return self.gw
        elif type is dns1:
            return self.dns1
        elif type is "dns2":
            return self.dns2

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

    def setDiskImage(self, image):
        self.disc_image = image

    def gettDiskImage(self):
        return self.disc_image 

    def delete(self):
        self.action_set.clear()
        super(VM, self).delete()

    def completeDelete(self):
        self.action_set.clear()
        for iface in self.ifaces.all():
            self.ifaces.remove(iface)
            iface.delete()
        super(VM, self).delete()

