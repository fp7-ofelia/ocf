#URLCONF for flowspace management app
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('OM.flowspace.views',
    url(r'^view_opt_in$', 'view_opt_in'),
    url(r'^add_opt_in$', 'add_opt_in'),
)