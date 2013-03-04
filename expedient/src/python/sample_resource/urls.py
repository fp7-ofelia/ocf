from django.conf.urls.defaults import patterns, url
from expedient.common.rpc4django.utils import rpc_url

urlpatterns = patterns('')

#urlpatterns = patterns('sample_resource.controller.ResourceController',
#    url(r'^aggregate/create/$', 'aggregate_crud', name='sample_resource_aggregate_create'),
#    url(r'^aggregate/(?P<agg_id>\d+)/edit/$', 'aggregate_crud', name='sample_resource_aggregate_edit'),
#)
#
#
#urlpatterns = urlpatterns + patterns('sample_resource.views',
#    url(r'^create_sample_resource/(?P<slice_id>\d+)/(?P<agg_id>\d+)/$', 'create_sample_resource', name='create_sample_resource'),
#    url(r'^manage_sample_resource/(?P<slice_id>\d+)/(?P<sample_resource_id>\d+)/(?P<action_type>\w+)/$', 'manage_sample_resource', name='manage_sample_resource'),
#    url(r'^sample_resource_crud/(?P<slice_id>\d+)/(?P<server_id>\d+)/$', 'sample_resource_crud', name='sample_resource_crud'),
#    url(r'^sample_resource_status/(?P<slice_id>\d+)/$', 'check_sample_resource_status', name='check_sample_resource_status'),
#)
#
#urlpatterns = urlpatterns + patterns('',
#     rpc_url(r'^xmlrpc/sample_resource_am/$', name='sample_resource_am'),
#)

