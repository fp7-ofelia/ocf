'''Slice-specific tests
Created on Feb 16, 2011

@author: jnaous
'''
from datetime import datetime, timedelta
from django.conf import settings
from expedient.common.tests.manager import SettingsTestCase
from expedient.clearinghouse.utils import add_dummy_agg_to_test_settings,\
    add_test_aggregate_to_project, start_test_slice
from expedient.common.tests.client import test_get_and_post_form
from expedient.clearinghouse.slice.models import Slice
from expedient.common.middleware import threadlocals
from django.core.management import call_command
from expedient.clearinghouse.aggregate.tests.models import DummySliceEvent
from expedient.common.timer.models import Job

class Tests(SettingsTestCase):
    def setUp(self):
        add_dummy_agg_to_test_settings(self)
        
    def test_slice_expiration_form(self):
        add_test_aggregate_to_project(self)
        
        self.client.login(
            username=self.u2.username, password="password")
        threadlocals.push_frame(user=self.u2)
        
        expiration = datetime.now() \
            + timedelta(days=settings.MAX_SLICE_LIFE + 5)
        
        response = test_get_and_post_form(
            client=self.client,
            url=Slice.get_create_url(proj_id=self.project.id),
            params={
                "name": "slice name",
                "description": "slice description",
                "expiration_date_0": "%s" % expiration.date(),
                "expiration_date_1": expiration.time().strftime("%H:%m:%S"),
            },
        )
        
        self.assertContains(
            response, "The entered date is too late. Maximum is",
        )
        
        response = test_get_and_post_form(
            client=self.client,
            url=Slice.get_create_url(proj_id=self.project.id),
            params={
                "name": "slice name",
                "description": "slice description",
                "expiration_date_0": "xyaz",
                "expiration_date_1": "%s" % expiration.time(),
            },
        )
        
        self.assertContains(
            response, "Enter a valid date",
        )

        self.client.logout()
        threadlocals.pop_frame()

    def test_slice_expiration(self):
        """
        Check that a slice expires correctly.
        """
        
        start_test_slice(self)
        
        self.slice.expiration_date = datetime.now() - timedelta(days=1)
        self.slice.save()
        
        slice_name = "%s" % self.slice
        
        self.assertTrue(self.slice.started)
        
        for j in Job.objects.all():
            j.next_run_time = datetime.now()
            j.save()
        
        call_command("run_timer_jobs")
        
        self.slice = Slice.objects.get(pk=self.slice.pk)
        self.assertFalse(self.slice.started)
        
        self.assertEqual(
            DummySliceEvent.objects.filter(
                slice=slice_name,
                status="stopped",
                aggregate="%s" % self.agg1,
            ).count(),
            1,
        )
        self.assertEqual(
            DummySliceEvent.objects.filter(
                slice=slice_name,
                status="stopped",
                aggregate="%s" % self.agg2,
            ).count(),
            1,
        )
        
        