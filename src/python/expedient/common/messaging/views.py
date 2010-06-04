'''
@author: jnaous
'''
from django.views.generic import date_based, create_update
from models import DatedMessage
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from forms import MessageForm

def list_msgs(request, number=None):
    '''
    Get a list of messages organized by date.
    '''
    
    if request.method == "GET":
        qs = DatedMessage.objects.get_messages_for_user(request.user)
        
        if number == None: number = qs.count()
            
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
    
    return create_update.create_object(
        request,
        form_class=MessageForm,
        template_name="expedient/common/messaging/create.html",
        post_save_redirect=reverse("messaging_created"),
    )
