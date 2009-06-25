from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^clearinghouse/', include('egeni.clearinghouse.urls')),
    (r'^admin/(.*)', admin.site.root),
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'accounts/login.html'}),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),
)
