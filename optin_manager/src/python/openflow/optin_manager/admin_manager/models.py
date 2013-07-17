from django.db import models
from django.contrib import auth
from openflow.optin_manager.flowspace.models import FlowSpace
from common.xmlrpc_serverproxy.models import PasswordXMLRPCServerProxy

class RequestedAdminFlowSpace(FlowSpace):
    '''
    Admin FLowSpace requests, waiting for approval from the supervisor
    '''
    user            = models.ForeignKey(auth.models.User, related_name = "admin_fs_requester")
    admin           = models.ForeignKey(auth.models.User, related_name = "admin_fs_approver")
    req_priority    = models.IntegerField()

class RequestedUserFlowSpace(FlowSpace):
    '''
    User FLowSpace requests, waiting for admin approval
    '''
    user            = models.ForeignKey(auth.models.User, related_name = "user_fs_requester")
    admin           = models.ForeignKey(auth.models.User, related_name = "user_fs_approver")
    
    
class AdminPromoteRequest(models.Model):
    '''
    The database table to store a request for promtion to admin 
    '''
    user            = models.ForeignKey(auth.models.User, related_name = "admin_requester")
    admin           = models.ForeignKey(auth.models.User, related_name = "admin_approver")
    text            = models.CharField(max_length = 8192)
    requested_position = models.CharField(max_length = 1024)
    
class AdminAutoApproveScript(models.Model):
    '''
    The database table to store information about the auto-approve script used by an admin
    '''
    admin           = models.ForeignKey(auth.models.User)
    remote          = models.BooleanField("Remote Auto Approve Server", default= False)
    script_name     = models.CharField(max_length = 1024, default="Manual")
    
    def __unicode__(self):
        return "admin: %s, script: %s, remote: %s"%(self.admin.username,self.script_name,self.remote)
    
    
class AutoApproveServerProxy(PasswordXMLRPCServerProxy):
    '''
    If an admin uses a remote xmlrpc server to approve user flowspace requests, then
    there will be one entry for that admin here.
    '''
    admin           = models.ForeignKey(auth.models.User)