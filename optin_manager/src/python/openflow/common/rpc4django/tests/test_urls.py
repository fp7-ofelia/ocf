'''
Created on Jun 9, 2010

@author: jnaous
'''
from django.conf.urls.defaults import *
from expedient.common.rpc4django.utils import rpc_url

urlpatterns = patterns("",
    rpc_url(r"^RPC2/$", name="serve_rpc_request", use_name_for_dispatch=False),
    rpc_url(r"^my_url/RPC2/$", name="my_url_name"),
)
