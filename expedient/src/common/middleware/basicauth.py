'''
Created on Jun 15, 2010

Based on code from http://djangosnippets.org/snippets/56/

@author: jnaous
'''

from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.models import Site
from django.http import HttpResponse
from django.conf import settings
import re
from expedient.common.middleware.utils import RegexMatcher

def basic_challenge(realm = None):
    if realm is None:
        try:
            realm = Site.objects.get_current().name
        except:
            realm = "Secured Area"
    response = HttpResponse('Authorization Required', mimetype="text/plain")
    response['WWW-Authenticate'] = 'Basic realm="%s"' % (realm)
    response.status_code = 401
    return response

def basic_authenticate(authentication):
    # Taken from paste.auth
    (authmeth, auth) = authentication.split(' ',1)
    if 'basic' != authmeth.lower():
        return None
    auth = auth.strip().decode('base64')
    username, password = auth.split(':',1)
    return authenticate(username = username, password = password)

class HTTPBasicAuthMiddleware(RegexMatcher):
    """
    Middleware that logs in users using HTTP Basic Authnetication. 
    The list of protected paths is specified as regular expressions in the
    C{settings.BASIC_AUTH_URLS} tuple. All URLs there will require basic
    HTTP authentication.
    
    The middleware checks if the request has the HTTP_AUTHORIZATION header
    and that there is no "REMOTE_USER" already set in the request by
    an external web server. It then authenticates the user
    and logs her in or redirects to an "Authorization Required" page.
    """
    def __init__(self):
        super(HTTPBasicAuthMiddleware, self).__init__("BASIC_AUTH_URLS")

    def process_request(self, request):
        # Make sure there was no other authentication
        if request.META.has_key("REMOTE_USER"):
            return None
        # check for a match
        if self.matches(request.path):
            if not request.META.has_key('HTTP_AUTHORIZATION'):
                logout(request)
                return basic_challenge()
            user = basic_authenticate(request.META['HTTP_AUTHORIZATION'])
            if user is None:
                return basic_challenge()
            else:
                login(request, user)
                
