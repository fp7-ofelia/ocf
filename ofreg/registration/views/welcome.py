from django.shortcuts import *
from django.http import HttpResponse
from django.core.urlresolvers import reverse

def index(request):
	return HttpResponseRedirect(reverse('registration.views.login.login'))
	# return render_to_response('welcome/index.html')