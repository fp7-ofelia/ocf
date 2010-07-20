'''
Created on Jul 19, 2010

@author: jnaous
'''
from django.core.urlresolvers import reverse
from django.test import Client
from expedient.common.tests.client import test_get_and_post_form
from django.contrib.auth.models import User
from pyquery import PyQuery as pq
from openflow.plugin.models import OpenFlowInterface, NonOpenFlowConnection
from geni.planetlab.models import PlanetLabNode

try:
    from setup_expedient_params import \
        SUPERUSER_USERNAME, SUPERUSER_PASSWORD,\
        USER_INFO,\
        PL_AGGREGATE_INFO,\
        OF_AGGREGATE_INFO,\
        OF_PL_CONNECTIONS
        
except ImportError:
    print """
Could not import setup_om_params module. Make sure this
module exists and that it contains the following variables:
        SUPERUSER_USERNAME, SUPERUSER_PASSWORD,
        CH_PASSWORD, CH_USERNAME
"""
    raise

def run():
    client = Client()
    client.login(username=SUPERUSER_USERNAME,
                 password=SUPERUSER_PASSWORD)
    
    # Add all planetlab aggregates
    for pl_agg in PL_AGGREGATE_INFO:
        response = test_get_and_post_form(
            client,
            reverse("planetlab_aggregate_create"),
            pl_agg,
        )
        assert response.status_code == 301
        
    for of_agg in OF_AGGREGATE_INFO:
        response = test_get_and_post_form(
            client,
            reverse("openflow_aggregate_create"),
            of_agg,
        )
        assert response.status_code == 301
        
    for cnxn_tuple in OF_PL_CONNECTIONS:
        NonOpenFlowConnection.objects.get_or_create(
            of_iface=OpenFlowInterface.objects.get(
                switch__datapath_id=cnxn_tuple[0],
                port_num=cnxn_tuple[1],
            ),
            resource=PlanetLabNode.objects.get(name=cnxn_tuple[2]),
        )
    
    client.logout()
    
    for username, info in USER_INFO.items():
        # create user
        User.objects.create_user(
            username=username, email=info["email"], password=info["password"])
        
        client.login(username=username, password=info["password"])
        # create project and slice
        for project in info["projects"]:
            response = test_get_and_post_form(
                client, reverse("project_create"),
                params=dict(
                    name=project["name"],
                    description=project["description"],
                ),
            )
            assert response.status_code == 301
            for slice in project["slices"]:
                response = test_get_and_post_form(
                    client, reverse("slice_create"),
                    params=dict(
                        name=slice["name"],
                        description=slice["description"],
                    ),
                )
                assert response.status_code == 301
        client.logout()
        