from django.shortcuts import *
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.conf import settings

from ofreg.registration.models.password_reset import *
from ofreg import util

def forgotten(request):
	if request.method == 'POST':
		form = PasswordResetForm(request.POST)

		if form.is_valid():
			email = form.cleaned_data['email']
			password_stub = util.generate_random_password()
			try:
				login = form.reset_password(password_stub)
			except util.LdapException, e:
				return render_to_response('password_reset/forgotten.html', { 'message' : 'Error during LDAP processing (%s)' % e.message, 'form' : form })
			
			util.send_mail(
				email,
				'OFELIA Registration - Password has been reset',
				'password_reset_reset.txt',
				password=password_stub, login=login)
			return HttpResponseRedirect(reverse('registration.views.password_reset.reset'))
	else:
		form = PasswordResetForm()
	return render_to_response('password_reset/forgotten.html', { 'form' : form })

def reset(request):
	return render_to_response('password_reset/reset.html', { })