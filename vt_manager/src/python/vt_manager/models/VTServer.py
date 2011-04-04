from django.db import models
from django.contrib import auth
#from common.sfa.trust.gid import *
import uuid
#from vt_manager.models.VM import VM
from vt_manager.models import *

class VTServer(models.Model):
    """Virtualization Server class"""

    VIRT_TECH_CHOICES = (
        ('xen', 'XEN'),
        ('Other', 'Other'),
    )

    OS_DIST_CHOICES = (
        ('Debian', 'Debian'),
        ('Ubuntu', 'Ubuntu'),
        ('RedHat', 'RedHat'),
        ('Other', 'Other'),
    )

    OS_VERSION_CHOICES = (
        ('5.0', '5.0'),
        ('6.0', '6.0'),
        ('Other', 'Other'),
    )

    OS_TYPE_CHOICES = (
        ('Windows', 'Windos'),
        ('GNU/Linux', 'GNU/Linux'),
        ('Other', 'Other'),
    )

    class Meta:
        """Meta Class for your model."""
        app_label = 'vt_manager'
    

    name = models.CharField(max_length = 511, default="", verbose_name = "Name")
    operatingSystemType = models.CharField(choices = OS_TYPE_CHOICES,max_length = 512, verbose_name = "OS Type")
    operatingSystemDistribution = models.CharField(choices = OS_DIST_CHOICES,max_length = 512, verbose_name = "OS Distribution")
    operatingSystemVersion = models.CharField(choices = OS_VERSION_CHOICES,max_length = 512, verbose_name = "OS Version")
    virtTech = models.CharField(choices = VIRT_TECH_CHOICES, max_length = 512, verbose_name = "Virtualization Technology")
    agentURL = models.URLField(verify_exists = False, verbose_name = "URL of the Server Agent")
    url = models.URLField(verify_exists = False, verbose_name = "URL of the Server")
    ipRange = models.IPAddressField(verbose_name = "VM IP range")#, help_text = "Range of IP to provide to the VMs")
    mask = models.IPAddressField(verbose_name = "Subnet mask")
    gw = models.IPAddressField(verbose_name = "Gateway")
    dns1 = models.IPAddressField(verbose_name = "DNS 1")
    dns2 =  models.IPAddressField(verbose_name = "DNS 2")

    uuid = models.CharField(max_length = 1024, default = uuid.uuid4(), editable = False)
    memory = models.IntegerField(blank = True, null=True,editable = False)
    vms = models.ManyToManyField('VM', blank = True, null = True, editable = False)
    freeDiscSpace = models.IntegerField(blank = True, null=True, editable = False)
    freeMemory = models.IntegerField(blank = True, null=True, editable = False)
    freeCpu = models.DecimalField(max_digits=3, decimal_places=2,blank = True, null=True, editable = False)

    ifaces = models.ManyToManyField('VTServerIface', blank = True, null = True, editable = False)

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def setUUID(self, uuid):
        self.uuid = uuid

    def getUUID(self):
        return self.uuid
    
    def setMemory(self,memory):
        if not memory in range(1,4000):
            handleFault(ExceptionMemory,memory)
            return
        else:
            self.memory = memory

    def getMemory(self):
        return self.memory


    def setAgentURL(self, url):
        self.agentURL = url

    def getAgentURL(self):
        return self.agentURL

    def setURL(self, url):
        self.url = url

    def getURL(self):
        return self.url

    def setVirtTech(self, virtTech):
         self.virtTech = virtTech

    def getVirtTech(self):
        return self.virtTech

    def setFreeDiscSpace(self):
        pass

    def getFreeDiscSpace(self):
        pass

    def setFreeMemory(self):
        pass

    def getFreeMemory(self):
        pass

    def setFreeCpu(self):
        pass

    def getFreeCpu(self):
        pass
    
    def setIpRange(self, value):
        self.ipRange = value

    def getIpRange(self):
        return self.ipRange

    def setGW(self, value):
        self.gw = value

    def getGW(self):
        return self.gw

    def setMask(self, value):
        self.mask = value

    def getMask(self):
        return self.mask

    def setDNS1(self, value):
        self.dns1 = value

    def getDNS1(self):
        return self.dns1

    def setDNS2(self, value):
        self.dns2 = value

    def getDNS2(self):
        return self.dns2
    
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
    
    def setVMs(self):
        vms = VM.objects.filter(serverID = self.name)
        for vm in vms:
            self.vms.add(vm)
