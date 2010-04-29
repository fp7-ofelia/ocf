from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('clearinghouse.aggregate.views',
    url(r'^list/$', 'list_aggs', name='aggregate_all'),
)

