'''
@author: jnaous
'''
from django.views.generic import date_based, create_update
from expedient.common.utils.views import generic_crud
from models import DatedMessage
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from forms import MessageForm, MessageFormNoIM

from django.forms.models import ModelFormMetaclass, ModelForm
from django.template import RequestContext, loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.xheaders import populate_xheaders
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.utils.translation import ugettext
from django.contrib.auth.views import redirect_to_login
from django.views.generic import GenericViewError
from django.contrib import messages
from django.contrib.auth.models import User
from expedient.common.utils.mail import send_mail # Wrapper for django.core.mail__send_mail
from django.conf import settings

def list_msgs(request, number=None):
    '''
    Get a list of messages organized by date.
    '''
    
    if request.method == "GET":
        qs = DatedMessage.objects.get_messages_for_user(request.user)
        
        if number == None:
			number = qs.count()
            
        return date_based.archive_index(
            request,
            queryset=qs,
            date_field='datetime',
            num_latest=number,
            template_name='expedient/common/messaging/list.html',
            extra_context={'requested': number}
        )
        
    elif request.method == "POST":
        msg_ids = request.POST.getlist("selected")
        qs = DatedMessage.objects.filter(id__in=msg_ids)
        DatedMessage.objects.delete_messages_for_user(qs, request.user)
        
        if number:
            return HttpResponseRedirect(
                reverse("messaging_subset", kwargs={"number": number}))
        else:
            return HttpResponseRedirect(
                reverse("messaging_all"))

    return HttpResponseNotAllowed("GET", "POST")

def create(request):
    '''
    Create a new message
    '''
    if request.user.is_superuser:
        message_class = MessageForm
    else:
        message_class = MessageFormNoIM
    
    # Original
#    return create_message(
#        request,
#        form_class=message_class,
#        template_name="expedient/common/messaging/create.html",
#        post_save_redirect=reverse("messaging_created"),
#    )
    
    return generic_crud(
        request, None, None,"expedient/common/messaging/create.html",
        redirect=lambda instance:reverse("messaging_center"),
        form_class=message_class,
        success_msg = lambda instance: "Successfully sent message.",
    )

def create_message(request, model=None, template_name=None,
        template_loader=loader, extra_context=None, post_save_redirect=None,
        login_required=False, context_processors=None, form_class=None):
    
    if extra_context is None: extra_context = {}
    if login_required and not request.user.is_authenticated():
        return redirect_to_login(request.path)

    model, form_class = create_update.get_model_and_form_class(model, form_class)
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            new_object = form.save()

            msg = ugettext("The %(verbose_name)s was created successfully.") %\
                                    {"verbose_name": model._meta.verbose_name}
            messages.success(request, msg, fail_silently=True)
            new_object.sender = request.user
            new_object.save()
            if new_object.type == DatedMessage.TYPE_U2U:
                try:
                    send_mail(
                             settings.EMAIL_SUBJECT_PREFIX + "User %s has sent you a message" % (new_object.sender),
                             "Original Message:\n\"%s\"\n\n\nYou can check the new message at https://%s/messagecenter/\n\n" % (new_object.msg_text, settings.SITE_DOMAIN),
                             from_email=settings.DEFAULT_FROM_EMAIL,
                             recipient_list= User.objects.filter(id__in = request.POST.getlist('users')).values_list('email', flat=True),
                             #recipient_list=[settings.ROOT_EMAIL],
                     )
                except Exception as e:
                    print "[WARNING] User e-mail notification could not be sent. Details: %s" % str(e)

            return create_update.redirect(post_save_redirect, new_object)
    else:
        form = form_class()

    # Create the template, context, response
    if not template_name:
        template_name = "%s/%s_form.html" % (model._meta.app_label, model._meta.object_name.lower())
    t = template_loader.get_template(template_name)
    c = RequestContext(request, {
        'form': form,
    }, context_processors)
    create_update.apply_extra_context(extra_context, c)
    return HttpResponse(t.render(c))
    
#    DatedMessage.objects.post_message_to_user(
#    "%s" % str(c),
#    request.user, msg_type=DatedMessage.TYPE_SUCCESS)
#    return HttpResponseRedirect(reverse('messaging_latest'))

