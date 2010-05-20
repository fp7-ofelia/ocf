from openflow.optin_manager.users.models import UserProfile
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from models import *
from openflow.optin_manager.xmlrpc_server.models import FVServerProxy
from openflow.optin_manager.xmlrpc_server.ch_api import delete_slice, create_slice

def config():
    Site.objects.all().delete()
    UserProfile.objects.all().delete()
    FVServerProxy.objects.all().delete()
    
    fv = FVServerProxy(name="fv",url="example.com",username="peyman")
    fv.save()
        
    s = Site(domain="127:0.0.1:8000", name="om.egeni.com")
    s.save()
    
    u = User.objects.get(pk=1)
    p = UserProfile.get_or_create_profile(u)
    p.is_net_admin = True
    p.supervisor = u
    p.priority = 7000
    p.save()
    
    o = User(username="user", password="user")
    o.set_password("user")
    o.save()
    po = UserProfile.get_or_create_profile(o)
    po.is_net_admin = False
    po.supervisor = u
    po.prioirty = 2000
    po.save()
    
    return 0

def setup():
    Experiment.objects.all().delete()
    UserOpts.objects.all().delete()
    ExperimentFLowSpace.objects.all().delete()
    OptsFlowSpace.objects.all().delete()
    AdminFlowSpace.objects.all().delete()
    UserFlowSpace.objects.all().delete()
    MatchStruct.objects.all()

    
    e1 = Experiment(slice_id = '1', project_name="Cool Project", slice_name="security app",
                   controller_url="controller.com:6633")
    e1.save()
    
    e2 = Experiment(slice_id = '2', project_name="Cool Project", slice_name="load balancer app",
                   controller_url="controller.com:6633")
    e2.save()
    
    efs1 = ExperimentFLowSpace(ip_src_s=0x55667788, ip_src_e=0x88000012, exp=e1,
                               dpid = '01' )
    efs1.save()
    efs1 = ExperimentFLowSpace(ip_src_s=0x55667788, ip_src_e=0x88000012, exp=e1,
                               dpid = '02' )
    efs1.save()

    efs2 = ExperimentFLowSpace(ip_src_s=0x25, ip_src_e=0x56, exp=e2,
                               dpid = '01')
    efs2.save()
    efs2 = ExperimentFLowSpace(ip_src_s=0x25, ip_src_e=0x56, exp=e2,
                               dpid = '02')
    efs2.save()
    
   
    u = User.objects.get(pk=1)
    ufs = AdminFlowSpace(user=u)
    ufs.save()
    
    u = User.objects.get(pk=2)
    ufs = UserFlowSpace(ip_src_s=0x66777766, ip_src_e=0x77000000, user=u)
    ufs.save()
#    op = UserOpts(user=u, experiment=e1, priority=500, nice=True,)
#    op.save()
#    ofs1 = OptsFlowSpace(fv_entry_id = 1, opt=op, ip_src_s=0x55667788, ip_src_e=0x88000011)
#    ofs1.save()
#    
#    op = UserOpts(user=u, experiment=e2, priority=1800, nice=False,)
#    op.save()
#    ofs1 = OptsFlowSpace(fv_entry_id = 2, opt=op, ip_src_s=0x44, ip_src_e=0x53)
#    ofs1.save()
    
    return 0

def createslice():
    args = [{"datapath_id":"00:00:00:00:00:11:11", 
             "flowspace":[{"nw_src_start":"192.168.0.0","nw_src_end":"192.168.255.255"}]
             }]
    create_slice("123","test project","just a simpe test","test slice",
                 "just a test slice","controller.com","owner@geni.com","password",args)

def deleteslice():
    delete_slice("123")