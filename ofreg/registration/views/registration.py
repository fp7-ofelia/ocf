from django.shortcuts import *
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.conf import settings

from ofreg.registration.models.registration import *
from ofreg import util

def register(request):
	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		form.recaptcha_remote_ip = request.META['REMOTE_ADDR']
		
		if form.is_valid():
			form.save()
			util.send_mail(
				form.instance.email,
				'OFELIA Registration - Please validate your email address',
				'registration_validation.txt',
				link=settings.SERVER_BASE + reverse('registration.views.registration.validate', args=(form.instance.validation_hash,)))
			return HttpResponseRedirect(reverse('registration.views.registration.register_success'))
	else:
		form = RegistrationForm()
	return render_to_response('registration/register.html', { 'form' : form })

def register_success(request):
	return render_to_response('registration/register_success.html', { })

def validate(request, validation_hash):
	try:
		registration = Registration.objects.get(validation_hash=validation_hash)
	except Registration.DoesNotExist:
		return render_to_response('registration/validate_error.html', { 'message' : 'The validation key you provided, has not been valid. Did you validate before?'})
		
	try:
		# save to LDAP
		registration.transfer_to_ldap()
		# send mail
		util.send_mail(
			registration.email,
			'OFELIA Registration - Registration complete',
			'registration_complete.txt',
			link=settings.SERVER_BASE + reverse('registration.views.login.login'),
			login=registration.safe_name)
	except Registration.LdapException, e:
		return render_to_response('registration/validate_error.html', { 'message' : 'Error during LDAP processing (%s)' % e.message})
		
	return render_to_response('registration/validate_success.html', { })
