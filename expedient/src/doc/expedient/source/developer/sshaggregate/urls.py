from django.conf.urls.defaults import *

urlpatterns = patterns('sshaggregate.views',
    url(r'^aggregate/create/$', 'aggregate_crud', name='sshaggregate_aggregate_create'),
    url(r'^aggregate/(?P<agg_id>\d+)/edit/$', 'aggregate_crud', name='sshaggregate_aggregate_edit'),
    url(r'^aggregate/(?P<agg_id>\d+)/servers/$', 'aggregate_add_servers', name='sshaggregate_aggregate_servers'),
)
