'''
Created on Jul 14, 2010

@author: jnaous
'''
from django import forms
from models import GENIAggregate
import logging
import traceback
from django.conf import settings
from sfa.trust.gid import GID
from sfa.trust.certificate import Keypair
from expedient_geni.utils import get_user_key_fname, get_user_cert_fname,\
    get_trusted_cert_filenames

logger = logging.getLogger("expedient_geni.forms")

def _clean_x_file_factory(name):
    """Factory to create functions that check file size"""
    def clean_x_file(self):
        logger.debug("Checking file lengths")
        if self.cleaned_data["%s_file" % name].size > \
        settings.GCF_MAX_UPLOADED_PEM_FILE_SIZE:
            raise forms.ValidationError(
                "File exceeds maximum file size of %s bytes."
                % settings.GCF_MAX_UPLOADED_PEM_FILE_SIZE)
        return self.cleaned_data["%s_file" % name]
    return clean_x_file

class UploadCertForm(forms.Form):
    """Form to upload a certificate and its corresponding key."""
    
    key_file = forms.FileField(
        help_text="Select the file that contains the key for the "\
            "certificate to upload.")
    cert_file = forms.FileField(
        help_text="Select the file that contains the "\
            "certificate to upload. The certificate must be signed "\
            "with the uploaded key.")
    
    clean_key_file = _clean_x_file_factory("key")
    clean_cert_file = _clean_x_file_factory("cert")
            
    def clean(self):
        """Check that the cert file is signed by the key file and is trusted."""
        logger.debug("cleaned_data %s" % self.cleaned_data)
        if self.files:
            self.key = Keypair(string=self.files["key_file"].read())
            self.cert = GID(string=self.files["cert_file"].read())
            
            cert_pubkey = self.cert.get_pubkey().get_pubkey_string()
            if cert_pubkey != self.key.get_pubkey_string():
                raise forms.ValidationError(
                    "Error: The certificate was not signed "
                    "by the uploaded key. Please use a key "
                    "that matches the certificate.")
    
            try:
                certs = [GID(filename=f) for f in get_trusted_cert_filenames()]
                self.cert.verify_chain(certs)
            except Exception as e:
                logger.error(traceback.format_exc())
                raise forms.ValidationError(
                    "Could not verify that the uploaded certificate is "
                    "trusted. This could be because none of the certificate's "
                    "ancestors have been installed as trusted. The error was: "
                    "%s" % e
                )

        return self.cleaned_data
    
    def save(self, user):
        """Write the key and cert into files.
        
        @param user: the user to save the cert and key for.
        @type user: C{django.contrib.auth.models.User}
        """
        
        key_fname = get_user_key_fname(user)
        cert_fname = get_user_cert_fname(user)
        
        self.key.save_to_file(key_fname)
        self.cert.save_to_file(cert_fname)
    
def geni_aggregate_form_factory(agg_model):
    class GENIAggregateForm(forms.ModelForm):
        class Meta:
            model = agg_model
            exclude = ['owner', 'users', 'leaf_name']
            
        def clean(self):
            """
            Check that the URL can be reached.
            """
            url = self.cleaned_data['url']
            agg = GENIAggregate(url=url)
            proxy = agg.get_expedient_client()
            
            # Check that the AM can be contacted
            logger.debug("Checking that GENI AM at %s can be reached." % url)
            try:
                v = proxy.GetVersion()
                ver = v["geni_api"]
                if ver != settings.CURRENT_GAPI_VERSION:
                    raise forms.ValidationError(
                        "Wrong GENI API version. Expected %s, but got %s." % (
                            settings.CURRENT_GAPI_VERSION, ver))
            except Exception as e:
                logger.error(traceback.format_exc())
                raise forms.ValidationError(
                    "Error getting version (GetVersion) information: %s" % e)
            
            # check that the credentials for ListResources work.
            logger.debug("Checking that ListResources works at %s." % url)
            try:
                proxy.ListResources(
                    [agg.get_am_cred()], 
                    {"geni_compressed": False, "geni_available": True})
            except Exception as e:
                traceback.print_exc()
                raise forms.ValidationError(
                    "Error getting resources (ListResources): %s" % e)
            
            return self.cleaned_data
            
    return GENIAggregateForm

