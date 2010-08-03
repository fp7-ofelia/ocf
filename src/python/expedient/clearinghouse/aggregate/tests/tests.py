'''
Created on Jun 11, 2010

@author: jnaous
'''

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from expedient.common.tests.manager import SettingsTestCase
from expedient.clearinghouse.aggregate.tests.models import DummyAggregate
from expedient.common.middleware import threadlocals
from expedient.common.permissions.shortcuts import give_permission_to
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.common.permissions.exceptions import PermissionDenied

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
        self.u = u
        d = threadlocals.get_thread_locals()
        d["user"] = u
        self.client.login(username="test", password="password")
        
    def test_disallowed_create(self):
        """
        Test that we cannot create an aggregate without permission.
        """
        response = self.client.post(
            reverse("tests_aggregate_create"),
            data=dict(
                name="dummy agg",
                description="aggregate description",
                location="Stanford, CA",
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue("/permissions/can_add_aggregate/" in response["location"])
        
    def test_allowed_create(self):
        """
        Test that we can create an aggregate.
        """
        give_permission_to("can_add_aggregate", Aggregate, self.u)
        response = self.client.post(
            reverse("tests_aggregate_create"),
            data=dict(
                name="dummy agg",
                description="aggregate description",
                location="Stanford, CA",
            )
        )
        self.assertRedirects(response, "/",
                             msg_prefix="response was %s" % response)
        self.assertEqual(DummyAggregate.objects.all().count(), 1)
        
    def test_disallowed_edit(self):
        """
        Test that we cannot edit or delete without permission.
        """
        give_permission_to("can_add_aggregate", Aggregate, self.u)
        agg = DummyAggregate.objects.create(
            name="dummy agg",
            owner=self.u,
            description="aggregate description",
            location="Stanford, CA",
        )
        self.assertRaises(PermissionDenied, agg.save)
        self.assertRaises(PermissionDenied, agg.delete)
        
    def test_allowed_edit(self):
        """
        Tests that we can edit an existing aggregate.
        """
        give_permission_to("can_add_aggregate", Aggregate, self.u)
        agg = DummyAggregate.objects.create(
            name="dummy agg",
            owner=self.u,
            description="aggregate description",
            location="Stanford, CA",
        )
        give_permission_to("can_edit_aggregate", agg, self.u)
        response = self.client.post(
            reverse("tests_aggregate_edit", kwargs={"agg_id": 1}),
            data=dict(
                name="Edited dummy agg",
                description="Edited aggregate description",
                location="Stanford, CA",
            )
        )
        self.assertRedirects(response, "/",
                             msg_prefix="response was %s" % response)
        