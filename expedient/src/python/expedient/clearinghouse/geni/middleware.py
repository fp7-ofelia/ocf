'''
Created on Oct 7, 2010

@author: jnaous
'''
from expedient.clearinghouse.geni.utils import get_or_create_user_cert

class CreateUserGID(object):
    """Middleware to create GIDs for users who login and do not have one."""
    def process_request(self, request):
        if request.user.is_authenticated():
            get_or_create_user_cert(request.user)

