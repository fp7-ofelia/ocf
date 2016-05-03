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
    disk_image = models.CharField(max_length = 1024, default="")
    disk_memory = models.IntegerField(default=512)
    uuid = models.CharField(max_length = 1024, default="")

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

    def get_disk_image(self):
        return self.disk_image

    def get_disk_memory(self):
        return self.disk_memory

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

    def set_disk_image(self, value):
        self.disk_image = value

    def set_disk_memory(self, value):
        self.disk_memory = value

