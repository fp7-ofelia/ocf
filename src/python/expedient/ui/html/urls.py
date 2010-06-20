'''
Created on Jun 19, 2010

@author: jnaous
'''
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^(?P<slice_id>\d+)/$', 'expedient.ui.html.views.home', name='html_plugin_home'),
)
