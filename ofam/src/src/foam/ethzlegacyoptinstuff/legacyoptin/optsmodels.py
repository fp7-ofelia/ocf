#from django.db import models
#from django.contrib import auth
from foam.ethzlegacyoptinstuff.legacyoptin.flowspacemodels import FlowSpace

#obsolete
'''
class UserFlowSpace(FlowSpace):
    #Holds information about the verified flowspace for each user
    user            = models.ForeignKey(auth.models.User, related_name = "user")        
    approver     = models.ForeignKey(auth.models.User, related_name = "approver")
'''

#obsolete
'''
class AdminFlowSpace(FlowSpace):
    #Holds information about the verified flowspace for each admin
    #This is the flowspace that can be delegated to each user
    user           = models.ForeignKey(auth.models.User)
'''
      
'''
Experiment, ExperimentFlowSpace stores information about each experiment
'''    
class Experiment(object): #(models.Model):
    ''' 
    Holds information about the topology and flowspace request of an experiment
    '''
    slice_id            = None #models.CharField(max_length = 1024)
    project_name        = None #models.CharField(max_length = 1024)
    project_desc        = None #models.CharField(blank=True, max_length = 1024)
    slice_name          = None #models.CharField(max_length = 1024)
    slice_desc          = None #models.CharField(blank=True, max_length = 1024)
    controller_url      = None #models.CharField(max_length = 1024)
    owner_email         = None #models.CharField(blank=True, max_length = 1024)
    owner_password      = None #models.CharField(blank=True, max_length = 2048)
    
    # TODO: takeout the replacement when Rob fixes the . escaping in FV
    def get_fv_slice_name(self):
        s = "%s ID: %s" % (self.slice_name, self.slice_id)
        return s.replace(".", "_").replace(":", "_").replace("=", "_").replace(" ", "_").replace("'","_")
    
    def __unicode__(self):
        return "experiment: %s:%s" % (self.project_name,self.slice_name)

class ExperimentFLowSpace(FlowSpace):
    dpid          = None #models.CharField(max_length = 30)
    direction     = None #models.IntegerField(default = 2)  #0:ingress 1:egress 2:bi-directional
    port_number_s = None #models.IntegerField("Start of Port Range", blank=True, default=0)
    port_number_e = None #models.IntegerField("End of Port Range", blank=True, default=0xFFFF)
    exp           = None #models.ForeignKey(Experiment)
    def __unicode__(self):
        fs_desc = super(ExperimentFLowSpace, self).__unicode__()
        
        pn = ""
        if self.port_number_s == self.port_number_e:
            pn = ", port number: %d"%self.port_number_s
        elif self.port_number_s > 0 or self.port_number_e < 0xFFFF:
            pn = ", port number: %d-%d"%(self.port_number_s,self.port_number_e)
            
        dir = ""
        if self.direction==2:
            dir = ", direction: bidirectional"
        elif self.direction==1:
            dir = ", direction: ingress"
        elif self.direction==0:
            dir = ", direction: egress"
            
        return "dpid: %s, FS: %s%s%s"%(self.dpid,fs_desc,pn,dir)   

#obsolete    
'''
UserOpts, OptsFlowSpace stores information about each opt-in
'''   
'''
class UserOpts(models.Model):
    #Holds information about all opt-ins
    user            = models.ForeignKey(auth.models.User)
    priority        = models.IntegerField()
    experiment      = models.ForeignKey(Experiment)
    nice            = models.BooleanField(default = True)
    
    def __unicode__(self):
        return "user: %s  opted into: %s"%(self.user, self.experiment)
'''   

#obsolete
'''    
class OptsFlowSpace(FlowSpace):
    dpid          = None #models.CharField(max_length = 30)
    direction     = None #models.IntegerField(default = 2)  #0:ingress 1:egress 2:bi-directional
    port_number_s = None #models.IntegerField("Start of Port Range", default = 0)
    port_number_e = None #models.IntegerField("End of Port Range", default=0xFFFF)
    opt           = None #models.ForeignKey(UserOpts)
    def __unicode__(self):
        fs_desc = super(OptsFlowSpace, self).__unicode__()        
        
        pn = ""
        if self.port_number_s == self.port_number_e:
            pn = ", port number: %d"%self.port_number_s
        elif self.port_number_s > 0 or self.port_number_e < 0xFFFF:
            pn = ", port number: %d-%d"%(self.port_number_s,self.port_number_e)
            
        dir = ""
        if self.direction==2:
            dir = ", direction: bidirectional"
        elif self.direction==1:
            dir = ", direction: ingress"
        elif self.direction==0:
            dir = ", direction: egress"
            
        return "dpid: %s, FS: %s%s%s"%(self.dpid,fs_desc,pn,dir) 
'''

#obsolete
'''    
class MatchStruct(models.Model):
    match       = models.CharField(max_length = 2000)
    #TODO unique should be true
    fv_id       = models.CharField(unique = False, max_length = 40)
    priority    = models.IntegerField()
    optfs       = models.ForeignKey(OptsFlowSpace)
    def __unicode__(self):
        return "%s: %s"%(self.fv_id, self.match)
'''

   
