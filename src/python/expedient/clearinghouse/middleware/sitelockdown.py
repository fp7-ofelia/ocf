'''
@author jnaous
'''
from django.conf import settings
from django.http import HttpResponseRedirect

class SiteLockDown(object):
    """
    This middleware class will force every single request coming from
    Django to be authenticated, or it will redirect the user to a login
    page.
    
    Modified from: http://davyd.livejournal.com/262859.html
    """
    def process_request (self, request):
    
        try:
            request.django_root
        except AttributeError:
            request.django_root = ''

        login_url = settings.LOGIN_URL + '?next=%s' % request.path

        if request.path.startswith (request.django_root):
            path = request.path[len (request.django_root):]
        else:
            return HttpResponseRedirect (login_url)
        
        if not request.user.is_authenticated () and not \
        (request.path == settings.LOGIN_URL or
         path.startswith ('/accounts/register') or
         path.startswith ('/accounts/activate') or
         path.startswith ('/admin/') or
         path.startswith ('/accounts/password/reset') or
         path.startswith ('/img/') or
         path.startswith ('/css/') or
         path.endswith('/xmlrpc') or
         path.endswith('/xmlrpc/') or
         path.endswith('/gapi') or
         path.endswith('/gapi/')
         ):
            return HttpResponseRedirect (login_url)

        return None

