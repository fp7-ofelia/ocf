from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('clearinghouse.openflow.views',
#    url(r'^$', 'home', name='openflow_home'),
    url(r'^aggregate/create/$', 'aggregate_create', name='openflow_aggregate_create'),
#    url(r'^aggregate/(?P<obj_id>\d+)/edit/$', 'edit', name='openflow_aggregate_edit'),
)

urlpatterns += patterns('',
    (r'^gapi$', 'rpc4django.views.serve_rpc_request'),
)
