'''
Created on Jun 11, 2010

@author: jnaous
'''

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from expedient.common.tests.manager import SettingsTestCase
from expedient.clearinghouse.aggregate.tests.models import DummyAggregate,\
    DummyResource, DummySliceEvent
from expedient.common.middleware import threadlocals
from expedient.common.permissions.shortcuts import give_permission_to
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.common.permissions.exceptions import PermissionDenied
from expedient.common.tests.client import test_get_and_post_form
from expedient.clearinghouse.resources.models import Sliver
from expedient.clearinghouse.utils import start_test_slice,\
    add_dummy_agg_to_test_settings

class Tests(SettingsTestCase):
    def setUp(self):
        # Add the test application
        add_dummy_agg_to_test_settings(self)
        
        u = User(username="test")
        u.set_password("password")
        u.save()
        self.u = u
        self.su = User.objects.create_superuser(
            "superuser", "su@su.su", "password")
        threadlocals.push_frame(user=u)
        self.client.login(username="test", password="password")
        
    def tearDown(self):
        threadlocals.pop_frame()
        
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
        threadlocals.push_frame(user=self.su)
        agg = DummyAggregate.objects.create(
            name="dummy agg",
            description="aggregate description",
            location="Stanford, CA",
        )
        threadlocals.pop_frame()
        
        self.assertRaises(PermissionDenied, agg.save)
        self.assertRaises(PermissionDenied, agg.delete)
        
        # Try delete using a post
        response = test_get_and_post_form(
            client=self.client,
            url=agg.get_delete_url(next="/"),
            params={},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue("/permissions/can_edit_aggregate/" in response["location"])

    def test_allowed_delete(self):
        """
        Tests that delete works when given permission.
        """
        give_permission_to("can_add_aggregate", Aggregate, self.u)
        agg = DummyAggregate.objects.create(
            name="dummy agg",
            description="aggregate description",
            location="Stanford, CA",
        )
        response = test_get_and_post_form(
            client=self.client,
            url=agg.get_delete_url(next="/"),
            params={},
        )
        self.assertRedirects(response, "/")
        
    def test_allowed_delete_with_started_slice(self):
        '''
        Tests that we can delete an aggregate that is in a started slice.
        '''
        
        start_test_slice(self)
        
        self.client.login(username=self.u1.username, password="password")
        threadlocals.push_frame(user=self.u1)

        # delete the aggregate. This should delete all the slivers
        # and resources, and create a DummySliceEvent to that effect.
        response = test_get_and_post_form(
            client=self.client,
            url=self.agg1.get_delete_url(next="/"),
            params={},
        )
        self.assertRedirects(response, "/")
        
        self.assertEqual(DummyAggregate.objects.count(), 1)
        self.assertEqual(Sliver.objects.count(), 3)
        self.assertEqual(
            DummySliceEvent.objects.filter(
                slice="%s" % self.slice, status="stopped").count(), 1)

    def test_allowed_edit(self):
        """
        Tests that we can edit an existing aggregate.
        """
        give_permission_to("can_add_aggregate", Aggregate, self.u)
        agg = DummyAggregate.objects.create(
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
        self.assertRedirects(response, "/",
                             msg_prefix="response was %s" % response)
        