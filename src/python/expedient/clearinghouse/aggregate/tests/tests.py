'''
Created on Jun 11, 2010

@author: jnaous
'''

from django.conf import settings
from expedient.common.tests.manager import SettingsTestCase
from django.core.urlresolvers import reverse
from expedient.clearinghouse.aggregate.tests.models import DummyAggregate
from django.contrib.auth.models import User

MOD = "expedient.clearinghouse.aggregate"

class Tests(SettingsTestCase):
    urls = MOD + ".tests.urls"
    
    def setUp(self):
        # Add the test application
        self.settings_manager.set(
            INSTALLED_APPS=settings.INSTALLED_APPS + [MOD + ".tests"],
            DEBUG_PROPAGATE_EXCEPTIONS=True,
        )
        u = User(username="test")
        u.set_password("password")
        u.save()
        self.client.login(username="test", password="password")
        
    def test_create(self):
        """
        Test that we can create an aggregate.
        """
        response = self.client.post(
            reverse("tests_aggregate_create"),
            data=dict(
                name="dummy agg",
                description="aggregate description",
                location="Stanford, CA",
            )
        )
        self.assertRedirects(response, "/")
        self.assertEqual(DummyAggregate.objects.all().count(), 1)
        
    def test_edit(self):
        """
        Tests that we can edit an existing aggregate.
        """
        DummyAggregate.objects.create(
            name="dummy agg",
            description="aggregate description",
            location="Stanford, CA",
        )
        response = self.client.post(
            reverse("tests_aggregate_edit", kwargs={"agg_id": 1}),
            data=dict(
                name="Edited dummy agg",
                description="Edited aggregate description",
                location="Stanford, CA",
            )
        )
        self.assertRedirects(response, "/")
        