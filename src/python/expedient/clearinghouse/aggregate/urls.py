'''
@author jnaous
'''
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('expedient.clearinghouse.aggregate.views',
    url(r'^list/$', 'list_aggs', name='aggregate_all'),
    url(r'^list/(?P<obj_id>\d+)/$', 'list_aggs', name='aggregate_list_highlight'),
    url(r'^delete/(?P<obj_id>\d+)/$', 'delete', name='aggregate_delete'),
)

