from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^xmlrpc/$', 'apps.rpc4django.views.serve_rpc_request'),
)
