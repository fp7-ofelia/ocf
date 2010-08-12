'''
@author: jnaous
'''
from django.core.urlresolvers import reverse
from expedient.common.utils.views import generic_crud
import logging
from forms import geni_aggregate_form_factory
from expedient.common.permissions.shortcuts import give_permission_to

logger = logging.getLogger("GENIViews")
TEMPLATE_PATH = "geni"

def aggregate_create(request, agg_model):
    '''
    Create a GENI Aggregate.
    
    @param request: The request.
    @param model: The child subclass for the aggregate.
    '''
    
    def pre_save(instance, created):
        instance.owner = request.user
    
    def post_save(instance, created):
        instance.update_resources()
        give_permission_to(
            "can_use_aggregate",
            instance,
            request.user,
            can_delegate=True
        )
        give_permission_to(
            "can_edit_aggregate",
            instance,
            request.user,
            can_delegate=True
        )
    
    def success_msg(instance):
        return "Successfully created aggregate %s." % instance.name
    
    return generic_crud(
        request, obj_id=None, model=agg_model,
        template=TEMPLATE_PATH+"/aggregate_crud.html",
        redirect=lambda instance:reverse("home"),
        form_class=geni_aggregate_form_factory(agg_model),
        pre_save=pre_save,
        post_save=post_save,
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

    