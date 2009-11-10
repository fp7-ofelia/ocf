from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^clearinghouse/', include('egeni.clearinghouse.urls')),
    (r'^admin/(.*)', admin.site.root),
)

urlpatterns += patterns('',
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'accounts/login.html'}),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),
    url(r'^accounts/password/change/$', 'django.contrib.auth.views.password_change', {'template_name': 'accounts/password_change_form.html'}, name='password_change'),
    (r'^accounts/password/change_done/$', 'django.contrib.auth.views.password_change_done', {'template_name': 'accounts/password_change_done.html'}),
    (r'^img/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),
    (r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),
)
