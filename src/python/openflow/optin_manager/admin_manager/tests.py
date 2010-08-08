from expedient.common.tests.manager import SettingsTestCase
from expedient.common.tests.client import test_get_and_post_form
from django.contrib.auth.models import User
from openflow.optin_manager.users.models import UserProfile
from django.core.urlresolvers import reverse

SCHEME = "test"
HOST = "testserver"

class Tests(SettingsTestCase):
    
    def setUp(self):
        # Create a test admin
        self.test_admin = User.objects.create_superuser(
                "admin", "admin@user.com", "password")
        
    def test_request_flowspace(self):
        '''
        A single user and a single admin.
        User send a request. test that admin auto approve and manual approve works.
        '''
        
    
    def test_multi_admin(self):
        '''
        5 admins in a hierarchial fashion, and one user sending 3 requests, each
        targeted to one admin. verify that they are being sent to correct admin.
        '''
        
        
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
        
    def test_multi_user_conflict(self):
        '''
        Create two users and one admin. two users requests two flowspaces that intersect.
        verify these:
        1) Admin gets conflict warning for both requests when in the approve page.
        2) Admin approves one of them. Still should get conflict warning for the other one.
        '''
        