
from django.conf import settings
from expedient.common.tests.manager import SettingsTestCase
from django.core.urlresolvers import reverse
import logging
from django.contrib.auth.models import User
from openflow.optin_manager.opts.models import UserFlowSpace,\
        Experiment,ExperimentFLowSpace, UserOpts, OptsFlowSpace
import random
from openflow.optin_manager.xmlrpc_server.ch_api import om_ch_translate
from expedient.common.tests.client import Browser, test_get_and_post_form
from openflow.optin_manager.users.models import UserProfile
from openflow.optin_manager.dummyfv.models import DummyFV
from openflow.optin_manager.xmlrpc_server.models import FVServerProxy
logger = logging.getLogger("OMOptsTest")

SCHEME = "test"
HOST = "testserver"
USE_RANDOM = False

class Tests(SettingsTestCase):
    
    def setUp(self):
        # Create a test user
        self.test_user = User.objects.create_user(
                "user", "user@user.com", "password")
        profile = UserProfile.get_or_create_profile(self.test_user)

        # Create a test admin
        self.test_admin = User.objects.create_superuser(
                "admin", "admin@user.com", "password")
        
        # Assign a flowpsace to uer
        self.user_ip_src_s = random.randint(0,0x80000000) & 0xFFFF0000
        self.user_ip_src_e = random.randint(0x80000000,0xFFFFFFFF) & 0xFFFF0000
    
        # Assign a flowpsace to experiment
        self.exp_ip_src_s = random.randint(0,0x80000000) & 0xFFFF0000
        self.exp_ip_src_e = random.randint(0x80000000,0xFFFFFFFF) & 0xFFFF0000
        
        # Choose a random field
        fields=["dl_src","dl_dst","vlan_id","tp_src","tp_dst"]
        random.shuffle(fields)
        (to_str,from_str,width,om_name,of_name) = om_ch_translate.attr_funcs[fields[0]]
        self.user_field_name = om_name
        self.user_field_s = random.randint(0,2**width-3)
        self.user_field_e = self.user_field_s + 1
        (to_str,from_str,width,om_name,of_name) = om_ch_translate.attr_funcs[fields[1]]
        self.exp_field_name = om_name
        self.exp_field_s = random.randint(0,2**width-3)
        self.exp_field_e = self.exp_field_s + 1 
              
        #save flowspace for user
        ufs = UserFlowSpace(user=self.test_user, ip_src_s=self.user_ip_src_s,
                             ip_src_e=self.user_ip_src_e,approver=self.test_admin)
        setattr(ufs,"%s_s"%self.user_field_name,self.user_field_s)
        setattr(ufs,"%s_e"%self.user_field_name,self.user_field_e)
        ufs.save()     
    
        #create an experiment and assign a flowspace to it
        exp = Experiment.objects.create(slice_id="slice_id", project_name="project name",
                                  project_desc="project description", slice_name="slice name",
                                  slice_desc="slice description", controller_url="controller url",
                                  owner_email="owner email", owner_password="owner password") 
        expfs = ExperimentFLowSpace.objects.create(exp=exp, dpid="00:00:00:00:00:00:01",
                            ip_src_s=self.exp_ip_src_s, 
                            ip_src_e=self.exp_ip_src_e, 
                             )
        setattr(expfs,"%s_s"%self.exp_field_name,self.exp_field_s)
        setattr(expfs,"%s_e"%self.exp_field_name,self.exp_field_e)
        expfs.save()     

        # Create dummy FV
        fv = DummyFV.objects.create()
        # Load up a fake topology in the Dummy FV
        fv.populateTopology(10, 20, use_random=USE_RANDOM)
            
        # create fake users for the Dummy FV
        username = "om"
        password = "password"
        u = User.objects.create(username=username)
        u.set_password(password)
        u.save()

        # Create the FV proxy connection
        FVServerProxy.objects.create(
            name="Flowvisor",
            username=username,
            password=password,

            url = SCHEME+"://%s:8443/dummyfv/1/xmlrpc/" % (
                    HOST,
            ),
        )
            
        #Login
        logged = self.client.login(username="user",password="password")
        self.assertEqual(logged,True)
        
    def test_optin(self):
        response = test_get_and_post_form(
            self.client,
            reverse("opt_in_experiment"),
            {"experiment":1},
        )
        self.assertContains(response, "successfully")
        uopt = UserOpts.objects.filter(user__username__exact="user")
        self.assertEqual(len(uopt),1)
        self.assertEqual(uopt[0].experiment.slice_name,"slice name")
        optfs = OptsFlowSpace.objects.filter(opt=uopt[0])
        self.assertEqual(len(optfs),1)
        self.assertEqual(optfs[0].ip_src_s,max(self.user_ip_src_s,self.exp_ip_src_s))
        self.assertEqual(optfs[0].ip_src_e,min(self.user_ip_src_e,self.exp_ip_src_e))
        self.assertEqual(getattr(optfs[0],"%s_s"%self.user_field_name), self.user_field_s)
        self.assertEqual(getattr(optfs[0],"%s_e"%self.user_field_name), self.user_field_e)
        self.assertEqual(getattr(optfs[0],"%s_s"%self.exp_field_name), self.exp_field_s)
        self.assertEqual(getattr(optfs[0],"%s_e"%self.exp_field_name), self.exp_field_e)     
        
    def test_optout(self):
        response = test_get_and_post_form(
            self.client,
            reverse("opt_out_of_experiment"),
            {"1":"checked"},
        )
        uopt = UserOpts.objects.filter(user__username__exact="user")
        self.assertEqual(len(uopt),0)
        optfs = OptsFlowSpace.objects.filter(opt__user__username="user")
        self.assertEqual(optfs.count(),0) 
        
