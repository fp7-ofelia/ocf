'''
Created on Jun 30, 2013

@author: CarolinaFernandez
'''
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('expedient.clearinghouse.administration.views',
    url(r'^$', 'home', name='administration_home'),
    url(r'^log/(?P<module_name>\w+)/view/$', 'view_log', name="administration_view_log"),
    url(r'^log/(?P<module_name>\w+)/(?P<option>\w+)/remove/$', 'remove_log', name="administration_remove_log"),
)

