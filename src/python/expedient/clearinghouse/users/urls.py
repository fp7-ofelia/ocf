'''
@author: jnaous
'''
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('expedient.clearinghouse.users.views',
    url(r'^$', 'home', name='users_home'),
    url(r'^(?P<user_id>\d+)/detail/$', 'detail', name='users_detail'),
    url(r'^detail/$', 'detail', name='users_my_detail'),
    url(r'^(?P<user_id>\d+)/saved/$', 'saved', name='users_saved'),
    url(r'^(?P<user_id>\d+)/delete/$', 'delete', name="users_delete"),
)
