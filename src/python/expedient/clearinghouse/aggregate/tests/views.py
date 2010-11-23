'''
Created on Jun 11, 2010

@author: jnaous
'''
from django.views.generic import create_update
from models import DummyAggregate
from expedient.clearinghouse.aggregate.tests.forms import DummyAggForm
from expedient.common.utils.views import generic_crud

def create(request):

    def pre_save(instance, created):
        instance.owner = request.user
        
    return generic_crud(
        request,
        obj_id=None,
        model=DummyAggregate,
        form_class=DummyAggForm,
        pre_save=pre_save,
        redirect=lambda(instance): "/",
        template="aggregate_tests/form.html",
    )

def edit(request, agg_id=None):
    return create_update.update_object(
        request,
        form_class=DummyAggForm,
        object_id=agg_id,
        post_save_redirect="/",
        template_name="aggregate_tests/form.html",
    )
