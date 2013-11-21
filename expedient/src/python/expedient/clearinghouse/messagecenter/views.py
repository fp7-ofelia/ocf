'''
@author: msune 
'''

from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse

'''
Shows all the messages in a simple way
'''

def home(request):
	return direct_to_template(
        	request,
	        template='expedient/clearinghouse/messagecenter/index.html',
        	extra_context={
		    "messages": "",
	            "breadcrumbs": (
        	        ("Home", reverse("home")),
                	("Last messages of %s" % request.user.username,""),
	            ),
	        }
	    )
    
