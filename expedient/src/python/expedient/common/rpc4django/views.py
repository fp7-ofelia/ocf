'''
Views

This module contains the method serve_rpc_request which is intended to
be called from the urls.py module of a 
`django <http://www.djangoproject.com/>`_ project.

It should be called like this from urls.py:

    rpc_url(r'^RPC2$', name="my_url_name"),

'''

import logging
from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.conf import settings
import types
from rpcdispatcher import RPCDispatcher
from __init__ import version

# these restrictions can change the functionality of rpc4django
# but they are completely optional
# see the rpc4django documentation for more details
LOG_REQUESTS_RESPONSES = getattr(settings,
                                 'RPC4DJANGO_LOG_REQUESTS_RESPONSES', True)
RESTRICT_INTROSPECTION = getattr(settings,
                                 'RPC4DJANGO_RESTRICT_INTROSPECTION', False)
RESTRICT_JSON = getattr(settings, 'RPC4DJANGO_RESTRICT_JSONRPC', False)
RESTRICT_XML = getattr(settings, 'RPC4DJANGO_RESTRICT_XMLRPC', False)
RESTRICT_METHOD_SUMMARY = getattr(settings, 
                                  'RPC4DJANGO_RESTRICT_METHOD_SUMMARY', False)
RESTRICT_RPCTEST = getattr(settings, 'RPC4DJANGO_RESTRICT_RPCTEST', False)
RESTRICT_RPCTEST = getattr(settings, 'RPC4DJANGO_RESTRICT_RPCTEST', False)
HTTP_ACCESS_CREDENTIALS = getattr(settings, 
                                  'RPC4DJANGO_HTTP_ACCESS_CREDENTIALS', False)
HTTP_ACCESS_ALLOW_ORIGIN = getattr(settings, 
                                  'RPC4DJANGO_HTTP_ACCESS_ALLOW_ORIGIN', '')

# get a list of the installed django applications
# these will be scanned for @rpcmethod decorators
APPS = getattr(settings, 'INSTALLED_APPS', [])

logger = logging.getLogger("rpc4django.views")

class NonExistingDispatcher(Exception):
    """Raised when the dispatcher for a particular name is not found."""
    def __init__(self, path, url_name):
        super(NonExistingDispatcher, self).__init__(
            "URL name '%s' is not used in any rpcmethod,\
 however, the URL '%s' uses it." % (url_name, path))
        self.path = path
        self.url_name = url_name

def get_dispatcher(path, url_name):
    try:
        dispatcher = dispatchers[url_name]
    except KeyError:
        raise NonExistingDispatcher(path, url_name)
    return dispatcher

def _check_request_permission(request, request_format='xml', url_name="root"):
    '''
    Checks whether this user has permission to perform the specified action
    This method does not check method call validity. That is done later
    
    PARAMETERS
    
    - ``request`` - a django HttpRequest object
    - ``request_format`` - the request type: 'json' or 'xml' 
    
    RETURNS 
    
    True if the request is valid and False if permission is denied
    '''
    
    user = getattr(request, 'user', None)
    dispatcher = get_dispatcher(request.path, url_name)
    methods = dispatcher.list_methods()
    method_name = dispatcher.get_method_name(request.raw_post_data, \
                                             request_format)
    response = True
    
    for method in methods:
        if method.name == method_name:
            # this is the method the user is calling
            # time to check the permissions
            if method.permission is not None:
                logger.debug('Method "%s" is protected by permission "%s"' \
                              %(method.name, method.permission))
                if user is None:
                    # user is only none if not using AuthenticationMiddleware
                    logger.warn('AuthenticationMiddleware is not enabled')
                    response = False
                elif not user.has_perm(method.permission):
                    # check the permission against the permission database
                    logger.info('User "%s" is NOT authorized' %(str(user)))
                    response = False
                else:
                    logger.debug('User "%s" is authorized' %(str(user)))
            else:
                logger.debug('Method "%s" is unprotected' %(method.name))
                
            break
    
    return response
    
def _is_xmlrpc_request(request):
    '''
    Determines whether this request should be served by XMLRPC or JSONRPC
    
    Returns true if this is an XML request and false for JSON
    
    It is based on the following rules:
    
    # If there is no post data, display documentation
    # content-type = text/xml or application/xml => XMLRPC
    # content-type contains json or javascript => JSONRPC
    # Try to parse as xml. Successful parse => XMLRPC
    # JSONRPC
    '''
    
    conttype = request.META.get('CONTENT_TYPE', 'unknown type')
    
    # check content type for obvious clues
    if conttype == 'text/xml' or conttype == 'application/xml':
        return True
    elif conttype.find('json') >= 0 or conttype.find('javascript') >= 0:
        return False
    
    if LOG_REQUESTS_RESPONSES:
        logger.info('Unrecognized content-type "%s"' %conttype)
        logger.info('Analyzing rpc request data to get content type')
    
    # analyze post data to see whether it is xml or json
    # this is slower than if the content-type was set properly
    try:
        parseString(request.raw_post_data)
        return True
    except ExpatError:
        pass
    
    return False

