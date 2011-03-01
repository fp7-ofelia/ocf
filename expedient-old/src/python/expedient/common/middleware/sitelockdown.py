'''
@author: jnaous
'''
from django.conf import settings
from django.http import HttpResponseRedirect
from utils import RegexMatcher

import logging
logger = logging.getLogger("sitelockdown")

class SiteLockDown(RegexMatcher):
    """
    This middleware class will force almost every request coming from
    Django to be authenticated, or it will redirect the user to a login
    page. Some urls can be excluded by specifying their regexes in the
    C{SITE_LOCKDOWN_EXCEPTIONS} tuple in the settings.
    
    Hints from: http://davyd.livejournal.com/262859.html
    """
    def __init__(self):
        super(SiteLockDown, self).__init__("SITE_LOCKDOWN_EXCEPTIONS")
        
    def process_request (self, request):
        try:
            request.django_root
        except AttributeError:
            request.django_root = ''

        login_url = settings.LOGIN_URL + '?next=%s' % request.path

        if request.path.startswith(request.django_root):
            path = request.path[len(request.django_root):]
        else:
            return HttpResponseRedirect (login_url)
        
        if not request.user.is_authenticated () and not \
        (path == settings.LOGIN_URL or
         self.matches(path)
         ):
            logger.debug("Redirecting locked down site %s to login." % path)
            return HttpResponseRedirect (login_url)

        return None
