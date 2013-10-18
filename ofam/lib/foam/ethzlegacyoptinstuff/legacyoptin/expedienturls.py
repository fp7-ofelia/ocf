from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^xmlrpc/$', 'expedient.common.rpc4django.views.serve_rpc_request'),
)