def serve_rpc_request(request, url_name="root", **kwargs):
    '''
    This method handles rpc calls based on the content type of the request
    '''
    
    dispatcher = get_dispatcher(request.path, url_name)
    
    if request.method == "POST" and len(request.POST) > 0:
        # Handle POST request with RPC payload
        
        if LOG_REQUESTS_RESPONSES:
            logger.debug('Incoming request: %s' % str(request.raw_post_data))
            
        if _is_xmlrpc_request(request):
            if RESTRICT_XML:
                raise Http404
            
            if not _check_request_permission(request, 'xml', url_name=url_name):
                return HttpResponseForbidden()
            
            resp = dispatcher.xmldispatch(request.raw_post_data,
                                          request=request, **kwargs)
            response_type = 'text/xml'
        else:
            if RESTRICT_JSON:
                raise Http404
            
            if not _check_request_permission(request, 'json',url_name=url_name):
                return HttpResponseForbidden()
            
            resp = dispatcher.jsondispatch(request.raw_post_data,
                                           request=request)
            response_type = 'application/json'
            
        if LOG_REQUESTS_RESPONSES:
            logger.debug('Outgoing %s response: %s' %(response_type, resp))
        
        return HttpResponse(resp, response_type)
    elif request.method == 'OPTIONS':
        # Handle OPTIONS request for "preflighted" requests
        # see https://developer.mozilla.org/en/HTTP_access_control
        
        response = HttpResponse('', 'text/plain')
        
        origin = request.META.get('HTTP_ORIGIN', 'unknown origin')
        response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
        response['Access-Control-Max-Age'] = 0
        response['Access-Control-Allow-Credentials'] = \
                        str(HTTP_ACCESS_CREDENTIALS).lower()
        response['Access-Control-Allow-Origin']= HTTP_ACCESS_ALLOW_ORIGIN
        
        response['Access-Control-Allow-Headers'] = \
                    request.META.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS', '')
                    
        if LOG_REQUESTS_RESPONSES:
            logger.debug('Outgoing HTTP access response to: %s' %(origin))
                    
        return response
    else:
        # Handle GET request
        
        if RESTRICT_METHOD_SUMMARY:
            # hide the documentation by raising 404
            raise Http404
        
        # show documentation
        methods = dispatcher.list_methods()
        template_data = {
            'methods': methods,
            'url': request.path,
            
            # rpc4django version
            'version': version(),
            
            # restricts the ability to test the rpc server from the docs
            'restrict_rpctest': RESTRICT_RPCTEST,
        }
        return render_to_response('rpc4django/rpcmethod_summary.html', \
                                  template_data)

# exclude from the CSRF framework because RPC is intended to be used cross site
try:
    # Django 1.2
    from django.views.decorators.csrf import csrf_exempt
except ImportError:
    try:
        # Django 1.1
        from django.contrib.csrf.middleware import csrf_exempt
    except ImportError:
        # Django 1.0
        csrf_exempt = None

if csrf_exempt is not None:
    serve_rpc_request = csrf_exempt(serve_rpc_request)

def _register_rpcmethods(apps, restrict_introspection=False, dispatchers={}):
    '''
    Scans the installed apps for methods with the rpcmethod decorator
    Adds these methods to the list of methods callable via RPC
    '''
    
    for appname in apps:
        # check each app for any rpcmethods
        app = __import__(appname, globals(), locals(), ['*'])
        for obj in dir(app):
            method = getattr(app, obj)
            if callable(method) and \
               getattr(method, 'is_rpcmethod', False) == True:
                # if this method is callable and it has the rpcmethod
                # decorator, add it to the dispatcher
                if method.url_name not in dispatchers:
                    #logger.debug("Registered URL name '%s'" % method.url_name)
                    dispatchers[method.url_name] = RPCDispatcher(
                        method.url_name, restrict_introspection)
                #logger.debug(
                #    "Registered method '%s' to URL name '%s'"
                #    % (method.external_name, method.url_name))
                dispatchers[method.url_name].register_method(
                    method, method.external_name)
            elif isinstance(method, types.ModuleType):
                # if this is not a method and instead a sub-module,
                # scan the module for methods with @rpcmethod
                try:
                    _register_rpcmethods(
                        ["%s.%s" % (appname, obj)], 
                        restrict_introspection, dispatchers)
                except ImportError:
                    pass
    return dispatchers

dispatchers = _register_rpcmethods(APPS, RESTRICT_INTROSPECTION)

