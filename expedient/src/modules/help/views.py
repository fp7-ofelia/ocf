"""
Created on Jul 11, 2013

@author: CarolinaFernandez
"""

from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse

def home(request):
	"""
	Show simple template for help.

	@param request HTTP request
	@return string template for the help main page
	"""
	return direct_to_template(
		request,
		template="help/index.html",#"templates/index.html",
		extra_context = {
		"messages": "",
			"breadcrumbs": (
				("Home", reverse("home")),
				("Get help", ""),
			),
		}
	)
