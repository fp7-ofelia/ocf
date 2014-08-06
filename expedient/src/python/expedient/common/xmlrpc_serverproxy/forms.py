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
        if not u.endswith("/"):
            u += "/"
        return u

    # Validation and so on
    def clean(self):
        logger.debug("Cleaning data")
        if self._errors:
            return self.cleaned_data
        # Check that both passwords (if present) are the same
        password = self.cleaned_data.get('password', None)
        confirm_password = self.cleaned_data.get('confirm_password', None)
        if password and confirm_password and (password != confirm_password):
            raise forms.ValidationError("Passwords don't match")
        # Remove fields that are not in the Model to avoid any mismatch when synchronizing
        d = dict(self.cleaned_data)
        if "password2" in d:
            del d["password2"]
        if "confirm_password" in d:
            del d["confirm_password"]
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
    
    confirm_password = forms.CharField(
        help_text="Confirm password.",
        max_length=40,
        widget=forms.PasswordInput(render_value=False))

    def __init__(self, check_available=False, *args, **kwargs):
        super(PasswordXMLRPCServerProxyForm, self).__init__(*args, **kwargs)
        self.check_available = check_available
        # Fix Django's autocompletion of username/password fields when type is password
        self.fields['username'].widget.attrs["autocomplete"] = 'off'
        self.fields['password'].widget.attrs["autocomplete"] = 'off'
        self.fields['confirm_password'].widget.attrs["autocomplete"] = 'off'

    class Meta:
        model = PasswordXMLRPCServerProxy
        # Defines all the fields in the model by ORDER
        fields = ('username','password','confirm_password','max_password_age','url','verify_certs')
        # Form widgets: HTML representation of fields
        widgets = {
            # Show the password
            'password': forms.PasswordInput(render_value=True),
        }

    def clean(self):
        return PasswordXMLRPCServerProxyFormHelperAddin.clean(self)
