import sys
from os.path import dirname, join
SRC_DIR = join(dirname(__file__), '../../../')
sys.path.append(SRC_DIR)

from unittest import TestCase
from expedient.common.tests.commands import call_env_command, Env
from openflow.tests import test_settings
from expedient.common.tests.utils import wrap_xmlrpc_call
import xmlrpclib
import random
from pprint import pprint
import logging

logger = logging.getLogger("manual_test")

SCHEME = "https" if test_settings.USE_HTTPS else "http"

class ManualTests(TestCase):
    
    def setUp(self):
        """
        Load up a DB for the OM.
        Create a client to talk to the OM.
        """
        
        
        call_env_command(test_settings.OM_PROJECT_DIR, "flush",
                         interactive=False)
        self.om_env = Env(test_settings.OM_PROJECT_DIR)
        self.om_env.switch_to()
        
        from openflow.optin_manager.dummyfv.models import DummyFV
        from openflow.optin_manager.xmlrpc_server.models import FVServerProxy
        from openflow.optin_manager.users.models import UserProfile
        from django.contrib.auth.models import User 

        # Create the clearinghouse user
        username = "clearinghouse"
        password = "password"
        u = User.objects.create(username=username)
        u.set_password(password)
        u.save()
        
        profile = UserProfile.get_or_create_profile(u) 
        profile.is_clearinghouse_user = True
        profile.save()
        self.om_client = xmlrpclib.ServerProxy(
            SCHEME + "://%s:%s@%s:%s/xmlrpc/xmlrpc/" % (
                username, password, test_settings.HOST, test_settings.OM_PORT
            )
        )
        
        #creat admin user: use this to look at DBs through admin interface
        username = "admin"
        password = "password"
        u = User.objects.create(username=username, is_superuser=True,
                                is_staff=True, is_active=True)
        u.set_password(password)
        u.save()
        profile = UserProfile.get_or_create_profile(u) 
        profile.is_net_admin = True
        profile.supervisor = u
        profile.max_priority_level = 7000
        profile.save()      
         
         
        # Create dummy FVs
        for i in range(test_settings.NUM_DUMMY_FVS):
            fv = DummyFV.objects.create()
            # Load up a fake topology in the Dummy FV
            fv.populateTopology(10, 20, use_random=test_settings.USE_RANDOM)
            
            # create fake users for the Dummy FV
            username = "om%s" % i
            password = "password"
            u = User.objects.create(username=username)
            u.set_password(password)
            u.save()

            # Create the FV proxy connection
            FVServerProxy.objects.create(
                name="Flowvisor %s" % i,
                username=username,
                password=password,
                url = SCHEME+"://%s:%s/dummyfv/%s/xmlrpc/" % (
                    test_settings.HOST, test_settings.OM_PORT, fv.id,
                ),
            )
            
    def test_case1(self):
        from django.contrib.auth.models import User
        from openflow.optin_manager.opts.models import UserFlowSpace,Experiment, ExperimentFLowSpace

        # create a second experiemnt        
        username = "user"
        password = "password"
        u = User.objects.create(username=username, is_active=True)
        u.set_password(password)
        u.save()
        self.user_ip_src_s = random.randint(0,0x80000000) & 0xFFFF0000
        self.user_ip_src_e = random.randint(0x80000000,0xFFFFFFFF) & 0xFFFF0000
        #assign flowspace to user
        adm = User.objects.get(username="admin")
        ufs = UserFlowSpace(user=u, ip_src_s=self.user_ip_src_s,
                             ip_src_e=self.user_ip_src_e,approver=adm)
        ufs.save()
        
        Experiment.objects.all().delete()
        ExperimentFLowSpace.objects.all().delete()
        
        exp = Experiment.objects.create(slice_id="first_id", project_name="first_project",
                                  project_desc="project description", slice_name="first slice",
                                  slice_desc="slice description", controller_url="http://controller.com",
                                  owner_email="owner email", owner_password="owner password") 
        expfs = ExperimentFLowSpace.objects.create(exp=exp, dpid="00:00:00:00:00:00:01",
                            ip_src_s=0x05866000, 
                            ip_src_e=0xa0000000, 
                             )  
        
        exp = Experiment.objects.create(slice_id="second_id", project_name="second_project",
                                  project_desc="project description", slice_name="second slice",
                                  slice_desc="slice description", controller_url="http://controller.com",
                                  owner_email="owner email", owner_password="owner password") 
        expfs = ExperimentFLowSpace.objects.create(exp=exp, dpid="00:00:00:00:00:00:02",
                            ip_src_s=0x00123456, 
                            ip_src_e=0x90123456, 
                             )  
        
        exp = Experiment.objects.create(slice_id="third_id", project_name="third_project",
                                  project_desc="project description", slice_name="third slice",
                                  slice_desc="slice description", controller_url="http://controller.com",
                                  owner_email="owner email", owner_password="owner password") 
        expfs = ExperimentFLowSpace.objects.create(exp=exp, dpid="00:00:00:00:00:00:03",
                            ip_src_s=0x00333456, 
                            ip_src_e=0x95123456, 
                             ) 
        
        
    def test_case2(self):
        from django.contrib.auth.models import User
        from openflow.optin_manager.opts.models import UserFlowSpace,Experiment, ExperimentFLowSpace

        # create a second experiemnt        
        username = "user"
        password = "password"
        u = User.objects.create(username=username, is_active=True)
        u.set_password(password)
        u.save()

        adm = User.objects.get(username="admin")

        # create a second experiemnt        
        username = "user2"
        password = "password"
        u = User.objects.create(username=username, is_active=True)
        u.set_password(password)
        u.save()

        
        Experiment.objects.all().delete()
        ExperimentFLowSpace.objects.all().delete()
        
        exp = Experiment.objects.create(slice_id="first_id", project_name="first_project",
                                  project_desc="project description", slice_name="first slice",
                                  slice_desc="slice description", controller_url="http://controller.com",
                                  owner_email="owner email", owner_password="owner password") 
        expfs = ExperimentFLowSpace.objects.create(exp=exp, dpid="00:00:00:00:00:00:01",
                            ip_src_s=0x05866000, 
                            ip_src_e=0xa0000000, 
                             )  
        
        exp = Experiment.objects.create(slice_id="second_id", project_name="second_project",
                                  project_desc="project description", slice_name="second slice",
                                  slice_desc="slice description", controller_url="http://controller.com",
                                  owner_email="owner email", owner_password="owner password") 
        expfs = ExperimentFLowSpace.objects.create(exp=exp, dpid="00:00:00:00:00:00:02",
                            ip_src_s=0x00123456, 
                            ip_src_e=0x90123456, 
                             )  
        
        exp = Experiment.objects.create(slice_id="third_id", project_name="third_project",
                                  project_desc="project description", slice_name="third slice",
                                  slice_desc="slice description", controller_url="http://controller.com",
                                  owner_email="owner email", owner_password="owner password") 
        expfs = ExperimentFLowSpace.objects.create(exp=exp, dpid="00:00:00:00:00:00:03",
                            ip_src_s=0x00333456, 
                            ip_src_e=0x95123456, 
                             ) 

if __name__ == '__main__':
    import unittest
    unittest.main()
