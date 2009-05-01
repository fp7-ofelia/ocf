from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^clearinghouse/', include('egeni.clearinghouse.urls')),
    (r'^admin/(.*)', admin.site.root),
)
