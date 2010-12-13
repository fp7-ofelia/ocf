from expedient.common.tests.manager import SettingsTestCase
from expedient.common.tests.client import test_get_and_post_form
from django.contrib.auth.models import User
from openflow.optin_manager.users.models import UserProfile
from django.core.urlresolvers import reverse
from openflow.optin_manager.admin_manager.models import *
from openflow.optin_manager.opts.models import *
from openflow.optin_manager.flowspace.utils import *
from openflow.optin_manager.xmlrpc_server.models import FVServerProxy

SCHEME = "test"
HOST = "testserver"

class Tests(SettingsTestCase):
    
    def setUp(self):
        # Create a test admin
        self.test_admin = User.objects.create_superuser(
                "admin", "admin@user.com", "password")
        # first set admin to use manual approve:
        logged = self.client.login(username="admin",password="password")
        self.assertEqual(logged,True)
        
        # Create the FV proxy connection
        username = "om"
        password = "password"
        u = User.objects.create(username=username)
        u.set_password(password)
        u.save()
        FVServerProxy.objects.create(
            name="Flowvisor",
            username=username,
            password=password,

            url = SCHEME+"://%s:8443/dummyfv/1/xmlrpc/" % (
                    HOST,
            ),
        )
        
        response = test_get_and_post_form(
            self.client,
            reverse("set_auto_approve"),
            {"script":"Manual"},
        )
        script = AdminAutoApproveScript.objects.filter(admin=self.test_admin)
        self.assertEqual(script.count(),1)
        self.assertEqual(script[0].script_name,"Manual")
        self.client.logout()
        
    def test_request_flowspace(self):
        '''
        A single user and a single admin.
        User send a request. test that admin auto approve and manual approve works.
        '''
        
        u = User.objects.create_user("user", "user@user.com", "password")
        profile = UserProfile.get_or_create_profile(u)
        
        # log in as user
        logged = self.client.login(username="user",password="password")
        self.assertEqual(logged,True)
        
        response = test_get_and_post_form(
            self.client,
            reverse("user_reg_fs"),
            {"ip_addr":"176.25.10.1","mac_addr":"*"},
        )
        rufs = RequestedUserFlowSpace.objects.filter(user=u)
        self.assertEqual(rufs.count(),2)
        self.assertContains(response, "submitted successfully")
        self.assertContains(response, "awaiting approval by")
        
        # now try it with auto approve script
        self.client.logout()
        logged = self.client.login(username="admin",password="password")
        self.assertEqual(logged,True)
        response = test_get_and_post_form(
            self.client,
            reverse("set_auto_approve"),
            {"script":"Approve All Requests"},
        )
        script = AdminAutoApproveScript.objects.filter(admin=self.test_admin)
        self.assertEqual(script.count(),1)
        self.assertEqual(script[0].script_name,"Approve All Requests")
        self.client.logout()
        
        # log in as user
        logged = self.client.login(username="user",password="password")
        self.assertEqual(logged,True)
        
        response = test_get_and_post_form(
            self.client,
            reverse("user_reg_fs"),
            {"ip_addr":"176.26.10.1","mac_addr":"*"},
        )

        ufs = UserFlowSpace.objects.filter(user=u)
        self.assertEqual(ufs.count(),2)
        self.assertContains(response, "submitted successfully")
        self.assertContains(response, "approved by")
        
    def test_multi_admin(self):
        '''
        5 admins in a hierarchial fashion, and one user sending 3 requests, each
        targeted to one admin. verify that they are being sent to correct admin.
        '''
        u1 = User.objects.create_user("admin1", "admin1@admin.com", "password")
        profile1 = UserProfile.get_or_create_profile(u1)

        u2 = User.objects.create_user("admin2", "admin2@admin.com", "password")
        profile2 = UserProfile.get_or_create_profile(u2)
        
        u3 = User.objects.create_user("admin3", "admin3@admin.com", "password")
        profile3 = UserProfile.get_or_create_profile(u3)
        
        u4 = User.objects.create_user("admin4", "admin4@admin.com", "password")
        profile4 = UserProfile.get_or_create_profile(u4)
        
        profile1.is_net_admin = True
        profile1.supervisor = self.test_admin
        profile1.save()
        
        profile2.is_net_admin = True
        profile2.supervisor = self.test_admin
        profile2.save()
        
        profile3.is_net_admin = True
        profile3.supervisor = u1
        profile3.save()
        
        profile4.is_net_admin = True
        profile4.supervisor = u2
        profile4.save()
        
        AdminFlowSpace.objects.create(user=u1,
                            ip_src_s=dotted_ip_to_int("192.0.0.0"),
                            ip_src_e=dotted_ip_to_int("192.255.255.255"))
        AdminFlowSpace.objects.create(user=u1,
                            ip_dst_s=dotted_ip_to_int("192.0.0.0"),
                            ip_dst_e=dotted_ip_to_int("192.255.255.255"))
        AdminFlowSpace.objects.create(user=u2,
                            ip_src_s=dotted_ip_to_int("193.0.0.0"),
                            ip_src_e=dotted_ip_to_int("193.255.255.255"))
        AdminFlowSpace.objects.create(user=u2,
                            ip_dst_s=dotted_ip_to_int("193.0.0.0"),
                            ip_dst_e=dotted_ip_to_int("193.255.255.255"))
        AdminFlowSpace.objects.create(user=u3,
                            ip_src_s=dotted_ip_to_int("192.168.0.0"),
                            ip_src_e=dotted_ip_to_int("192.168.255.255"))
        AdminFlowSpace.objects.create(user=u3,
                            ip_dst_s=dotted_ip_to_int("192.168.0.0"),
                            ip_dst_e=dotted_ip_to_int("192.168.255.255"))
        AdminFlowSpace.objects.create(user=u4,
                            ip_src_s=dotted_ip_to_int("193.168.0.0"),
                            ip_src_e=dotted_ip_to_int("193.168.255.255"))
        AdminFlowSpace.objects.create(user=u4,
                            ip_dst_s=dotted_ip_to_int("193.168.0.0"),
                            ip_dst_e=dotted_ip_to_int("193.168.255.255"))
        
        u = User.objects.create_user("user", "user@user.com", "password")
        profile = UserProfile.get_or_create_profile(u)
        # log in as user
        logged = self.client.login(username="user",password="password")
        self.assertEqual(logged,True)
        
        # this should be assigned to admin1
        response = test_get_and_post_form(
            self.client,
            reverse("user_reg_fs"),
            {"ip_addr":"192.165.10.1","mac_addr":"*"},
        )
        self.assertContains(response, "submitted successfully")
        self.assertContains(response, "(admin1)")
                
        # this should be assigned to admin2
        response = test_get_and_post_form(
            self.client,
            reverse("user_reg_fs"),
            {"ip_addr":"193.122.10.1","mac_addr":"*"},
        )
        self.assertContains(response, "submitted successfully")
        self.assertContains(response, "(admin2)")
        
        # this should be assigned to admin3
        response = test_get_and_post_form(
            self.client,
            reverse("user_reg_fs"),
            {"ip_addr":"192.168.10.1","mac_addr":"*"},
        )
        self.assertContains(response, "submitted successfully")
        self.assertContains(response, "(admin3)")
        
        # this should be assigned to admin4
        response = test_get_and_post_form(
            self.client,
            reverse("user_reg_fs"),
            {"ip_addr":"193.168.10.1","mac_addr":"*"},
        )
        self.assertContains(response, "submitted successfully")
        self.assertContains(response, "(admin4)")
        
        rufs = RequestedUserFlowSpace.objects.filter(user=u,admin=profile1.user)
        self.assertEqual(rufs.count(),2)
        rufs = RequestedUserFlowSpace.objects.filter(user=u,admin=profile2.user)
        self.assertEqual(rufs.count(),2)
        rufs = RequestedUserFlowSpace.objects.filter(user=u,admin=profile3.user)
        self.assertEqual(rufs.count(),2)
        rufs = RequestedUserFlowSpace.objects.filter(user=u,admin=profile4.user)
        self.assertEqual(rufs.count(),2)
        
    def test_one_user_conflict(self):
        '''
        1) User requests one flowspace. then requests a subset of that flowpsace.
        The request should be rejected.
        2) User requests one flowspace. then requests a superset of that flowpsace.
        The previous request should be deleted and replaced by new one
        3) User requests one flowspace. Admin accepts it. then requests a subset of 
        that flowpsace. request should be rejected.
        4) User requests one flowspace. Admin accepts it. then requests a superset of 
        that flowpsace. admin accepts that as well. We should just see the second 
        request in UserFlowSpace.
        '''
        u = User.objects.create_user("user", "user@user.com", "password")
        profile = UserProfile.get_or_create_profile(u)
    
        ### part 1
        logged = self.client.login(username="user",password="password")
        self.assertEqual(logged,True)
        response = test_get_and_post_form(
            self.client,
            reverse("user_reg_fs"),
            {"ip_addr":"192.168.1.10","mac_addr":"*"},
        )
        rufs = RequestedUserFlowSpace.objects.filter(user=u)
        self.assertEqual(rufs.count(),2)
        self.assertContains(response, "submitted successfully")
        self.assertContains(response, "awaiting approval by")
        
        # now request a subset of the first FS:
        response = test_get_and_post_form(
            self.client,
            reverse("user_reg_fs"),
            {"ip_addr":"192.168.1.10","mac_addr":"00:11:22:33:44:55"},
        )
        rufs = RequestedUserFlowSpace.objects.filter(user=u)
        self.assertEqual(rufs.count(),2)
        self.assertContains(response, "already owned")

        RequestedUserFlowSpace.objects.filter(user=u).delete()

        ### part 2
        response = test_get_and_post_form(
            self.client,
            reverse("user_reg_fs"),
            {"ip_addr":"193.168.1.10","mac_addr":"00:11:22:33:44:55"},
        )
        rufs = RequestedUserFlowSpace.objects.filter(user=u)
        self.assertEqual(rufs.count(),2)
        self.assertContains(response, "submitted successfully")
        self.assertContains(response, "awaiting approval by")
        
        response = test_get_and_post_form(
            self.client,
            reverse("user_reg_fs"),
            {"ip_addr":"193.168.1.10","mac_addr":"*"},
        )
        rufs = RequestedUserFlowSpace.objects.filter(user=u)
        self.assertEqual(rufs.count(),2)
        self.assertContains(response, "submitted successfully")
        self.assertContains(response, "awaiting approval by")
        
        RequestedUserFlowSpace.objects.filter(user=u).delete()
        
        #### part 3
        self.client.logout()
        logged = self.client.login(username="admin",password="password")
        self.assertEqual(logged,True)
        response = test_get_and_post_form(
            self.client,
            reverse("set_auto_approve"),
            {"script":"Approve All Requests"},
        )
        script = AdminAutoApproveScript.objects.filter(admin=self.test_admin)
        self.assertEqual(script.count(),1)
        self.assertEqual(script[0].script_name,"Approve All Requests")
        self.client.logout()
        logged = self.client.login(username="user",password="password")
        self.assertEqual(logged,True)
        
        response = test_get_and_post_form(
            self.client,
            reverse("user_reg_fs"),
            {"ip_addr":"192.168.1.10","mac_addr":"*"},
        )

        ufs = UserFlowSpace.objects.filter(user=u)
        self.assertEqual(ufs.count(),2)
        self.assertContains(response, "submitted successfully")
        self.assertContains(response, "approved by")
        
        response = test_get_and_post_form(
            self.client,
            reverse("user_reg_fs"),
            {"ip_addr":"192.168.1.10","mac_addr":"00:11:22:33:44:55"},
        )

        ufs = UserFlowSpace.objects.filter(user=u)
        self.assertEqual(ufs.count(),2)
        self.assertContains(response, "already owned")
        
        UserFlowSpace.objects.filter(user=u).delete()
        
        #### part 4
        response = test_get_and_post_form(
            self.client,
            reverse("user_reg_fs"),
            {"ip_addr":"193.168.1.10","mac_addr":"00:11:22:33:44:55"},
        )
        ufs = UserFlowSpace.objects.filter(user=u)
        self.assertEqual(ufs.count(),2)
        self.assertContains(response, "submitted successfully")
        self.assertContains(response, "approved by")
        
        response = test_get_and_post_form(
            self.client,
            reverse("user_reg_fs"),
            {"ip_addr":"193.168.1.10","mac_addr":"*"},
        )

        ufs = UserFlowSpace.objects.filter(user=u)
        self.assertEqual(ufs.count(),2)
        self.assertContains(response, "submitted successfully")
        self.assertContains(response, "approved by")
        
    def test_multi_user_conflict(self):
        '''
        Create two users and one admin. two users requests two flowspaces that intersect.
        verify these:
        1) Admin gets conflict warning for both requests when in the approve page.
        2) Admin approves one of them. Still should get conflict warning for the other one.
        '''
        u1 = User.objects.create_user("user1", "user1@user.com", "password")
        profile1 = UserProfile.get_or_create_profile(u1)

        u2 = User.objects.create_user("user2", "user2@user.com", "password")
        profile2 = UserProfile.get_or_create_profile(u2)
        
        logged = self.client.login(username="user1",password="password")
        self.assertEqual(logged,True)
        response = test_get_and_post_form(
            self.client,
            reverse("user_reg_fs"),
            {"ip_addr":"192.168.1.10","mac_addr":"*"},
        )
        rufs = RequestedUserFlowSpace.objects.filter(user=u1)
        self.assertEqual(rufs.count(),2)
        self.assertContains(response, "submitted successfully")
        self.assertContains(response, "awaiting approval by")
        
        self.client.logout()
        
        logged = self.client.login(username="user2",password="password")
        self.assertEqual(logged,True)
        response = test_get_and_post_form(
            self.client,
            reverse("user_reg_fs"),
            {"ip_addr":"192.168.1.10","mac_addr":"*"},
        )
        rufs = RequestedUserFlowSpace.objects.filter(user=u2)
        self.assertEqual(rufs.count(),2)
        self.assertContains(response, "submitted successfully")
        self.assertContains(response, "awaiting approval by")
        
        self.client.logout()
        
        logged = self.client.login(username="admin",password="password")
        self.assertEqual(logged,True)
        response = test_get_and_post_form(
            self.client,
            reverse("approve_user_reg"),
            {"req_1":"none"},
        )
        self.assertContains(response,"Conflict with   (username: user1)")
        self.assertContains(response,"Conflict with   (username: user2)")
        response = test_get_and_post_form(
            self.client,
            reverse("approve_user_reg"),
            {"req_1":"accept","req_2":"accept"},
        )
        self.assertContains(response,"Conflict with   (username: user1)")
        self.assertNotContains(response, "Conflict with   (username: user2)")
        self.assertNotContains(response,"req_1")
        self.assertNotContains(response,"req_2")
        
        