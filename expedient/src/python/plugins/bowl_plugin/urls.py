#
# BOWL expedient plugin for the Berlin Open Wireless Lab
# based on the sample plugin
#
# Authors: Theresa Enghardt (tenghardt@inet.tu-berlin.de)
#          Robin Kuck (rkuck@net.t-labs.tu-berlin.de)
#          Julius Schulz-Zander (julius@net.t-labs.tu-berlin.de)
#          Tobias Steinicke (tsteinicke@net.t-labs.tu-berlin.de)
#
# Copyright (C) 2013 TU Berlin (FG INET)
# All rights reserved.
#
from django.conf.urls.defaults import *

urlpatterns = patterns(
     'bowl_plugin.controller.aggregate',
    url(r'^aggregate/create/$', 'aggregate_crud', name='bowl_plugin_aggregate_create'),
    url(r'^aggregate/(?P<agg_id>\d+)/edit/$', 'aggregate_crud', name='bowl_plugin_aggregate_edit'),
    url(r'^aggregate/delete/$', 'aggregate_delete', name='bowl_plugin_aggregate_delete'),
)

urlpatterns = urlpatterns + patterns(
     'bowl_plugin.controller.resource',
    url(r'^resource/provision/(?P<agg_id>\d+)/(?P<slice_id>\d+)/$', 'resource_provision', name='bowl_plugin_resource_provision'),
    url(r'^resource/extend/(?P<agg_id>\d+)/(?P<slice_id>\d+)/$', 'resource_extend', name='bowl_plugin_resource_extend'),
    url(r'^resource/delete/(?P<agg_id>\d+)/(?P<slice_id>\d+)/$', 'resource_delete', name='bowl_plugin_resource_delete'),
    url(r'^resource/allocate/(?P<slice_id>\d+)/(?P<agg_id>\d+)/(?P<node_id>\d*)/$', 'resource_allocate', name='bowl_plugin_resource_allocate'),
    url(r'^resource/allocate/(?P<slice_id>\d+)/(?P<agg_id>\d+)/$', 'resource_allocate', name='bowl_plugin_resource_allocate'),
)

urlpatterns = urlpatterns + patterns('bowl_plugin.controller.GUIdispatcher',
#urlpatterns = patterns('bowl_plugin.controller.GUIdispatcher',
    url(r'^create/(?P<slice_id>\d+)/(?P<agg_id>\d+)/$', 'create_resource', name='bowl_plugin_resource_create'),
    url(r'^edit/(?P<slice_id>\d+)/(?P<agg_id>\d+)/(?P<resource_id>\d+)/$', 'resource_crud', name='bowl_plugin_resource_edit'),
    url(r'^manage/(?P<resource_id>\d+)/(?P<action_type>\w+)/$', 'manage_resource', name='bowl_plugin_resource_manage'),
    url(r'^crud/(?P<slice_id>\d+)/(?P<agg_id>\d+)/$', 'resource_crud', name='bowl_plugin_resource_crud'),
)

