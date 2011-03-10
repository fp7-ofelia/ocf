from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib.auth.views import login, logout_then_login
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    ( r'^admin/(.*)', admin.site.root ),
    ( r'^site_media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT } ),
    ( r'^demo/', include( 'demo.urls' ) ),
)