from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('openflow.optin_manager.controls.views',
    url(r'^set_clearinghouse$', 'set_clearinghouse', name="set_clearinghouse"),
    url(r'^set_flowvisor$', 'set_flowvisor', name="set_flowvisor"),
)
