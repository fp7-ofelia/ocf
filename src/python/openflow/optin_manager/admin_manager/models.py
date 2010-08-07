from django.db import models
from django.contrib import auth
from openflow.optin_manager.flowspace.models import FlowSpace
from expedient.common.xmlrpc_serverproxy.models import PasswordXMLRPCServerProxy

class RequestedAdminFlowSpace(FlowSpace):
    '''
    Admin FLowSpace requests, waiting for higher level admin approval
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
    
    
class AdminAutoApproveScript(models.Model):
    admin           = models.ForeignKey(auth.models.User)
    remote          = models.BooleanField("Remote Auto Approve Server", default= False)
    script_name     = models.CharField(max_length = 1024, default="Manual")
    
    def __unicode__(self):
        return "admin: %s, script: %s, remote: %s"%(self.admin.username,self.script_name,self.remote)
    
    
class AutoApproveServerProxy(PasswordXMLRPCServerProxy):
    admin           = models.ForeignKey(auth.models.User)