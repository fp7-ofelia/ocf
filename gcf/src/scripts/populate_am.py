'''
Created on May 13, 2010

@author: jnaous
'''
from clearinghouse.dummyom.models import DummyOM
from django.contrib.auth.models import User
from clearinghouse.openflow.models import OpenFlowAggregate
from clearinghouse.xmlrpc_serverproxy.models import PasswordXMLRPCServerProxy
import socket

NUM_DUMMY_OMS = 3
NUM_SWITCHES_PER_AGG = 10
NUM_LINKS_PER_AGG = 10

HOST = socket.getfqdn()
PORT = 443
PREFIX = ""

# Dummy OMs
for i in range(NUM_DUMMY_OMS):
    om = DummyOM.objects.create()
    om.populate_links(NUM_SWITCHES_PER_AGG, NUM_LINKS_PER_AGG)
    username = "clearinghouse%s" % i
    password = "clearinghouse"
    u = User.objects.create(username=username)
    u.set_password(password)
    u.save()
    
    # Add the aggregate to the CH
    proxy = PasswordXMLRPCServerProxy.objects.create(
        username=username,
        password=password,
        url="https://%s:%s/%sdummyom/%s/xmlrpc/" % (
            HOST, PORT, PREFIX, om.id,
        ),
        verify_certs = False,
    )

    # test availability
    print "Checking availability."
    if not proxy.is_available:
        raise Exception("Problem: Proxy not available")

    # Add aggregate
    of_agg = OpenFlowAggregate.objects.create(
        name=username,
        description="hello",
        location="America",
        client=proxy,
    )

    err = of_agg.setup_new_aggregate(HOST)
    if err:
        raise Exception("Error setting up aggregate: %s" % err)
