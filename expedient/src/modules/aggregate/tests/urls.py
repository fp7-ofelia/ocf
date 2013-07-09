'''
Created on Jun 11, 2010

@author: jnaous
'''
from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('expedient.clearinghouse.aggregate.tests.views',
    url(r'^tests/create/$', 'create', name='tests_aggregate_create'), 
    url(r'^tests/edit/(?P<agg_id>\d+)/$', 'edit', name='tests_aggregate_edit'),
)
