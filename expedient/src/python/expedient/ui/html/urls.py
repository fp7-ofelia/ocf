'''
Created on Jun 19, 2010

@author: jnaous
'''
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('expedient.ui.html.views',
    url(r'^(?P<slice_id>\d+)/$', 'home', name='html_plugin_home'),
    url(r'^flowspace/(?P<slice_id>\d+)/$', 'flowspace', name='html_plugin_flowspace'),
    url(r'^ssh_keys/(?P<slice_id>\d+)/$', 'sshkeys', name='html_plugin_sshkeys'),
    url(r'^ssh_public_key/(?P<slice_id>\d+)/$', 'sshkey_file', kwargs={"type": "ssh_public_key"}, name='html_plugin_sshkeys_public'),
    url(r'^ssh_private_key/(?P<slice_id>\d+)/$', 'sshkey_file', kwargs={"type": "ssh_private_key"}, name='html_plugin_sshkeys_private'),
)
