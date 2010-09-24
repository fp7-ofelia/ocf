'''
Created on Jul 14, 2010

@author: jnaous
'''
from django import forms
from models import GENIAggregate
import logging
import traceback
from django.conf import settings

logger = logging.getLogger("GENIForms")


def geni_aggregate_form_factory(agg_model):
    class GENIAggregateForm(forms.ModelForm):
        class Meta:
            model = agg_model
            exclude = ['owner', 'users']
            
        def clean(self):
            """
            Check that the URL can be reached.
            """
            url = self.cleaned_data['url']
            agg = GENIAggregate(url=url)
            
            # Check that the AM can be contacted
            logger.debug("Checking that GENI AM at %s can be reached." % url)
            try:
                v = agg.proxy.GetVersion()
                ver = v["geni_api"]
                if ver != settings.CURRENT_GAPI_VERSION:
                    raise forms.ValidationError(
                        "Wrong GENI API version. Expected %s, but got %s." % (
                            settings.CURRENT_GAPI_VERSION, ver))
            except Exception as e:
                traceback.print_exc()
                raise forms.ValidationError(
                    "Error getting version (GetVersion) information: %s" % e)
            
            # check that the credentials for ListResources work.
            logger.debug("Checking that ListResources works at %s." % url)
            try:
                agg.proxy.ListResources(
                    [agg.get_am_cred()], 
                    {"geni_compressed": False, "geni_available": True})
            except Exception as e:
                traceback.print_exc()
                raise forms.ValidationError(
                    "Error getting resources (ListResources): %s" % e)
            
            return self.cleaned_data
            
    return GENIAggregateForm

