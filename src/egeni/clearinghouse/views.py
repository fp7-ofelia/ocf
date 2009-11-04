from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponseBadRequest,\
    HttpRequest, HttpResponseForbidden
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed, HttpResponseForbidden
from django.core.urlresolvers import reverse
from egeni.clearinghouse.models import *
from django.db.models import Q

def home(request):
    '''Show the Clearinghouse dashboard'''
    
    context = {'aggmgr_count': AggregateManager.objects.count(),
               'node_count': Node.objects.count(),
               'link_count': Link.objects.count(),
               'slice_count': Slice.objects.count(),
               'user_count': User.objects.count(),
               }
    
    context['announcements'] = DatedMessage.objects.filter(type=DatedMessage.TYPE_ANNOUNCE)
    context['errors'] = DatedMessage.objects.filter(Q(type=DatedMessage.TYPE_ERROR)
                                                    | Q(type=DatedMessage.TYPE_WARNING))
    
    context['show_admin'] = request.user.is_staff
    context['show_user']  = not context['show_admin']
    
    return render_to_response("clearinghouse/home.html", context)

