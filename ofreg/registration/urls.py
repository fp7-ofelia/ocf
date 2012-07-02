from django.conf.urls.defaults import *
from ofreg import util

urlpatterns = patterns('',
	(r'^$', 'django.views.generic.simple.redirect_to', { 'url' : '/welcome'}),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root' : util.project_path('registration/static/') }),

	# --- welcome views
	(r'^welcome$', 'registration.views.welcome.index'),

	# --- login views
	(r'^login/login$', 'registration.views.login.login'),
	(r'^login/success$', 'registration.views.login.success'),

	# --- registration views
	(r'^registration/register$', 'registration.views.registration.register'),
	(r'^registration/register_success$', 'registration.views.registration.register_success'),
	(r'^registration/validate/(.*)$', 'registration.views.registration.validate'),
	
	# --- password forgotten
	(r'^password_reset/forgotten$', 'registration.views.password_reset.forgotten'),
	(r'^password_reset/reset$', 'registration.views.password_reset.reset'),
)
