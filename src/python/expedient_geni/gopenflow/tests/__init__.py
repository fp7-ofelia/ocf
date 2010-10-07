'''
Created on Oct 6, 2010

@author: jnaous
'''
from django.conf import settings
from expedient.common.tests.manager import SettingsTestCase
from django.contrib.auth.models import User
from expedient.common.middleware import threadlocals
from openflow.dummyom.models import DummyOM
from expedient.common.tests.client import test_get_and_post_form
from django.core.urlresolvers import reverse
from expedient_geni.gopenflow.tests.models import DummyOFAggregate
from openflow.plugin.models import OpenFlowAggregate
from expedient.common.rpc4django import views as rpc4django_views

from rpc import *

MOD = "expedient_geni.gopenflow"

class Tests(SettingsTestCase):
    urls = MOD + ".tests.urls"
    
    def setUp(self):
        """
        Update settings, create DummyOMs and test models and login.
        """
        # add the test application
        self.settings_manager.set(
            INSTALLED_APPS=settings.INSTALLED_APPS + [MOD + ".tests"],
            DEBUG_PROPAGATE_EXCEPTIONS=True,
        )
        
        logger.debug("Updating RPC dispatchers.")
        
        rpc4django_views._register_rpcmethods(
            [MOD + ".tests"],
            restrict_introspection=False,
            dispatchers=rpc4django_views.dispatchers)
        
        self.su = User.objects.create_superuser(
            "superuser", "bla@bla.com", "password")
        self.client.login(username="superuser", password="password")

        om = DummyOM.objects.create()
        om.populate_links(5, 10)

        # Add the aggregate to the CH
        test_get_and_post_form(
            self.client, reverse("openflow_aggregate_create"),
            dict(
                name="DummyOM",
                description="DummyOM Description",
                location="Stanford, CA",
                usage_agreement="Do you agree?",
                username="superuser",
                password="password",
                url="test://testserver:80/dummyom/1/xmlrpc/",
            )
        )
        
        self.of = DummyOFAggregate.objects.create()
        
        # now get the list of resources and store it, then delete the
        # OpenFlowAggregate.
        self.of.snapshot_switches()
        OpenFlowAggregate.objects.all().delete()
        
        # set defaults for SSL_CLIENT_CERT and REMOTE_USER
        tl = threadlocals.get_thread_locals()
        #tl["test_client_transport_defaults"]["REMOTE_USER"] = 
        
    def test_add_aggregate(self):
        resp = test_get_and_post_form(
            self.client, reverse("gopenflow_aggregate_create"),
            dict(
                name="DummyOM",
                description="DummyOF Description",
                location="Stanford, CA",
                url="test://testserver:80"+reverse("dummy_gopenflow"),
            )
        )
        self.assertRedirects(resp, reverse("home"), msg_prefix="response was %s" % resp)
        self.assertEqual(self.of.adv_rspec, gapi.ListResources({}, None))
        
    def test_reserve_sliver(self):
        pass