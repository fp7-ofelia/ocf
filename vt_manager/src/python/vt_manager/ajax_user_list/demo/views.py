from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.db.models import Q
from django.contrib.auth.models import User
import time

def index( request ):    
    template = 'index.html'
    data = {
    }
    return render_to_response( template, data, 
                               context_instance = RequestContext( request ) )

def ajax_user_search( request ):
    if request.is_ajax():
        q = request.GET.get( 'q' )
        if q is not None:            
            results = User.objects.filter( 
                Q( first_name__contains = q ) |
                Q( last_name__contains = q ) |
                Q( username__contains = q ) ).order_by( 'username' )
            
            template = 'results.html'
            data = {
                'results': results,
            }
            return render_to_response( template, data, 
                                       context_instance = RequestContext( request ) )