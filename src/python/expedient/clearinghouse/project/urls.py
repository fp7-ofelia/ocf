'''
@author: jnaous
'''
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('expedient.clearinghouse.project.views',
    url(r'^list/$', 'list', name='project_list'),
    url(r'^create/$', 'create', name="project_create"),
    url(r'^update/iframe/(?P<proj_id>\d+)/$', 'update_iframe', name="project_iframe_update"),
    url(r'^update/(?P<proj_id>\d+)/$', 'update', name="project_update"),
    url(r'^detail/(?P<proj_id>\d+)/$', 'detail', name='project_detail'),
    url(r'^delete/(?P<proj_id>\d+)/$', 'delete', name="project_delete"),
    url(r'^aggregates/add/(?P<proj_id>\d+)/$', 'add_aggregate', name="project_add_agg"),
    url(r'^aggregates/update/(?P<proj_id>\d+)/(?P<agg_id>\d+)/$', 'update_aggregate', name="project_update_agg"),
    url(r'^aggregates/remove/(?P<proj_id>\d+)/(?P<agg_id>\d+)/$', 'remove_aggregate', name="project_remove_agg"),
)
