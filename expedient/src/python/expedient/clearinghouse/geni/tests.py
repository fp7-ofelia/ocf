'''
Created on Oct 8, 2010

@author: jnaous
'''
from expedient.common.tests.manager import SettingsTestCase
from django.core.urlresolvers import reverse
from django.conf import settings
import os
from expedient.clearinghouse.geni.utils import get_user_cert_fname, get_user_key_fname
from django.contrib.auth.models import User
from expedient.common.tests.client import test_get_and_post_form

def try_unlink(fname):
    try:
        os.unlink(fname)
    except OSError as e:
        if "No such file" not in str(e):
            raise

class Tests(SettingsTestCase):
    
    def setUp(self):
        self.u = User.objects.create_user(
            "test_user", "email@email.com", "password")
        
        self.cert_fname = get_user_cert_fname(self.u)
        self.key_fname = get_user_key_fname(self.u)
        
        try_unlink(self.cert_fname)
        try_unlink(self.key_fname)
    
    def test_login_redirect(self):
        """Check that a user who is not logged in get redirected with no cert created."""
        
        response = self.client.get(reverse("home"))
        expected_url = settings.LOGIN_URL \
            + '?next=%s' % reverse("home")
        self.assertRedirects(
            response,
            expected_url,
        )
        
        self.assertFalse(
            os.access(self.cert_fname, os.F_OK))
        self.assertFalse(
            os.access(self.key_fname, os.F_OK))
        
    def test_login(self):
        """Check that users can login and get a cert created for them."""
        response = test_get_and_post_form(
            self.client,
            settings.LOGIN_URL,
            {"username": "test_user", "password": "password"},
        )
        expected_url = reverse("home")
        self.assertRedirects(
            response,
            expected_url,
        )
        
        self.assertTrue(
            os.access(self.cert_fname, os.F_OK))
        self.assertTrue(
            os.access(self.key_fname, os.F_OK))
        
    def tearDown(self):
        try_unlink(self.cert_fname)
        try_unlink(self.key_fname)
        
