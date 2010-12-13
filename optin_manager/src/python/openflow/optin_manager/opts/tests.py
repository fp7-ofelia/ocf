
from django.conf import settings
from expedient.common.tests.manager import SettingsTestCase
from django.core.urlresolvers import reverse
import logging
from django.contrib.auth.models import User
from openflow.optin_manager.opts.models import UserFlowSpace,\
        Experiment,ExperimentFLowSpace, UserOpts, OptsFlowSpace, MatchStruct
import random
from openflow.optin_manager.xmlrpc_server.ch_api import om_ch_translate
from expedient.common.tests.client import Browser, test_get_and_post_form
from openflow.optin_manager.users.models import UserProfile, Priority
from openflow.optin_manager.dummyfv.models import DummyFV, DummyFVRule
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
        exp = Experiment.objects.create(slice_id="slice_id_1", project_name="project name_1",
                                  project_desc="project description", slice_name="slice name_1",
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

            url = SCHEME+"://%s:8443/dummyfv/%d/xmlrpc/" % (
                    HOST,fv.id,
            ),
        )
            
        #Login
        logged = self.client.login(username="user",password="password")
        self.assertEqual(logged,True)
        
    def test_user_optin(self):
        '''
        Test if a single opt-in is happening correctly
        '''
        all_exps = Experiment.objects.all()
        self.assertEqual(all_exps.count(),1)
        
        response = test_get_and_post_form(
            self.client,
            reverse("opt_in_experiment"),
            {"experiment":all_exps[0].id},
        )
        self.assertContains(response, "successfully")
        uopt = UserOpts.objects.filter(user__username__exact="user")
        self.assertEqual(len(uopt),1)
        self.assertEqual(uopt[0].experiment.slice_name,"slice name_1")
        optfs = OptsFlowSpace.objects.filter(opt=uopt[0])
        self.assertEqual(len(optfs),1)
        self.num_fv_rules = MatchStruct.objects.filter(optfs=optfs[0]).count()
        actual_fv_rules_count = DummyFVRule.objects.all().count()
        self.assertEqual(actual_fv_rules_count,self.num_fv_rules)
        self.assertEqual(optfs[0].ip_src_s,max(self.user_ip_src_s,self.exp_ip_src_s))
        self.assertEqual(optfs[0].ip_src_e,min(self.user_ip_src_e,self.exp_ip_src_e))
        self.assertEqual(getattr(optfs[0],"%s_s"%self.user_field_name), self.user_field_s)
        self.assertEqual(getattr(optfs[0],"%s_e"%self.user_field_name), self.user_field_e)
        self.assertEqual(getattr(optfs[0],"%s_s"%self.exp_field_name), self.exp_field_s)
        self.assertEqual(getattr(optfs[0],"%s_e"%self.exp_field_name), self.exp_field_e)     
     
    def test_user_optin_invalid(self):
        '''
        Test if a single opt-in is happening correctly
        '''
        #opt into an experiemnt that doesn't
        response = test_get_and_post_form(
            self.client,
            reverse("opt_in_experiment"),
            {"experiment":234},
        )
        self.assertNotContains(response, "successfully")
        uopt = UserOpts.objects.filter(user__username__exact="user")
        self.assertEqual(len(uopt),0)
        actual_fv_rules_count = DummyFVRule.objects.all().count()
        self.assertEqual(actual_fv_rules_count,0)
        
    def test_user_optin_invalid_fv(self):
        fv_server_proxy = FVServerProxy.objects.all()[0]
        fv_server_proxy.username = "wrong_username"
        fv_server_proxy.save()
        all_exps = Experiment.objects.all()
        self.assertEqual(all_exps.count(),1)
        
        response = test_get_and_post_form(
            self.client,
            reverse("opt_in_experiment"),
            {"experiment":all_exps[0].id},
        )
        print response
        self.assertNotContains(response, "successfully")
        uopt = UserOpts.objects.filter(user__username__exact="user")
        self.assertEqual(len(uopt),0)
        
    def test_user_re_optin(self):
        '''
        Test if opting into the same experiment just updates the previous opt and
        doesn't double opt
        '''
        self.test_user_optin()
            
        all_exps = Experiment.objects.all()
        self.assertEqual(all_exps.count(),1)
            
        uopt = UserOpts.objects.filter(user__username__exact="user")
        optfs = OptsFlowSpace.objects.filter(opt=uopt[0])
        self.assertEqual(len(optfs),1)
        response = test_get_and_post_form(
            self.client,
            reverse("opt_in_experiment"),
            {"experiment":all_exps[0].id},
        )  
        self.assertContains(response, "successfully")
        uopt = UserOpts.objects.filter(user__username__exact="user")
        self.assertEqual(len(uopt),1)
        optfs = OptsFlowSpace.objects.filter(opt=uopt[0])
        self.assertEqual(len(optfs),1)
        actual_fv_rules_count = DummyFVRule.objects.all().count()
        self.assertEqual(self.num_fv_rules,actual_fv_rules_count)
        
    def test_optout(self):
        self.test_user_optin()

        uopt = UserOpts.objects.filter(user__username__exact="user")
        optfs = OptsFlowSpace.objects.filter(opt=uopt[0])
        self.assertEqual(len(optfs),1)
        response = test_get_and_post_form(
            self.client,
            reverse("opt_out_of_experiment"),
            {"1":"checked"},
        )
        uopt = UserOpts.objects.filter(user__username__exact="user")
        self.assertEqual(len(uopt),0)
        optfs = OptsFlowSpace.objects.filter(opt__user__username="user")
        self.assertEqual(optfs.count(),0) 
        
        
    def test_user_multiple_opts(self):
        '''
        Opt into multiple experiments,change their priorities and then opt all out.
        at each of the three steps, test internal database to make sure that it is done
        correctly.
        '''
        max_opt = random.randint(5,9)
        
        exp_ids = []
        first_id = Experiment.objects.all()[0].id
        exp_ids.append(first_id)
        
        for index in range(2,max_opt):
        #create a random number of experiments
            exp = Experiment.objects.create(slice_id="slice_id_%d"%index, project_name="project name_%d"%index,
                                      project_desc="project description", slice_name="slice name_%d"%index,
                                      slice_desc="slice description", controller_url="controller url",
                                      owner_email="owner email", owner_password="owner password") 
            expfs = ExperimentFLowSpace.objects.create(exp=exp, dpid="00:00:00:00:00:00:0%d"%index,
                                ip_src_s=random.randint(0,0x80000000) & 0xFFFF0000, 
                                ip_src_e=random.randint(0x80000000,0xFFFFFFFF) & 0xFFFF0000, 
                                 )
            expfs.save() 
            exp_ids.append(exp.id)
        
        # opt into all of them
        count = 0
        for exp in Experiment.objects.all():
            count = count + 1
            response = test_get_and_post_form(
                self.client,
                reverse("opt_in_experiment"),
                {"experiment":exp.id},
            )
            self.assertContains(response, "successfully")
            uopt = UserOpts.objects.filter(user__username__exact="user")
            self.assertEqual(len(uopt),count)
            self.assertEqual(uopt[count-1].experiment.slice_name,exp.slice_name)
            optfs = OptsFlowSpace.objects.filter(opt=uopt[count-1])
            self.assertEqual(len(optfs),1)
            
            
        # change priority
        request_post = {}
        for id in range(1,max_opt):
            request_post["p_%d"%exp_ids[id-1]] = max_opt - id + 1
            
        response = test_get_and_post_form(
            self.client,
            reverse("change_priority"),
            request_post,
        )
        self.assertContains(response, "Successfully")
        for id in range(1,max_opt):
            uopt = UserOpts.objects.filter(user__username__exact="user",\
                                    experiment__slice_name="slice name_%d"%id)
            self.assertEqual(uopt.count(),1,"uopt.count()!=1 for id=%d"%id)
            self.assertEqual(uopt[0].priority,max_opt - id + 1)
            optfs = OptsFlowSpace.objects.filter(opt = uopt[0])
            self.assertEqual(optfs.count(),1)
            mstr = optfs[0].matchstruct_set.all()
            self.assertNotEqual(mstr.count(),0)
            fv_rule = DummyFVRule.objects.filter(match=mstr[0].match,\
                                                 dpid="00:00:00:00:00:00:0%d"%id)
            self.assertEqual(fv_rule.count(),1)
            self.assertEqual(fv_rule[0].priority,mstr[0].priority)
            
            
        #opt out of all of them
        request_post = {}
        for id in range(1,max_opt):
            request_post["%d"%exp_ids[id-1]] = "checked"
            
        response = test_get_and_post_form(
            self.client,
            reverse("opt_out_of_experiment"),
            request_post,
        )
        uopt = UserOpts.objects.filter(user__username__exact="user")
        self.assertEqual(len(uopt),0)
        optfs = OptsFlowSpace.objects.filter(opt__user__username="user")
        self.assertEqual(optfs.count(),0) 
        actual_fv_rules_count = DummyFVRule.objects.all().count()
        self.assertEqual(actual_fv_rules_count,0)
        

        
