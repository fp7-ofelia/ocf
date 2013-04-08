from django.conf.urls.defaults import patterns
#from expedient.common.rpc4django.utils import rpc_url

urlpatterns = patterns('',
    (r'^xmlrpc/$', 'expedient.common.rpc4django.views.serve_rpc_request'),
#    (r'^sfa/?$', 'optin_sfa'),
)
