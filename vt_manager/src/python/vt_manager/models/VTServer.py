from django.db import models
from django.contrib import auth
import re
import uuid
#from vt_manager.models.VM import VM
from vt_manager.models import *
from vt_manager.settings import ISLAND_NETMASK, ISLAND_IP_RANGE, ISLAND_GW, ISLAND_DNS1, ISLAND_DNS2
from django.core.exceptions import ValidationError

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
        ('Windows', 'Windows'),
        ('GNU/Linux', 'GNU/Linux'),
        ('Other', 'Other'),
    )

    class Meta:
        """Meta Class for your model."""
        app_label = 'vt_manager'

    def validate_agentURL(value):
        def error():
            raise ValidationError(
                "Invalid URL of the Server Agent. Format should be \"https://ip:port\"",
                code="invalid", 
            )
        cntrlr_url_re = re.compile("https://(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?):(?P<port>\d*)")
        m = cntrlr_url_re.match(value)
        if m:
            port = m.group("port")
            if not port:
                error()
            else:
                port = int(port)
                if port > 2**16-1:
                    error()
        else:
            error()

    available = models.BooleanField(default=1)
    name = models.CharField(max_length = 511, default="", verbose_name = "Name")
    operatingSystemType = models.CharField(choices = OS_TYPE_CHOICES,max_length = 512, verbose_name = "OS Type")
    operatingSystemDistribution = models.CharField(choices = OS_DIST_CHOICES,max_length = 512, verbose_name = "OS Distribution")
    operatingSystemVersion = models.CharField(choices = OS_VERSION_CHOICES,max_length = 512, verbose_name = "OS Version")
    virtTech = models.CharField(choices = VIRT_TECH_CHOICES, max_length = 512, verbose_name = "Virtualization Technology")
    agentURL = models.URLField(verify_exists = False, verbose_name = "URL of the Server Agent", validators=[validate_agentURL])
    url = models.URLField(verify_exists = False, verbose_name = "URL of the Server", editable = False, blank = True)
    ipRange = models.IPAddressField(default = ISLAND_IP_RANGE, verbose_name = "VM IP range", editable = False)
    mask = models.IPAddressField(default = ISLAND_NETMASK, verbose_name = "Subnet mask", editable = False)
    gw = models.IPAddressField(default= ISLAND_GW , verbose_name = "Gateway", editable = False)
    dns1 = models.IPAddressField(default = ISLAND_DNS1, verbose_name = "DNS 1", editable = False)
    dns2 =  models.IPAddressField(default = ISLAND_DNS2, verbose_name = "DNS 2", blank = True, null = True, editable = False)
    vmMgmtIface = models.CharField(max_length = 1024, default = "", verbose_name = "Server Mgmt Bridge")
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

    def setAvailable(self,av):
        self.available = av

    def getAvailable(self):
        return self.available
    
    def setVmMgmtIface(self, ifaceName):
        self.vmMgmtIface = ifaceName
        
    def getVmMgmtIface(self):
        return self.vmMgmtIface
