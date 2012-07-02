import ldap
from django import forms
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.exceptions import ValidationError
from ofreg import util

def require_login(view):
	def new_view(request):
		if not 'login' in request.session:
			return HttpResponseRedirect(reverse('registration.views.login.login'))
		return view(request)
	return new_view

class LoginForm(forms.Form):
	login = forms.CharField()
	password = forms.CharField(widget=forms.PasswordInput)
	
	def clean_password(self):
		if not self.authenticate():
			raise ValidationError('No user found with that password.')
		
	def authenticate(self):
		l = util.ldap_connection()
		user = l.search_s(settings.LDAP_USERGP, ldap.SCOPE_SUBTREE, '(&(cn=%s)(userPassword=%s))' % (self.cleaned_data['login'], util.hash_password(self.cleaned_data['password'])))
		l.unbind_s()
		if user and (len(user) > 0):
			return True
		else:
			return False