'''
Created on Apr 29, 2010

@author: jnaous
'''

from django import forms
from models import PasswordXMLRPCServerProxy

class PasswordXMLRPCServerProxyForm(forms.ModelForm):
    '''
    A form that can be used to create/edit info on a PasswordXMLRPCClient
    '''
    class Meta:
        model = PasswordXMLRPCServerProxy

    def clean_url(self):
        '''Check url'''
        import urlparse
        url = self.cleaned_data['url']
        parsed = urlparse.urlparse(url, "https", False)
#        if parsed.scheme.lower() != "https":
#            raise forms.ValidationError("Server URL must be contacted using HTTPS")
        u = parsed.geturl()
        if not u.endswith("/"): u += "/"
        return u
