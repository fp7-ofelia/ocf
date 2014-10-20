from django.db import models
from django.contrib import auth
from datetime import datetime
from vt_manager.models.faults import *
import re
import inspect 
from vt_manager.models.VirtualMachine import VirtualMachine
from vt_manager.models.XenServer import XenServer

class Reservation(VirtualMachine):

    class Meta:
        app_label = 'vt_manager'

    valid_until =  models.CharField(max_length = 1024, default="") 
    server = models.ForeignKey(XenServer, related_name="reservation")        

    def get_name(self):
        return self.name

    def get_uuid(self):
        return self.uuid

    def get_project_id(self):
        return self.projectId

    def get_project_name(self):
        return self.projectName

    def get_slice_id(self):
        return self.sliceId

    def get_slice_name(self):
        return self.sliceName

    def get_memory(self):
        return self.memory

    def get_callback_url(self):
        return self.callBackUrl

    def get_valid_until(self):
        return self.valid_until
 
    def set_name(self, value):
        self.name = value

    def set_uuid(self, value):
        self.uuid = value

    def set_project_id(self, value):
        self.projectId = value

    def set_project_name(self, value):
        self.projectName = value

    def set_slice_id(self, value):
        self.sliceId = value

    def set_slice_name(self, value):
        self.sliceName = value

    def set_memory(self, value):
        self.memory = value

    def set_call_back_url(self, value):
        self.callBackUrl = value

    def set_valid_until(self, value):
        self.valid_until = value
