'''
Created on Jun 17, 2010

@author: jnaous
'''
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('expedient.clearinghouse.slice.views',
    url(r'^detail/(?P<slice_id>\d+)/$', 'detail', name='slice_detail'),
    url(r'^create/(?P<proj_id>\d+)/$', 'create', name='slice_create'),
    url(r'^update/(?P<slice_id>\d+)/$', 'update', name='slice_update'),
    url(r'^delete/(?P<slice_id>\d+)/$', 'delete', name="slice_delete"),
    url(r'^start/(?P<slice_id>\d+)/$', 'start', name="slice_start"),
    url(r'^stop/(?P<slice_id>\d+)/$', 'stop', name="slice_stop"),
    url(r'^aggregates/add/(?P<slice_id>\d+)/$', 'add_aggregate', name="slice_add_agg"),
    url(r'^aggregates/update/(?P<slice_id>\d+)/(?P<agg_id>\d+)/$', 'update_aggregate', name="slice_update_agg"),
    url(r'^aggregates/remove/(?P<slice_id>\d+)/(?P<agg_id>\d+)/$', 'remove_aggregate', name="slice_remove_agg"),
    url(r'^resources/(?P<slice_id>\d+)/$', 'select_ui_plugin', name="slice_manage_resources"),    
)

