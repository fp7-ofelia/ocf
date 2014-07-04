from django.db import models

class VirtualMachineKeys(models.Model):
    """VM data model class"""

    class Meta:
        """Meta Class for your model."""
        app_label = 'vt_manager'

    ''' General parameters '''
    uuid = models.CharField(max_length = 1024, default="")
    
    ''' Resource parameters '''
    project_uuid = models.CharField(max_length = 1024, default="")
    slice_uuid = models.CharField(max_length = 1024, default="")
    vm_uuid = models.CharField(max_length = 1024, default="")
    user_name = models.CharField(max_length = 128, default="")

    '''SSH keys'''
    ssh_key = models.CharField(max_length = 2048, default="")

    def get_uuid(self):
        return self.uuid

    def set_uuid(self, uuid):
        self.uuid = uuid

    def get_project_uuid(self):
        return self.project_uuid

    def set_project_uuid(self, project_uuid):
        self.project_uuid = project_uuid

    def get_slice_uuid(self):
        return self.slice_uuid

    def set_slice_uuid(self, slice_uuid):
        self.slice_uuid = slice_uuid

    def get_vm_uuid(self):
        return self.vm_uuid

    def set_vm_uuid(self, vm_uuid):
        self.vm_uuid = vm_uuid

    def get_user_name(self):
        return self.user_name
    
    def set_user_name(self, user_name):
        self.user_name = user_name    

    def get_ssh_key(self):
        return self.ssh_key

    def set_ssh_key(self, ssh_key):
        self.ssh_key = ssh_key
