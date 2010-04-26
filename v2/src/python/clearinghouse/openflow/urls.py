from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('clearinghouse.openflow.views',
#    url(r'^$', 'home', name='openflow_home'),
#    url(r'^(?P<user_id>\d+)/detail/$', 'detail', name='users_detail'),
#    url(r'^detail/$', 'detail', name='users_my_detail'),
#    url(r'^(?P<user_id>\d+)/saved/$', 'saved', name='users_saved'),
#    url(r'^(?P<user_id>\d+)/delete/$', 'delete', name="users_delete"),
)

urlpatterns += patterns('',
    (r'^gapi$', 'rpc4django.views.serve_rpc_request'),
)
