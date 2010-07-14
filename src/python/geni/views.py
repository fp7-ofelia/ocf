'''
@author: jnaous
'''
from django.core.urlresolvers import reverse
from expedient.common.utils.views import generic_crud
from models import GENIAggregate
from django import forms
from django.conf import settings
import logging
import traceback

logger = logging.getLogger("GENIViews")
TEMPLATE_PATH = "geni"

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

def aggregate_create(request, agg_model):
    '''
    Create a GENI Aggregate.
    
    @param request: The request.
    @param model: The child subclass for the aggregate.
    '''
    
    def pre_save(instance, created):
        instance.owner = request.user
    
    def success_msg(instance):
        return "Successfully created aggregate %s." % instance.name
    
    return generic_crud(
        request, obj_id=None, model=agg_model,
        template=TEMPLATE_PATH+"/aggregate_crud.html",
        redirect=lambda instance:reverse("home"),
        form_class=geni_aggregate_form_factory(agg_model),
        pre_save=pre_save,
        extra_context={
            "create": True,
            "name": agg_model._meta.verbose_name,
        },
        success_msg=success_msg)
    
def aggregate_edit(request, agg_id, agg_model):
    """
    Update a GENI Aggregate.
    
    @param request: The request object
    @param agg_id: the aggregate id
    @param agg_model: the GENI Aggregate subclass.
    """
    
    def success_msg(instance):
        return "Successfully updated aggregate %s." % instance.name
    
    return generic_crud(
        request, obj_id=agg_id, model=agg_model,
        template=TEMPLATE_PATH+"/aggregate_crud.html",
        template_object_name="aggregate",
        redirect=lambda instance:reverse("home"),
        form_class=geni_aggregate_form_factory(agg_model),
        success_msg=success_msg)
