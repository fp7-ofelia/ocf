'''
Created on Jul 12, 2010

@author: jnaous
'''

from django.test import TestCase
from openflow.dummyom.models import DummyOM
from django.contrib.auth.models import User
from openflow.plugin.models import OpenFlowAggregate
from expedient.common.xmlrpc_serverproxy.models import PasswordXMLRPCServerProxy

import logging
logger = logging.getLogger("OpenFlowPluginTests")

NUM_DUMMY_OMS = 3
NUM_SWITCHES_PER_AGG = 10
NUM_LINKS_PER_AGG = 30
SCHEME = "test"
HOST = "testserver"

class Tests(TestCase):
    def setUp(self):
        """
        Create DummyOMs and login.
        """
        for i in range(NUM_DUMMY_OMS):
            om = DummyOM.objects.create()
            om.populate_links(NUM_SWITCHES_PER_AGG, 
                              NUM_LINKS_PER_AGG/2)
            username = "clearinghouse%s" % i
            password = "clearinghouse"
            u = User.objects.create(username=username)
            u.set_password(password)
            u.save()
    
            # Add the aggregate to the CH
            url = SCHEME + "://%s/dummyom/%s/xmlrpc/" % (HOST, om.id)
            
            proxy = PasswordXMLRPCServerProxy.objects.create(
                username=username, password=password,
                url=url, verify_certs=False,
            )
    
            # test availability
            if not proxy.is_available():
                raise Exception("Problem: Proxy not available")

            proxy.delete()
            
    def test_create_aggregate(self):
        """
        Test that we can create an OpenFlow Aggregate using the create view.
        """
        pass
    
    