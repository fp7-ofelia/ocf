#URLCONF for flowspace management app
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('openflow.optin_manager.flowspace.views',
    url(r'^view_opt_in$', 'view_opt_in',{'error_msg' : 0}),
    url(r'^opt_in$', 'add_opt_in'),
    url(r'^opt_out$', 'opt_out'),
    url(r'^update_opts$', 'update_opts'),
    url(r'^experiments$', 'view_experiments'),
    url(r'^experiment/(?P<exp_id>\d+)$', 'view_experiment'),
)
