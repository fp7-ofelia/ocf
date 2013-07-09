'''
@author: jnaous
'''
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('expedient_geni.views',
    # Certificate management
    url(r'^certs/manage/(?P<user_id>\d+)/$', 'user_cert_manage', name='gcf_cert_manage'),
    url(r'^certs/create/(?P<user_id>\d+)/$', 'user_cert_generate', name='gcf_cert_generate'),
    url(r'^certs/cert/(?P<user_id>\d+)/$', 'user_cert_download', name='gcf_cert_download'),
    url(r'^certs/key/(?P<user_id>\d+)/$', 'user_key_download', name='gcf_key_download'),
    url(r'^certs/upload/(?P<user_id>\d+)/$', 'user_cert_upload', name='gcf_cert_upload'),
    # SSH keys
    url(r'^ssh_keys/(?P<slice_id>\d+)/$', 'sshkeys', name='gcf_sshkeys'),
    url(r'^ssh_public_key/(?P<slice_id>\d+)/$', 'sshkey_file', kwargs={"type": "ssh_public_key"}, name='gcf_sshkeys_public'),
    url(r'^ssh_private_key/(?P<slice_id>\d+)/$', 'sshkey_file', kwargs={"type": "ssh_private_key"}, name='gcf_sshkeys_private'),
)
