'''
Created on May 20, 2010

@author: jnaous
'''
from unittest import TestCase
from openflow.tests import test_settings as settings, test_settings
from expedient.common.tests.commands import call_env_command, Env
from django.core.urlresolvers import reverse
from expedient.common.tests.client import login

class LoggedInTests(TestCase):
    def setUp(self):
        """
        Flush the CH DB.
        Create User and login.
        """
        call_env_command(settings.CH_PROJECT_DIR, "flush", interactive=False)
        self.ch_env = Env(settings.CH_PROJECT_DIR)
        self.ch_env.switch_to()
        
        from django.contrib.auth.models import User
        u = User.objects.create_user("testuser", "email@email.com", "password")
        login_url = "https://%s:%s%s" % (
            test_settings.HOST,
            test_settings.CH_PORT,
            reverse("auth_login"),
        )
        
        self.assertTrue(login(login_url, u.username, "password"))
        
    def test_add_aggregate(self):
        """
        Add aggregate.
        """
        pass

if __name__ == '__main__':
    import unittest
    unittest.main()
  
