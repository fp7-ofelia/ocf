#URLCONF for flowspace management app
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('openflow.optin_manager.opts.views',
    url(r'^view_opt_in$', 'change_priority'),
    url(r'^change_priority$', 'change_priority'),
    url(r'^opt_in$', 'add_opt_in', name="opt_in_experiment"),
    url(r'^opt_out$', 'opt_out', name="opt_out_of_experiment"),
    url(r'^experiments$', 'view_experiments'),
    url(r'^experiment/(?P<exp_id>\d+)$', 'view_experiment'),
    url(r'^experiment_simple/(?P<exp_id>\d+)$', 'view_experiment_simple'),
)
