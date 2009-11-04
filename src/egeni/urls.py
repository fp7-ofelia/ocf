from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^clearinghouse/', include('egeni.clearinghouse.urls')),
    (r'^admin/(.*)', admin.site.root),
)

urlpatterns += patterns('django.contrib.auth.views',
    (r'^accounts/login/$', 'login', {'template_name': 'accounts/login.html'}),
    (r'^accounts/logout/$', 'logout_then_login'),
    url(r'^accounts/password/change/$', 'password_change', {'template_name': 'accounts/password_change_form.html'}, name='password_change'),
    (r'^accounts/password/change_done/$', 'password_change_done', {'template_name': 'accounts/password_change_done.html'}),
)
