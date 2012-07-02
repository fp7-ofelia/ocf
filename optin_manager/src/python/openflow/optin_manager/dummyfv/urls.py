'''
Created on May 16, 2010

@author: jnaous
'''
from django.conf.urls.defaults import patterns
from expedient.common.rpc4django.utils import rpc_url

urlpatterns = patterns('',
    rpc_url(r'^(?P<fv_id>\d+)/xmlrpc/$', name="dummyfv_rpc"),
)
