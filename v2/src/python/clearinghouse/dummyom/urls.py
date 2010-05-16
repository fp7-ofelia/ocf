'''
Created on May 12, 2010

@author: jnaous
'''
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^(?P<om_id>\d+)/xmlrpc/$', 'apps.rpc4django.views.serve_rpc_request', name="dummyom_rpc"),
)
