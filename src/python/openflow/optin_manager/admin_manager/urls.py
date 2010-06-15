from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('openflow.optin_manager.admin_manager.views',
    url(r'^promote_to_admin$', 'promote_to_admin'),
    url(r'^approve_admin/(?P<req_id>\d+)/approve$', 'approve_admin',{'operation':1}),
    url(r'^approve_admin/(?P<req_id>\d+)/reject$', 'approve_admin',{'operation':2}),
    url(r'^approve_admin$','approve_admin',{'operation':0,'req_id':0}),
    url(r'^resign_admin$','resign_admin'),
    url(r'^user_add_fs$','user_add_fs'),
)