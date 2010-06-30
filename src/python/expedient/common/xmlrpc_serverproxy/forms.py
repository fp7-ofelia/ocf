'''
Created on Apr 29, 2010

@author: jnaous
'''

from django import forms
from models import PasswordXMLRPCServerProxy

import logging
logger = logging.getLogger("PasswordXMLRPCServerProxyForm") 

class PasswordXMLRPCServerProxyFormHelperAddin(object):
    def clean_url(self):
        '''Check url'''
        import urlparse
        url = self.cleaned_data['url']
        logger.debug("Checking URL %s" % url)
        parsed = urlparse.urlparse(url, "https", False)
        if parsed.port == None:
            raise forms.ValidationError("Did not specify a port. Please \
explicitly specify the port. e.g. https://hostname:portnum/xmlrpc/xmlrpc/") 
        if parsed.port == 0:
            raise forms.ValidationError("Invalid port number 0.") 
        u = parsed.geturl()
        logger.debug("parsed url: %s" % u)
        if not u.endswith("/"): u += "/"
        return u

    def clean(self):
        logger.debug("Cleaning data")
        if self._errors:
            return self.cleaned_data
        d = dict(self.cleaned_data)
        if "password2" in d: del d["password2"]
        p = self._meta.model(**d)
        avail, msg = p.is_available(get_info=True)
        if not avail:
            url = self.cleaned_data.get("url", "None")
            logger.debug("URL not available.")
            raise forms.ValidationError(
                "The url %s could not be reached. Check the url, username, "
                "and password. The error message was: %s." % (
                url, msg))
        logger.debug("Done cleaning data")
        return self.cleaned_data

class PasswordXMLRPCServerProxyForm(forms.ModelForm,
                                    PasswordXMLRPCServerProxyFormHelperAddin):
    '''
    A form that can be used to create/edit info on a PasswordXMLRPCClient
    If C{check_available} is True, the form will check that a saved client
    can access the location.
    '''
    
    def __init__(self, check_available=False, *args, **kwargs):
        super(PasswordXMLRPCServerProxyForm, self).__init__(*args, **kwargs)
        self.check_available = check_available
    
    class Meta:
        model = PasswordXMLRPCServerProxy

    def clean(self):
        return PasswordXMLRPCServerProxyFormHelperAddin.clean(self)
    