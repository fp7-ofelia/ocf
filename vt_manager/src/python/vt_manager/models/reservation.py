from django.db import models
from vt_manager.models.XenServer import XenServer

class Reservation(models.Model):

    class Meta:
        app_label = 'vt_manager'

    valid_until = models.CharField(max_length = 1024, default="") 
    is_provisioned = models.BooleanField(default=False) 
    server = models.ForeignKey(XenServer, related_name="reservation")

    name = models.CharField(max_length = 512, default="", verbose_name = "Reservation name")
    projectName = models.CharField(max_length = 1024, default="")
    sliceName = models.CharField(max_length = 1024, default="")
    uuid  = models.CharField(max_length = 1024, default="")
    

    def get_name(self):
        return self.name

    def get_project_name(self):
        return self.projectName

    def get_slice_name(self):
        return self.sliceName

    def get_valid_until(self):
        return self.valid_until

    def get_provisioned(self):
        return self.is_provisioned
     
    def set_name(self, value):
        self.name = value

    def set_project_name(self, value):
        self.projectName = value

    def set_slice_name(self, value):
        self.sliceName = value

    def set_valid_until(self, value):
        self.valid_until = value

    def set_provisioned(self, value):
        self.is_provisioned = value
