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
        response = test_get_and_post_form(
            self.client,
            reverse("opt_in_experiment"),
            {"experiment":1},
        ) 