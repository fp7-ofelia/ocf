'''
Created on May 16, 2010

@author: jnaous
'''
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^(?P<fv_id>\d+)/xmlrpc/$', 'apps.rpc4django.views.serve_rpc_request', name="dummyfv_rpc"),
)
