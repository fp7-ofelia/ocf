from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    (r'^gapi/$', 'rpc4django.views.serve_rpc_request'),
)
