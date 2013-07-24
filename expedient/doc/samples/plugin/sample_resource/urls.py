from django.conf.urls.defaults import *

urlpatterns = patterns('sample_resource.controller.aggregate',
    url(r'^aggregate/create/$', 'aggregate_crud', name='sample_resource_aggregate_create'),
    url(r'^aggregate/(?P<agg_id>\d+)/edit/$', 'aggregate_crud', name='sample_resource_aggregate_edit'),
)

urlpatterns = urlpatterns + patterns('sample_resource.controller.GUIdispatcher',
    url(r'^create/(?P<slice_id>\d+)/(?P<agg_id>\d+)/$', 'create_resource', name='sample_resource_resource_create'),
    url(r'^edit/(?P<slice_id>\d+)/(?P<agg_id>\d+)/(?P<resource_id>\d+)/$', 'resource_crud', name='sample_resource_resource_edit'),
    url(r'^manage/(?P<resource_id>\d+)/(?P<action_type>\w+)/$', 'manage_resource', name='sample_resource_resource_manage'),
    url(r'^crud/(?P<slice_id>\d+)/(?P<agg_id>\d+)/$', 'resource_crud', name='sample_resource_resource_crud'),
)

