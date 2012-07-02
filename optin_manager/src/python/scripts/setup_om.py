'''
Created on Jul 19, 2010

@author: jnaous
'''
from django.core.urlresolvers import reverse
from django.test import Client
from expedient.common.tests.client import test_get_and_post_form
from django.contrib.auth.models import User
from pyquery import PyQuery as pq

try:
    from setup_expedient_params import \
        SUPERUSER_USERNAME, SUPERUSER_PASSWORD,\
        FV_USERNAME, FV_PASSWORD, FV_URL,\
        CH_PASSWORD, CH_USERNAME,\
        USER_INFO
        
except ImportError:
    print """
Could not import setup_om_params module. Make sure this
module exists and that it contains the following variables:
        SUPERUSER_USERNAME, SUPERUSER_PASSWORD,
        FV_USERNAME, FV_PASSWORD, FV_URL,
        CH_PASSWORD, CH_USERNAME
"""
    raise

def run():
    client = Client()
    client.login(username=SUPERUSER_USERNAME,
                 password=SUPERUSER_PASSWORD)
    
    # setup the Flowvisor
    response = test_get_and_post_form(
        client,
        reverse("set_flowvisor"),
        params=dict(
            name="flowvisor",
            username=FV_USERNAME,
            password=FV_PASSWORD,
            password2=FV_PASSWORD,
            url=FV_URL,
        ),
    )
    assert response.status_code == 301

    # setup the Clearinghouse user
    response = test_get_and_post_form(
        client, reverse("set_clearinghouse"),
        params=dict(
            username=CH_USERNAME,
            password1=CH_PASSWORD,
            password2=CH_PASSWORD,
        ),
    )
    assert response.status_code == 301
    
    client.logout()
    
    for username, info in USER_INFO.items():
        # create user
        User.objects.create_user(
            username=username, email=info["email"], password=info["password"])
        
        client.login(username=username, password=info["password"])
        # request flowspace
        for fs in info["flowspace"]:
            response = test_get_and_post_form(
                client, reverse("user_reg_fs"),
                params=dict(
                    mac_addr=fs["mac_addr"],
                    ip_addr=fs["ip_addr"],
                ),
            )
            assert response.status_code == 301
        client.logout()
        
    
    # Login to approve user requests
    client.login(username=SUPERUSER_USERNAME,
                 password=SUPERUSER_PASSWORD)

    # Parse the approval form
    resp = client.get(reverse("approve_user_reg_table"))
    
    # Get all the forms
    d = pq(resp.content, parser="html")
    forms = d("form")
    for f in forms:
        # only post to approve urls
        if "approve" in f.action:
            client.post(f.action, {})
    
    client.logout()
