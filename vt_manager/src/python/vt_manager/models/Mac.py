from django.db import models
from django.contrib import auth
from vt_manager.models import *

class Mac(models.Model):
    """MAC"""

    class Meta:
        """Meta Class for your model."""
        app_label = 'vt_manager'

    projectID = models.CharField(max_length = 1024, default="")
    amID = models.CharField(max_length = 1024, default="")
    sliceID = models.CharField(max_length = 1024, default="")
    slotID = models.IntegerField()
    AMslotID = models.IntegerField()
    HostID = models.IntegerField()
    mac = models.CharField(max_length = 17, default="")
    vmID = models.CharField(max_length = 1024, default="")
    isMgmt = models.BooleanField()
    ifaceName = models.CharField(max_length = 512, default="") 

    def setHostID(self, value):
        self.HostID = value

    def getHostID(self):
        return self.HostID

    def setProjectID(self, value):
        self.projectID = value

    def setAMid(self, value):
        self.amID = value

    def setSliceID(self, value):
        self.sliceID = value

    def setSlotID(self, value):
        self.slotID = value

    def setAMslotID(self, value):
        self.AMslotID = value

    def setMAC(self, value):
        self.mac = value

    def getProjectID(self):
        return self.projectID

    def getAMid(self):
        return self.amID

    def getSliceID(self):
        return self.sliceID

    def getSlotID(self):
        return self.slotID

    def getAMslotID(self):
        return self.AMslotID

    def getMAC(self):
        return self.mac

    def setVMid(self, value):
        self.vmID = value

    def getHostID(self):
        return self.vmID
