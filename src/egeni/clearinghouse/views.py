from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponseBadRequest,\
    HttpRequest, HttpResponseForbidden, Http404
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed, HttpResponseForbidden
from django.core.urlresolvers import reverse
from egeni.clearinghouse.models import *
from django.db.models import Q

REL_PATH = "."

def home(request):
    '''Show the Clearinghouse dashboard'''
    
    context = {'aggmgr_count': AggregateManager.objects.count(),
               'node_count': Node.objects.count(),
               'link_count': Link.objects.count(),
               'slice_count': Slice.objects.count(),
               'user_count': User.objects.count(),
               'active_slice_count': Slice.objects.filter(owner=request.user, committed=True).count(),
               'inactive_slice_count': Slice.objects.filter(owner=request.user, committed=False).count(),
               'reserved_host_count': NodeSliceStatus.objects.filter(node__type=Node.TYPE_PL,
                                                                     reserved=True,
                                                                     slice__owner=request.user,
                                                                     ).count(),
               'reserved_switch_count': NodeSliceStatus.objects.filter(node__type=Node.TYPE_OF,
                                                                       reserved=True,
                                                                       slice__owner=request.user,
                                                                       ).count(),
               }
    
    context['announcements'] = DatedMessage.objects.filter(type=DatedMessage.TYPE_ANNOUNCE)
    context['errors'] = DatedMessage.objects.filter(Q(type=DatedMessage.TYPE_ERROR)
                                                    | Q(type=DatedMessage.TYPE_WARNING))
    
    context['show_admin'] = request.user.is_staff
    context['show_user']  = not context['show_admin']
    
    return render_to_response("clearinghouse/home.html", context)

def get_img(request, img_name):
    print "Reading image %s" % img_name
    if "/" in img_name:
        return HttpResponseForbidden()
    
    try:
        print "<1>"
        image_data = open("%s/img/%s" % (REL_PATH, img_name), "rb").read()
        print "<2>"
        bla, extension = img_name.split(".")
        print "<3>"
        return HttpResponse(image_data, mimetype="image/%s" % extension)
    except Exception, e:
        print e
        return Http404()
