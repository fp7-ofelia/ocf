import uuid
import ldap
from django import forms
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from ofreg import util

class PasswordResetForm(forms.Form):
	email = forms.EmailField(max_length=255)
	challenge = forms.CharField(max_length=255)
	
	# resets the password and returns the login of the user which has been reset
	def reset_password(self, password_stub):
		email = self.cleaned_data['email']
		challenge = self.cleaned_data['challenge']
		password_full = password_stub + challenge
		try:
			protocol = '' # protocol for logging what is happing
			protocol += 'initialize & bind; '
			l = util.ldap_connection()
			protocol += 'find user by mail; '
			users = l.search_s(settings.LDAP_USERGP, ldap.SCOPE_SUBTREE, '(&(mail=%s))' % (email))
			if (len(users) <= 0):
				raise util.LdapException("No user with this email found")
			# reset only the first account
			cn = users[0][0]
			login = users[0][1]['uid'][0]
			protocol += 'change modify password'
			l.modify_s(users[0][0], [(ldap.MOD_REPLACE, 'userPassword', str(util.hash_password(password_full)))])
			# release binding
			protocol += 'release binding; '
			l.unbind_s()
			return login
		except ldap.LDAPError, e:
			raise util.LdapException("%s: %s" % (e, protocol))
	