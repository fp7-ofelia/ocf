from django.conf.urls.defaults import *
from expedient.common.rpc4django.utils import rpc_url
from expedient.common.rpc4django import rpcmethod

urlpatterns = patterns('sample_resource.controller.vtAggregateController.vtAggregateController',
    url(r'^aggregate/create/$', 'aggregate_crud', name='sample_resource_aggregate_create'),
    url(r'^aggregate/(?P<agg_id>\d+)/edit/$', 'aggregate_crud', name='sample_resource_aggregate_edit'),
)


urlpatterns = urlpatterns + patterns('sample_resource.controller.dispatchers.GUIdispatcher',
    url(r'^create/(?P<slice_id>\d+)/(?P<agg_id>\d+)/$', 'create_resource', name='create'),
    url(r'^manage_vm/(?P<slice_id>\d+)/(?P<vm_id>\d+)/(?P<action_type>\w+)/$', 'manage_vm', name='manage_vm'),
    url(r'^resource_crud/(?P<slice_id>\d+)/(?P<server_id>\d+)/$', 'resource_crud', name='resource_crud'),
    url(r'^vms_status/(?P<slice_id>\d+)/$', 'check_vms_status', name='check_vms_status'),
    url(r'^update_messages/$', 'update_messages', name='update_messages'),
)




urlpatterns = urlpatterns + patterns('',
     rpc_url(r'^xmlrpc/sr_am/$', name='sr_am'),
)
