from django.conf.urls.defaults import *

urlpatterns = patterns('clearinghouse.users.views',
    url(r'^/$', 'home', name='user_home'),
    url(r'^(?P<user_id>\d+)/detail/$', 'detail', name='user_detail'),
    url(r'^(?P<user_id>\d+)/saved/$', 'saved', name='user_saved'),
    url(r'^(?P<user_id>\d+)/delete/$', 'delete', name="user_delete"),
)
