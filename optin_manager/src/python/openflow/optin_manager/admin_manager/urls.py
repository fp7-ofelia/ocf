from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('openflow.optin_manager.admin_manager.views',
    url(r'^promote_to_admin$', 'promote_to_admin', name="promote_to_admin"),
    url(r'^delete_promote_to_admin$', 'delete_promote_to_admin', name="delete_promote_to_admin"),
    url(r'^resign_admin$','resign_admin'),
    url(r'^user_reg_fs$','user_reg_fs', name="user_reg_fs"),
    url(r'^admin_reg_fs$','admin_reg_fs', name="admin_reg_fs"),
    url(r'^admin_reg_fs_by_file$','admin_reg_fs_by_file', name="admin_reg_fs_by_file"),
    url(r'^approve_user$', 'approve_user', name="approve_user_reg"),
    url(r'^approve_admin$', 'approve_admin',name="approve_admin"),
    url(r'^user_unreg_fs$','user_unreg_fs', name="user_unregister_flowspace"),
    url(r'^admin_unreg_fs$','admin_unreg_fs', name="admin_unregister_flowspace"),
    url(r'^set_auto_approve$','set_auto_approve', name="set_auto_approve"),
    url(r'^manage_admin_fs$','manage_admin_fs', name="manage_admin_fs"),
    url(r'^change_admin_fs/(?P<user_id>\d+)$','change_admin_fs', name="change_admin_fs"),
    url(r'^manage_user_fs$','manage_user_fs', name="manage_user_fs"),
    url(r'^change_user_fs/(?P<user_id>\d+)$','change_user_fs', name="change_user_fs"),
)
