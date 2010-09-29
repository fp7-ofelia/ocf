'''
@author: jnaous
'''
from django.conf.urls.defaults import patterns, url
from expedient.common.rpc4django.utils import rpc_url

urlpatterns = patterns('expedient_geni.views',
    url(r'^certs/manage/(?P<user_id>\d+)/$', 'user_cert_manage', name='gcf_cert_manage'),
    url(r'^certs/create/(?P<user_id>\d+)/$', 'user_cert_generate', name='gcf_cert_generate'),
    url(r'^certs/cert/(?P<user_id>\d+)/$', 'user_cert_download', name='gcf_cert_download'),
    url(r'^certs/key/(?P<user_id>\d+)/$', 'user_key_download', name='gcf_key_download'),
    url(r'^certs/upload/(?P<user_id>\d+)/$', 'user_cert_upload', name='gcf_cert_upload'),
)
