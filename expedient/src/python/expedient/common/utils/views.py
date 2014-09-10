'''
Created on Jun 18, 2010

@author: jnaous
'''
from django.shortcuts import get_object_or_404
from django.views.generic.create_update import get_model_and_form_class
from django.views.generic import simple
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from expedient.common.messaging.models import DatedMessage

def generic_crud(request, obj_id, model, template, redirect,
                 extra_context={}, form_class=None, extra_form_params={},
                 template_object_name="object", pre_save=None,
                 post_save=None, success_msg=None):
    """
    Generic way to create/update a bit more advanced than the django's generic
    views. The context will contain the form as C{form}, the object when
    updating as the value in C{template_object_name} which defaults to
    "object", and anything specified in C{extra_context}.
    
    @param request: The request object
    @param obj_id: The object's id to update or None if creating an object
    @param model: The model class
    @param template: the name of the template to use
    @param redirect: callable that takes the created/saved instance as argument
        and returns a URL to redirect to.
    @keyword extra_context: dict of fields to add to the template context.
    @keyword form_class: the form class to use for the object
        (ModelForm subclass)
    @keyword extra_form_params: dict of additional keyword parameters to pass
        to the form when init'ing the form instance.
    @keyword template_object_name: name of the object field in the template
        context. This is only available when updating.
    @keyword pre_save: function to call before saving the object instantiated
        from the form. Called with arguments (C{instance}, C{created}).
    @keyword post_save: function to call after saving the object instantiated
        from the form but before calling m2m_save() on it. Called with argument
        (C{instance}, C{created}).
    @keyword success_msg: callable that should take instance as parameter and
        return a string to be put in a success DatedMessage and sent to the
        user on success. 
    """
    
    model, form_class = get_model_and_form_class(model, form_class)

    if obj_id != None:
        instance = get_object_or_404(model, pk=obj_id)
    else:
        instance = None
    
    if request.method == "GET":
        form = form_class(instance=instance, **extra_form_params)
    elif request.method == "POST":
        form = form_class(request.POST, instance=instance, **extra_form_params)
        if form.is_valid():
            instance = form.save(commit=False)
            if pre_save:
                pre_save(instance, obj_id == None)
            instance.save()
            if post_save:
                post_save(instance, obj_id == None)
            form.save_m2m()
            # Send signal when generic object is ready
            from expedient.common.utils.signals import post_object_ready
            post_object_ready(instance)
            if success_msg:
                DatedMessage.objects.post_message_to_user(
                    success_msg(instance), request.user,
                    msg_type=DatedMessage.TYPE_SUCCESS)
            return HttpResponseRedirect(redirect(instance))
    else:
        return HttpResponseNotAllowed("GET", "POST")

    context = {"form": form}
    context.update(extra_context)
    if obj_id != None:
        context[template_object_name] = instance

    return simple.direct_to_template(
        request,
        template=template,
        extra_context=context,
        form=form,
    )
