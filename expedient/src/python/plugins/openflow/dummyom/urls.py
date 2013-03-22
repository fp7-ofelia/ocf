'''
Created on May 12, 2010

@author: jnaous
'''
from django.conf.urls.defaults import patterns
from expedient.common.rpc4django.utils import rpc_url

urlpatterns = patterns('',
    rpc_url(r'^(?P<om_id>\d+)/xmlrpc/$', name="dummyom_rpc"),
)
