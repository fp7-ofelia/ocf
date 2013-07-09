'''
Created on Jun 19, 2010

@author: jnaous
'''
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('expedient.ui.rspec.views',
    url(r'^(?P<slice_id>\d+)/$', 'home', name='rspec_plugin_home'),
    url(r'^adv/$', 'download_adv_rspec', name='rspec_download_adv'),
    url(r'^resv/(?P<slice_id>\d+)/$', 'download_resv_rspec', name='rspec_download_resv'),
)
