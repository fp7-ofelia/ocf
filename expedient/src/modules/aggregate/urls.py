'''
@author: jnaous
'''
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('expedient.clearinghouse.aggregate.views',
    url(r'^list/$', 'list', name='aggregate_all'),
    url(r'^list/(?P<agg_id>\d+)/$', 'list', name='aggregate_list_highlight'),
    url(r'^delete/(?P<agg_id>\d+)/$', 'delete', name='aggregate_delete'),
    url(r'^info/(?P<ct_id>\d+)/$', 'info', name='aggregate_info'),
    url(r'^status/(?P<agg_id>\d+)/$', 'status_img_url', name='aggregate_status_img'),
)

