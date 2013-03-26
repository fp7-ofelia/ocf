from django.db import models
from django.core import validators
from expedient.clearinghouse.resources.models import Resource
#from sample_resource.models import *
from sample_resource.utils.validators import validate_resource_name, validate_temperature_scale

TEMPERATURE_SCALE_CHOICES = (
                        ('C','Celsius'),
                        ('F','Fahrenheit'),
                        ('K','Kelvin'),
                      )
#HD_SETUP_TYPE_CHOICES = (
#                        ('file-image','File Image'),
#                      )
#VIRTUALIZATION_SETUP_TYPE_CHOICES = (
#                        ('paravirtualization','Paravirtualization'),
#                      )

class SampleResource(Resource):
    
    '''
    Sample Resource
    '''

    class Meta:
        """Meta Class for your model."""
        app_label = 'sample_resource'

#    uuid = models.CharField(max_length = 1024, default = "")

#    memory = models.IntegerField(blank = True, null=True, validators=[validate_memory])    
  #  cpuNumber = models.IntegerField(blank = True, null=True)

    temperature = models.FloatField(validators=[validators.MinLengthValidator(0)])
    temperature_scale = models.CharField(max_length = 10, choices = TEMPERATURE_SCALE_CHOICES,
#                        default = "celsius", validators = [validate_temperature_scale],
                        default = "C",
                        verbose_name = "Temperature scale")
#    operatingSystemType = models.CharField(max_length = 512, default="")
#    operatingSystemVersion = models.CharField(max_length = 512, default="")
#    operatingSystemDistribution = models.CharField(max_length = 512, default="")

    project_id = models.CharField(max_length = 1024, default = "")
    project_name = models.CharField(max_length = 1024, default = "")
    slice_id = models.CharField(max_length = 1024, default = "")
    slice_name = models.CharField(max_length = 1024, default = "")
#    state = models.CharField(max_length = 24, default="")

#    hdSetupType = models.CharField(max_length = 20, choices = HD_SETUP_TYPE_CHOICES, validators=[validate_hdSetupType], 
#                                   verbose_name = "HD Setup Type")
#    hdOriginPath = models.CharField(max_length = 1024, default="")    
#    virtualizationSetupType = models.CharField(max_length = 20, choices = VIRTUALIZATION_SETUP_TYPE_CHOICES,
#                                               validators=[validate_virtualizationSetupType],verbose_name = "Virtualization Setup Type")
    interfaces = models.ManyToManyField("SampleResourceInterface", blank = True, null = True)
    
#    disc_image = models.CharField(max_length = 20, choices = DISC_IMAGE_CHOICES,validators=[validate_discImage],
#                                  verbose_name = "Disc Image")
    

#    def setMemory(self,memory):
#        self.memory = memory

#    def getMemory(self):
#        return self.memory

    def clean(self):
        validate_temperature_scale([ t[0] for t in TEMPERATURE_SCALE_CHOICES ])
#        from django.core.exceptions import ValidationError
#        if self.temperature_scale not in [ t[0] for t in TEMPERATURE_SCALE_CHOICES ]:
#            raise ValidationError('Draft entries may not have a publication date.')

    def set_temperature(self, temperature):
        self.temperature = temperature

    def get_temperature(self):
        return self.temperature

    def set_temperature_scale(self, temperature_scale):
        self.temperature_scale = temperature_scale

    def get_temperature_scale(self):
        return self.temperature_scale

    def set_name(self, name):
        if not self.name:
            validate_resource_name(name)
            self.name = name

    def get_name(self):
        return self.name

    def set_uuid(self, uuid):
        self.uuid = uuid

    def get_uuid(self):
        return self.uuid

#    def setOStype(self, type):
#        self.operatingSystemType = type

#    def getOStype(self):
#        return self.operatingSystemType

#    def setOSversion(self, version):
#        self.operatingSystemVersion = version

#    def getOSversion(self):
#        return self.operatingSystemVersion

#    def setOSdist(self, dist):
#        self.operatingSystemDistribution = dist

#    def getOSdist(self):
#        return self.operatingSystemDistribution

#    def setServerID(self, server_id):
#        #from vt_manager.models.VTServer import VTServer
#        #self.serverID = VTServer.objects.get(name = server)
#        self.serverID = server_id

#    def getServerID(self):
#        return self.serverID

    def set_project_id(self, project_id):
        if not isinstance(project_id,str):
            project_id = str(project_id)
        self.project_id = project_id

    def get_project_id(self):
        return self.project_id

    def set_project_name(self,project_name):
        if not isinstance(project_name,str):
            project_name = str(project_name)
        self.project_name = project_name

    def get_project_name(self):
        return self.project_name

    def set_slice_id(self, value):
        self.slice_id = value

    def get_slice_id(self):
        return self.slice_id

    def set_slice_name(self, value):
        self.slice_name = value

    def get_slice_name(self):
        return self.slice_name    

#    def setState(self,state):
#        possibleStats = ('running', 'created (stopped)', 'stopped', 'unknown', 'failed', 'on queue', 'starting...', 'stopping...', 'creating...','deleting...','rebooting...')
#        if state not in possibleStats:
#            raise KeyError, "Unknown state"
#        else:
#            self.state = state

#    def getState(self):
#        return self.state

#    def setMacs(self):
#        macs = Mac.objects.filter(vmID = self.name)
#        for mac in macs:
#            self.macs.add(mac)
#
#    def getMacs(self):
#        return self.macs

#    def setIpType(self, ip, type):
#
#        if type is "ip":
#            self.ipControl = ip
#        elif type is "gw":
#            self.gw = ip
#        elif type is "dns1":
#            self.dns1 = ip
#        elif type is "dns2":
#            self.dns2 = ip

#    def getIpType(self, type):
#        if type is "ip":
#            return self.ipControl
#        elif type is "gw":
#            return self.gw
#        elif type is dns1:
#            return self.dns1
#        elif type is "dns2":
#            return self.dns2

#    def setHDsetupType(self, value):
#        self.hdSetupType = value

#    def getHDsetupType(self):
#        return self.hdSetupType

#    def setHDoriginPath(self, value):
#        self.hdOriginPath = value

#    def getHDoriginPath(self):
#        return self.hdOriginPath

#    def setVirtualizationSetupType(self, value):
#        self.virtualizationSetupType = value

#    def getVirtualizationSetupType(self):
#        return self.virtualizationSetupType

    def delete(self):
        self.action_set.clear()
        super(SampleResource, self).delete()

    def complete_delete(self):
        self.action_set.clear()
        for interface in self.interfaces.all():
            self.interfaces.remove(interface)
            interface.delete()
        super(SampleResource, self).delete()

class SampleResourceInterface(models.Model): 

    class Meta:
        """Meta Class for your model."""
        app_label = 'sample_resource' 

    name = models.CharField(max_length = 32, default="", blank = True, null=True)
    mac = models.CharField(max_length = 17, default="", blank = True, null=True)
    ip = models.IPAddressField(blank = True, null=True)
    gw = models.IPAddressField(blank = True, null=True)
    mask = models.IPAddressField(blank = True, null=True)
    dns1 = models.IPAddressField(blank = True, null=True)
    dns2 = models.IPAddressField(blank = True, null=True)
    bridge_interface = models.CharField(max_length = 32, default="", blank = True, null=True)

