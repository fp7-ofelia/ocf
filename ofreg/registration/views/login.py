from django.shortcuts import *
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from ofreg.registration.models.login import *

def login(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			request.session['login'] = form.cleaned_data['login']
			return HttpResponseRedirect(reverse('registration.views.login.success'))
	else:
		form = LoginForm()
	return render_to_response('login/login.html', { 'form' : form })


@require_login
def success(request):
	return render_to_response('login/success.html', { })