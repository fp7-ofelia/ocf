'''
Created on Jun 11, 2010

@author: jnaous
'''
from django.views.generic import create_update
from models import DummyAggregate
from expedient.clearinghouse.aggregate.tests.forms import DummyAggForm

def create(request):
    return create_update.create_object(
        request,
        form_class=DummyAggForm,
        post_save_redirect="/",
        template_name="aggregate_tests/form.html",
    )

def edit(request, agg_id=None):
    return create_update.update_object(
        request,
        form_class=DummyAggForm,
        object_id=agg_id,
        post_save_redirect="/",
        template_name="aggregate_tests/form.html",
    )
