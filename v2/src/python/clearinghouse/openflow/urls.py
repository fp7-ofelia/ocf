from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('clearinghouse.openflow.views',
#    url(r'^$', 'home', name='openflow_home'),
    url(r'^aggregate/create/$', 'aggregate_crud', name='openflow_aggregate_create'),
    url(r'^aggregate/(?P<agg_id>\d+)/edit/$', 'aggregate_crud', name='openflow_aggregate_edit'),
    url(r'^aggregate/(?P<agg_id>\d+)/delete/$', 'aggregate_delete', name='openflow_aggregate_delete'),
)

urlpatterns += patterns('',
    (r'^gapi$', 'rpc4django.views.serve_rpc_request'),
)
