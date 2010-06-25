'''
Created on Jun 19, 2010

@author: jnaous
'''
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('expedient.ui.html.views',
    url(r'^(?P<slice_id>\d+)/$', 'home', name='html_plugin_home'),
    url(r'^flowspace/(?P<slice_id>\d+)/$', 'flowspace', name='html_plugin_flowspace'),
)
